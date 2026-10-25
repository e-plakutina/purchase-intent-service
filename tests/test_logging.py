"""
Тесты проверяют, что каждый запрос к /v1/predict записывается в таблицу логов с фичами и настоящим кодом ответа - 200,
422 или 500; тело, которое не является JSON, сохраняется как {"raw": ...}.
"""

import pytest

from purchase_intent import db


@pytest.fixture()
def saved(monkeypatch):
    rows = []
    monkeypatch.setattr(db, "save_prediction", lambda *args: rows.append(args))
    return rows


def test_features_logged_on_200(client, good_row, saved):
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    assert saved[0][1] == good_row
    assert saved[0][5] == 200


def test_features_logged_on_422(client, good_row, saved):
    row = {**good_row, "Informational": -1}
    r = client.post("/v1/predict", json=row)
    assert r.status_code == 422
    assert saved[0][1] == row
    assert saved[0][5] == 422


def test_garbage_body_logged_as_raw(client, saved):
    r = client.post(
        "/v1/predict", content=b"not json", headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 422
    assert saved[0][1] == {"raw": "not json"}


def test_features_logged_on_500(client, good_row, saved, monkeypatch):
    class Broken:
        def predict_proba(self, X):
            raise RuntimeError("model failed")

    monkeypatch.setattr(client.app.state, "pipeline", Broken())
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 500
    assert saved[0][1] == good_row
    assert saved[0][5] == 500
