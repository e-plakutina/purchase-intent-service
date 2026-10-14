import numpy as np
import pandas as pd

CODE_CAT_COLS = ["OperatingSystems", "Browser", "Region", "TrafficType"]
COUNT_COLS = ["Administrative", "Informational", "ProductRelated"]
FLAG_BASE = [
    "PageValues",
    "Informational",
    "BounceRates",
    "SpecialDay",
]


def add_features(X: pd.DataFrame) -> pd.DataFrame:
    X = X.copy()
    X[CODE_CAT_COLS] = X[CODE_CAT_COLS].astype(str)
    X["Weekend"] = X["Weekend"].astype(int)
    for c in FLAG_BASE:
        X[f"has_{c}"] = (X[c] > 0).astype(int)
    for c in COUNT_COLS:
        X[f"{c}_avg_time"] = np.where(
            X[c] > 0, X[f"{c}_Duration"] / X[c].replace(0, np.nan), 0.0
        )
    return X
