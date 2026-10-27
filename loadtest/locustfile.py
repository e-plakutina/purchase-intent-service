"""
Нагрузочный тест API: виртуальные пользователи отправляют запросы к /v1/predict и /health.
"""

import json
from pathlib import Path

from locust import HttpUser, between, task

REQUEST = json.loads(
    (Path(__file__).resolve().parents[1] / "examples" / "request.json").read_text()
)


class ApiUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task(10)
    def predict(self):
        self.client.post("/v1/predict", json=REQUEST)

    @task(1)
    def health(self):
        self.client.get("/health")
