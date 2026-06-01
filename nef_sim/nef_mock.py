#!/usr/bin/env python3
"""
Mock NEF — Nnef_EventExposure (TS 29.591)
Supports: PERF_DATA, UE_MOBILITY, UE_COMM
Optional live mode: scapy sniff on CAPTURE_IFACE, emit UE_COMM from real flows.
"""
import asyncio
import logging
import os
import random
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock NEF — Nnef_EventExposure")

# ── Config ────────────────────────────────────────────────────────────────────

CAPTURE_IFACE = os.getenv("CAPTURE_IFACE", "")
CAPTURE_BPF = os.getenv("CAPTURE_BPF", "ip")  # BPF filter for scapy sniff
CAPTURE_WINDOW = float(os.getenv("CAPTURE_WINDOW", "5"))
FLOW_IDLE_SECONDS = float(os.getenv("FLOW_IDLE_SECONDS", "30"))
IGNORE_SRCS = set(filter(None, os.getenv("IGNORE_SRCS", "").split(",")))

# ── Subscription store ────────────────────────────────────────────────────────

subscriptions: dict[str, dict] = {}  # subId → {notifId, notifUri, events}


class EventFilter(BaseModel):
    tgtUe: dict = {"anyUeId": True}


class EventSub(BaseModel):
    event: str
    eventFilter: EventFilter | None = None


class SubscriptionRequest(BaseModel):
    notifId: str
    notifUri: str
    eventsSubs: list[EventSub]


# ── Static pools (fallback / non-capture events) ─────────────────────────────

UE_POOL = [
    {"supi": "imsi-001011234567890", "ipv4Addr": "10.0.1.10"},
    {"supi": "imsi-001011234567891", "ipv4Addr": "10.0.1.11"},
    {"supi": "imsi-001011234567892", "ipv4Addr": "10.0.1.12"},
]

CELLS = [
    {"tac": "000001", "nrCellId": "000000001"},
    {"tac": "000002", "nrCellId": "000000002"},
    {"tac": "000003", "nrCellId": "000000003"},
]

