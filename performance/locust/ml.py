from locust import HttpUser, task, between, TaskSet
from common import AUTH_HEADER

TAGS = {
    "snssai_sst": "1",
    "snssai_sd": "1",
    "dnn": "internet",
    "event": "PERF_DATA",
}


class MLTasks(TaskSet):

    @task
    def run_inference(self):
        with self.client.post(
            "/pei-ml/v1/inference",
            json={"output_field": "thrputDl_mbps_min", "tags": TAGS},
            headers=AUTH_HEADER,
            name="POST /pei-ml/inference",
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f"{r.status_code}: {r.text[:200]}")


class MLUser(HttpUser):
    tasks = [MLTasks]
    wait_time = between(0.1, 0.3)
    weight = 1

    def on_start(self):
        self.client.verify = False
        self.client.timeout = 120
