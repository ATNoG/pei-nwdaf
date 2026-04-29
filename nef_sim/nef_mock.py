#!/usr/bin/env python3
"""
Mock NEF — Nnef_EventExposure (TS 29.591)
Supports: PERF_DATA, UE_MOBILITY
"""
import asyncio
import logging
import random
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Mock NEF — Nnef_EventExposure")

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


# ── Fake data generators ──────────────────────────────────────────────────────

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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _bitrate(mbps: float) -> str:
    """Format as 3GPP BitRate string."""
    return f"{mbps:.2f} Mbps"


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
            "pdb": random.randint(5, 50),          # ms
            "plr": random.randint(0, 30),           # tenths of %, i.e. 0..30 = 0%..3%
        },
    }


def generate_ue_mobility() -> dict[str, Any]:
    ue = random.choice(UE_POOL)
    # UE moves through 2 cells
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
    return {
        "supi": ue["supi"],
        "appId": "app-mobility-test",
        "ueTrajs": trajs,
    }


EVENT_GENERATORS = {
    "PERF_DATA": ("perfDataInfos", generate_perf_data),
    "UE_MOBILITY": ("ueMobilityInfos", generate_ue_mobility),
}


def build_notification(notif_id: str, events: list[str]) -> dict[str, Any]:
    event_notifs = []
    for event in events:
        if event not in EVENT_GENERATORS:
            continue
        field_name, generator = EVENT_GENERATORS[event]
        event_notifs.append({
            "event": event,
            "timeStamp": _now(),
            field_name: [generator()],
        })
    return {
        "notifId": notif_id,
        "eventNotifs": event_notifs,
    }


# ── Background sender ─────────────────────────────────────────────────────────

INTERVAL_SECONDS = 5


async def notification_loop():
    await asyncio.sleep(2)  # let server boot
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            for sub_id, sub in list(subscriptions.items()):
                events = sub["events"]
                payload = build_notification(sub["notifId"], events)
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
    asyncio.create_task(notification_loop())


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8990, log_level="info")
