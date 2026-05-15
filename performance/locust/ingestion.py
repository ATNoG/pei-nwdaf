from locust import HttpUser, task, between, TaskSet
from common import random_nef_payload, nef_subscription, make_notif_id, AUTH_HEADER


class IngestionTasks(TaskSet):

    @task(10)
    def ingest_event(self):
        with self.client.post(
            "/data-ingestion/nef/notify",
            json=random_nef_payload(self.user.notif_id),
            headers=AUTH_HEADER,
            name="POST /data-ingestion/nef/notify",
            catch_response=True,
        ) as r:
            if r.status_code == 204:
                r.success()
            else:
                r.failure(f"{r.status_code}: {r.text[:200]}")

    @task(1)
    def list_subscriptions(self):
        self.client.get(
            "/data-ingestion/nef/subscriptions",
            headers=AUTH_HEADER,
            name="GET /data-ingestion/nef/subscriptions",
        )


class IngestionUser(HttpUser):
    tasks = [IngestionTasks]
    wait_time = between(0.05, 0.1)
    weight = 3

    def on_start(self):
        self.client.verify = False
        self.notif_id = make_notif_id()
        with self.client.post(
            "/data-ingestion/nef/subscriptions",
            json=nef_subscription(self.notif_id),
            headers=AUTH_HEADER,
            name="POST /data-ingestion/nef/subscriptions (setup)",
            catch_response=True,
        ) as r:
            if r.status_code == 201:
                r.success()
            else:
                r.failure(f"subscription failed: {r.status_code} {r.text[:200]}")

    def on_stop(self):
        self.client.delete(
            f"/data-ingestion/nef/subscriptions/{self.notif_id}",
            headers=AUTH_HEADER,
            name="DELETE /data-ingestion/nef/subscriptions (teardown)",
        )
