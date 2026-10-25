"""
Тесты проверяют контракт API: эндпоинты /health и /ready отвечают 200, /v1/predict отклоняет некорректные запросы с 422.
"""

import pytest


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert "model_version" in r.json()


def test_ready(client):
    assert client.get("/ready").status_code == 200


@pytest.mark.parametrize(
    "field, value",
    [
        ("Month", "Jan"),
        ("Month", "Jun"),
        ("VisitorType", "abc"),
        ("PageValues", None),
        ("Informational", -1),
        ("ProductRelated_Duration", 70000),
        ("BounceRates", 1.5),
        ("ExitRates", -0.1),
        ("OperatingSystems", 0),
        ("TrafficType", 21),
        ("Administrative", "abc"),
        ("Weekend", "maybe"),
    ],
)
def test_invalid_value_is_422(client, good_row, field, value):
    r = client.post("/v1/predict", json={**good_row, field: value})
    assert r.status_code == 422


def test_missing_field_is_422(client, good_row):
    row = dict(good_row)
    del row["Month"]
    assert client.post("/v1/predict", json=row).status_code == 422


def test_extra_field_is_422(client, good_row):
    r = client.post("/v1/predict", json={**good_row, "hacker_field": 1})
    assert r.status_code == 422


def test_target_in_request_is_422(client, good_row):
    r = client.post("/v1/predict", json={**good_row, "Revenue": True})
    assert r.status_code == 422


def test_garbage_body_is_422(client):
    r = client.post(
        "/v1/predict", content=b"not json", headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 422
