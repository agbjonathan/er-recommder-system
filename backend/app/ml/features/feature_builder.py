from app.ml.features.pressure import compute_pressure_score
import pandas as pd

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw ERSnapshot row into ML features.
    """

    df = df.sort_values(["hospital_id", "snapshot_time"]).copy()

    df["pressure_score"] = df.apply(compute_pressure_score, axis=1)

    df["hour"] = df["snapshot_time"].dt.hour
    df["day_of_week"] = df["snapshot_time"].dt.dayofweek
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    df["pressure_lag_1"] = df.groupby("hospital_id")["pressure_score"].shift(1)
    df["pressure_lag_2"] = df.groupby("hospital_id")["pressure_score"].shift(2)
    df["pressure_lag_3"] = df.groupby("hospital_id")["pressure_score"].shift(3)

    df["pressure_trend"] = df["pressure_lag_1"] - df["pressure_lag_3"]

    return df
