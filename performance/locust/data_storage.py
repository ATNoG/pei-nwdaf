import time
from locust import HttpUser, task, between, TaskSet
from common import AUTH_HEADER


class DataStorageTasks(TaskSet):

    @task
    def get_processed(self):
        end = int(time.time())
        start = end - 3600
        self.client.get(
            f"/data-storage/api/v1/processed?limit=100&start_time={start}&end_time={end}",
            headers=AUTH_HEADER,
            name="GET /data-storage/processed (ClickHouse)",
        )


class StorageQueryUser(HttpUser):
    tasks = [DataStorageTasks]
    wait_time = between(0.1, 0.3)
    weight = 2

    def on_start(self):
        self.client.verify = False
