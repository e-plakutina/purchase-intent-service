"""
Тесты проверяют, насколько корректно работает преобразование фичей. Исходные данные берутся из conftest.py.
"""

import pandas as pd
import pytest

from purchase_intent.features import CODE_CAT_COLS, add_features


def test_flags(good_row):
    output = add_features(pd.DataFrame([{**good_row, "Informational": 0}]))
    assert output.loc[0, "has_PageValues"] == 1
    assert output.loc[0, "has_BounceRates"] == 1
    assert output.loc[0, "has_Informational"] == 0
    assert output.loc[0, "has_SpecialDay"] == 0


def test_avg_time(good_row):
    output = add_features(pd.DataFrame([good_row]))
    assert output.loc[0, "ProductRelated_avg_time"] == pytest.approx(1200.5 / 35)


def test_avg_time_with_zero_count(good_row):
    output = add_features(pd.DataFrame([{**good_row, "Informational": 0}]))
    assert output.loc[0, "Informational_avg_time"] == 0.0


def test_types_are_cast(good_row):
    output = add_features(pd.DataFrame([good_row]))
    assert output.loc[0, "Browser"] == "2"
    assert output.loc[0, "Weekend"] == 0


def test_input_is_not_changed(good_row):
    frame = pd.DataFrame([good_row])
    add_features(frame)
    assert list(frame.columns) == list(good_row)
    assert frame.loc[0, "Browser"] == 2


def test_same_score_for_int_and_str_codes(client, good_row):
    pipeline = client.app.state.pipeline
    features = client.app.state.meta["features"]
    str_row = {**good_row, **{c: str(good_row[c]) for c in CODE_CAT_COLS}, "Weekend": 0}
    expected = pipeline.predict_proba(
        pd.DataFrame([str_row]).reindex(columns=features)
    )[0, 1]

    score = client.post("/v1/predict", json=good_row).json()["score"]
    assert score == pytest.approx(expected)
