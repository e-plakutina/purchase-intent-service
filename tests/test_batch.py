"""
Тесты проверяют батч-эндпоинт: на каждую строку возвращается предсказание в том же порядке и с тем же score, что у
/v1/predict; пустой батч, батч больше 1000 строк и батч с одной некорректной строкой отклоняются с кодом 422.
"""

import pytest


def test_batch_matches_single(client, good_row):
    rows = [good_row, {**good_row, "PageValues": 0.0, "Month": "Feb"}]
    r = client.post("/v1/predict/batch", json={"rows": rows})
    assert r.status_code == 200
    predictions = r.json()["predictions"]
    assert len(predictions) == len(rows)
    for row, pred in zip(rows, predictions):
        single = client.post("/v1/predict", json=row).json()
        assert pred["score"] == pytest.approx(single["score"])
        assert pred["purchase"] == single["purchase"]


@pytest.mark.parametrize("n_rows", [0, 1001])
def test_batch_size_out_of_bounds_is_422(client, good_row, n_rows):
    r = client.post("/v1/predict/batch", json={"rows": [good_row] * n_rows})
    assert r.status_code == 422


def test_batch_with_one_bad_row_is_422(client, good_row):
    rows = [good_row, {**good_row, "Month": "Jan"}]
    r = client.post("/v1/predict/batch", json={"rows": rows})
    assert r.status_code == 422
    assert r.json()["detail"][0]["loc"] == ["body", "rows", 1, "Month"]
