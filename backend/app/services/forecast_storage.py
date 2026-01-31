from sqlalchemy.orm import Session
from app.db.models import Forecast
from datetime import datetime
import pandas as pd



def save_forecasts(db: Session, predictions: list):
    """
    Save ML forecast results into the database.
    """

    for p in predictions:
        forecast = Forecast(
            hospital_id=int(to_python(p["hospital_id"])),
            predicted_pressure=to_python(p["predicted_pressure"]),
            forecast_time=to_python(p["forecast_time"]),
            horizon_hours=int(to_python(p["horizon_hours"])),
        )
        db.add(forecast)

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

