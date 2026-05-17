import os
import random
import uuid

NEF_URL = "http://nef-sim:8990/nnef-event-exposure/v1/subscriptions"
AUTH_HEADER = {"Authorization": f"Bearer {os.environ['AION_TOKEN']}"} if os.environ.get("AION_TOKEN") else {}
SNSSAI = {"sst": 2, "sd": "000002"}
DNN = "internet"


def make_notif_id():
    return f"perf-{uuid.uuid4().hex[:8]}"


def nef_subscription(notif_id):
    return {
        "notifId": notif_id,
        "nefUrl": NEF_URL,
        "snssai": SNSSAI,
        "dnn": DNN,
        "events": ["PERF_DATA", "UE_MOBILITY"],
    }


def random_nef_payload(notif_id):
    return {
        "notifId": notif_id,
        "eventNotifs": [
            {
                "event": "PERF_DATA",
                "perfDataInfos": [
                    {
                        "ueIpAddr": {"ipv4Addr": f"10.0.{random.randint(0,255)}.{random.randint(1,254)}"},
                        "appId": random.choice(["app-voip", "app-video", "app-data"]),
                        "perfData": {
                            "thrputUl": f"{random.uniform(1, 50):.2f} Mbps",
                            "thrputDl": f"{random.uniform(5, 100):.2f} Mbps",
                            "pdb": random.randint(5, 100),
                            "plr": random.randint(0, 50),
                        },
                        "timeStamp": "2025-01-01T00:00:00Z",
                    }
                ],
            },
            {
                "event": "UE_MOBILITY",
                "ueMobilityInfos": [
                    {
                        "supi": f"imsi-00101{random.randint(1000000000, 9999999999)}",
                        "ueTrajs": [
                            {
                                "ts": "2025-01-01T00:00:00Z",
                                "location": {
                                    "nrLocation": {
                                        "tai": {"tac": "000001"},
                                        "ncgi": {"nrCellId": f"{random.randint(1,10):09d}"},
                                    }
                                },
                            }
                        ],
                    }
                ],
            },
        ],
    }