PLMN = {"mcc": "001", "mnc": "01"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _iso(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _bitrate(mbps: float) -> str:
    return f"{mbps:.2f} Mbps"


def _supi_for_ip(ip: str) -> str:
    """Deterministic synthetic SUPI per IP. Keeps schema 3GPP-shaped."""
    h = abs(hash(ip)) % 10_000_000_000
    return f"imsi-0010199{h:010d}"


# ── Random generators ────────────────────────────────────────────────────────

def generate_perf_data() -> dict[str, Any]:
    ue = random.choice(UE_POOL)
    thr_ul = round(random.uniform(1, 20), 2)
    thr_dl = round(random.uniform(10, 100), 2)
    return {
        "ueIpAddr": {"ipv4Addr": ue["ipv4Addr"]},
        "appId": f"app-{random.choice(['video', 'voip', 'web'])}",
        "timeStamp": _now(),
        "perfData": {
            "thrputUl": _bitrate(thr_ul),
            "thrputDl": _bitrate(thr_dl),
            "pdb": random.randint(5, 50),
            "plr": random.randint(0, 30),
        },
    }


def generate_ue_mobility() -> dict[str, Any]:
    ue = random.choice(UE_POOL)
    cells = random.sample(CELLS, 2)
    trajs = []
    for i, cell in enumerate(cells):
        trajs.append({
            "ts": _now(),
            "location": {
                "nrLocation": {
                    "tai": {"plmnId": PLMN, "tac": cell["tac"]},
                    "ncgi": {"plmnId": PLMN, "nrCellId": cell["nrCellId"]},
                    "ageOfLocationInformation": i * 5,
                }
            },
        })
    return {"supi": ue["supi"], "appId": "app-mobility-test", "ueTrajs": trajs}


def generate_ue_comm_random() -> dict[str, Any]:
    ue = random.choice(UE_POOL)
    return {
        "supi": ue["supi"],
        "appId": "app-mock",
        "ulVol": random.randint(100, 10000),
        "dlVol": random.randint(100, 10000),
        "commDur": random.randint(1, 60),
        "comms": [{"startTime": _now(), "endTime": _now()}],
    }


# ── Scapy live capture → flow aggregator ─────────────────────────────────────

class FlowAggregator:
    """Track 5-tuple flows. Produce per-src-IP UE_COMM."""

    def __init__(self):
        self.lock = threading.Lock()
        self.flows: dict[tuple, dict] = {}

    def on_packet(self, src: str, dst: str, sport: int, dport: int,
                  proto: str, length: int, ts: float):
        if src in IGNORE_SRCS:
            return
        key = (src, dst, sport, dport, proto)
        with self.lock:
            f = self.flows.get(key)
            if f is None:
                f = {"start": ts, "last": ts, "ul": 0, "dl": 0, "src": src}
                self.flows[key] = f
            f["last"] = ts
            f["ul"] += length
            rev = (dst, src, dport, sport, proto)
            rf = self.flows.get(rev)
            if rf is not None:
                rf["dl"] += length

    def snapshot(self) -> dict[str, list[dict]]:
        now = time.time()
        per_src: dict[str, list[dict]] = defaultdict(list)
        with self.lock:
            stale = []
            for key, f in self.flows.items():
                if now - f["last"] > FLOW_IDLE_SECONDS:
                    stale.append(key)
                    continue
                # Per-window deltas (bytes since last snapshot), NOT cumulative.
                # A long-lived flow (e.g. a continuous ping) would otherwise ramp
                # forever; the model needs the volume *in this window*.
                ul_d = int(f["ul"] - f.get("rep_ul", 0))
                dl_d = int(f["dl"] - f.get("rep_dl", 0))
                rep_ts = f.get("rep_ts", f["start"])
                f["rep_ul"] = f["ul"]
                f["rep_dl"] = f["dl"]
                f["rep_ts"] = f["last"]
                if ul_d <= 0 and dl_d <= 0:
                    continue  # no new traffic this window
                per_src[f["src"]].append({
                    "startTime": _iso(rep_ts),
                    "endTime": _iso(f["last"]),
                    "ul": ul_d,
                    "dl": dl_d,
                    "dur": max(int(round(f["last"] - rep_ts)), 0),
                })
            for k in stale:
                del self.flows[k]
        return per_src


flow_agg: FlowAggregator | None = None
_sniffer = None


def _start_capture(iface: str) -> FlowAggregator:
    from scapy.all import IP, TCP, UDP, AsyncSniffer  # lazy import; scapy is heavy

    agg = FlowAggregator()

    def cb(pkt):
        if IP not in pkt:
            return
        ip = pkt[IP]
        sport = dport = 0
        proto = "other"
        if TCP in pkt:
            proto = "tcp"
            sport, dport = int(pkt[TCP].sport), int(pkt[TCP].dport)
        elif UDP in pkt:
            proto = "udp"
            sport, dport = int(pkt[UDP].sport), int(pkt[UDP].dport)
        agg.on_packet(ip.src, ip.dst, sport, dport, proto, int(ip.len), float(pkt.time))

    global _sniffer
    _sniffer = AsyncSniffer(iface=iface, filter=CAPTURE_BPF, prn=cb, store=False)
    _sniffer.start()
    logger.info(f"scapy sniff started iface={iface} bpf={CAPTURE_BPF!r}")
    return agg


def generate_ue_comm_live() -> list[dict]:
    if flow_agg is None:
        return [generate_ue_comm_random()]
    snap = flow_agg.snapshot()
    if not snap:
        return []
    out = []
    for src_ip, flows in snap.items():
        ul_total = sum(f["ul"] for f in flows)
        dl_total = sum(f["dl"] for f in flows)
        comm_dur = max(f["dur"] for f in flows)
        out.append({
            "supi": _supi_for_ip(src_ip),
            "appId": f"app-capture",
            "ulVol": ul_total,
            "dlVol": dl_total,
            "commDur": comm_dur,
            "comms": [{"startTime": f["startTime"], "endTime": f["endTime"]} for f in flows],
        })
    return out


# ── Event generators (each returns LIST of info dicts) ───────────────────────

EVENT_GENERATORS: dict[str, tuple[str, Any]] = {
    "PERF_DATA":   ("perfDataInfos",   lambda: [generate_perf_data()]),
    "UE_MOBILITY": ("ueMobilityInfos", lambda: [generate_ue_mobility()]),
    "UE_COMM":     ("ueCommInfos",     generate_ue_comm_live),
}


def build_notification(notif_id: str, events: list[str]) -> dict[str, Any]:
    event_notifs = []
    for event in events:
        entry = EVENT_GENERATORS.get(event)
        if not entry:
            continue
        field_name, generator = entry
        items = generator()
        if not items:
            continue
        event_notifs.append({
            "event": event,
            "timeStamp": _now(),
            field_name: items,
        })
    return {"notifId": notif_id, "eventNotifs": event_notifs}


# ── Background sender ─────────────────────────────────────────────────────────

INTERVAL_SECONDS = CAPTURE_WINDOW if CAPTURE_IFACE else 5


async def notification_loop():
    await asyncio.sleep(2)
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            for sub_id, sub in list(subscriptions.items()):
                events = sub["events"]
                payload = build_notification(sub["notifId"], events)
                if not payload["eventNotifs"]:
                    continue
                try:
                    r = await client.post(sub["notifUri"], json=payload)
                    logger.info(
                        f"→ {sub['notifUri']} events={events} status={r.status_code}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify {sub['notifUri']}: {e}")
            await asyncio.sleep(INTERVAL_SECONDS)


@app.on_event("startup")
async def startup():
    global flow_agg
    if CAPTURE_IFACE:
        try:
            flow_agg = _start_capture(CAPTURE_IFACE)
        except Exception as e:
            logger.error(f"failed to start capture: {e}")
    asyncio.create_task(notification_loop())


@app.on_event("shutdown")
async def shutdown():
    if _sniffer is not None:
        try:
            _sniffer.stop()
        except Exception:
            pass


# ── API endpoints ─────────────────────────────────────────────────────────────

@app.post("/nnef-event-exposure/v1/subscriptions", status_code=201)
def create_subscription(body: SubscriptionRequest):
    sub_id = str(uuid.uuid4())
    events = [s.event for s in body.eventsSubs]
    subscriptions[sub_id] = {
        "notifId": body.notifId,
        "notifUri": body.notifUri,
        "events": events,
    }
    logger.info(f"Subscription created: {sub_id} → {body.notifUri} events={events}")
    return {"subscriptionId": sub_id, "notifId": body.notifId, "notifUri": body.notifUri}


@app.delete("/nnef-event-exposure/v1/subscriptions/{sub_id}", status_code=204)
def delete_subscription(sub_id: str):
    if sub_id not in subscriptions:
        raise HTTPException(status_code=404, detail="Subscription not found")
    del subscriptions[sub_id]
    logger.info(f"Subscription deleted: {sub_id}")
    return Response(status_code=204)


@app.get("/nnef-event-exposure/v1/subscriptions")
def list_subscriptions():
    return subscriptions


@app.get("/debug/flows")
def debug_flows():
    if flow_agg is None:
        return {"enabled": False}
    return {"enabled": True, "iface": CAPTURE_IFACE, "flows_by_src": flow_agg.snapshot()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8990, log_level="info")
