import pandas as pd
from sqlalchemy.orm import Session

from app.db.models import ERSnapshot
from app.ml.features.feature_builder import build_features
from app.utils.time import delta_hours, get_current_time

def load_snapshots_df(db: Session, lookback_hours:int = 72) -> pd.DataFrame:
    """
    Load ER snapshots from the last 3 days from database into a pandas DataFrame.
    """

    cutoff = get_current_time() - delta_hours(lookback_hours)
    
    snapshots = (
        db.query(ERSnapshot)
        .filter(ERSnapshot.snapshot_time >= cutoff)
        .order_by(ERSnapshot.hospital_id, ERSnapshot.snapshot_time)
        .all()
    )

    data = [
        {
            "hospital_id": s.hospital_id,
            "functional_stretchers": s.functional_stretchers,
            "occupied_stretchers": s.occupied_stretchers,
            "patients_total": s.patients_total,
            "patients_waiting_mc": s.patients_waiting_mc,
            "patients_over_24h": s.patients_over_24h,
            "patients_over_48h": s.patients_over_48h,
            "snapshot_time": s.snapshot_time,
        }
        for s in snapshots
    ]

    df = pd.DataFrame(data)

    # Ensure datetime type
    df["snapshot_time"] = pd.to_datetime(df["snapshot_time"], utc=True)

    return df

def add_forecast_targets(df: pd.DataFrame, horizon_hours: int = 1) -> pd.DataFrame:
    """
    Create future pressure targets for forecasting.
    """

    df = df.sort_values(["hospital_id", "snapshot_time"])

    df[f"target_pressure_t+{horizon_hours}h"] = (
        df.groupby("hospital_id")["pressure_score"].shift(-horizon_hours)
    )

    return df


def build_ml_dataset(db: Session, horizon_hours: int = 1) -> pd.DataFrame:
    """
    Full pipeline: DB → Features → Targets
    """


    df = load_snapshots_df(db)

    
    df = build_features(df)

    
    true_latest_times = df.groupby("hospital_id")["snapshot_time"].max()

    
    df = add_forecast_targets(df, horizon_hours=horizon_hours)

    
    df = df.dropna()


    df = df.merge(
        true_latest_times.rename("true_latest_snapshot_time"),
        on="hospital_id"
    )

    return df

