from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db.models import Forecast
from datetime import datetime
import pandas as pd



def save_forecasts(db: Session, predictions: list):
    """
    Save ML forecast results into the database.
    Skips forecasts that already exist (same hospital, time, horizon).
    """

    for p in predictions:
        stmt = (
            insert(Forecast)
            .values(
                hospital_id=int(to_python(p["hospital_id"])),
                predicted_pressure=to_python(p["predicted_pressure"]),
                forecast_time=to_python(p["forecast_time"]),
                horizon_hours=int(to_python(p["horizon_hours"])),
                risk_level=to_python(p["risk_level"]),
            )
            .on_conflict_do_nothing(constraint="uq_forecast_unique")
        )
        db.execute(stmt)

    db.commit()


def to_python(value):
    """Convert numpy / pandas types to native Python types."""
    if value is None:
        return None

    # NumPy integers
    if hasattr(value, "item"):
        return value.item()

    # Pandas Timestamp
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    return value

