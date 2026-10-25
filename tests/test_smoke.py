import uuid


def test_predict_smoke(client, good_row):
    r = client.post("/v1/predict", json=good_row)
    assert r.status_code == 200
    body = r.json()
    assert 0.0 <= body["score"] <= 1.0
    assert isinstance(body["purchase"], bool)
    assert body["latency_ms"] >= 0
    assert body["model_version"] == client.app.state.version
    uuid.UUID(body["request_id"])


def test_purchase_follows_threshold(client, good_row):
    body = client.post("/v1/predict", json=good_row).json()
    assert body["purchase"] == (body["score"] >= client.app.state.meta["threshold"])


def test_same_input_gives_same_score(client, good_row):
    s1 = client.post("/v1/predict", json=good_row).json()["score"]
    s2 = client.post("/v1/predict", json=good_row).json()["score"]
    assert s1 == s2
