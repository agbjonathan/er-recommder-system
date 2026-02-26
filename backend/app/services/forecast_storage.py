from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.db.models import Forecast
from datetime import datetime
import pandas as pd
from app.utils.time import get_current_time, delta_hours
from app.core.logging import logger
from datetime import timezone



def save_forecasts(db: Session, predictions: list, horizon_hours: int = 1):
    """
    Save ML forecast results into the database.
    Skips forecasts that already exist (same hospital, time, horizon).
    """
    now = get_current_time()
    max_reasonable_future = now + delta_hours(horizon_hours + 2)



    for p in predictions:

        forecast_time = to_python(p["forecast_time"])

        # Reject forecasts that are unreasonably far in the future
        if forecast_time.tzinfo is None:
            forecast_time = forecast_time.replace(tzinfo=timezone.utc)
            
        if forecast_time > max_reasonable_future:
            logger.error(
                f"Refusing to save forecast for hospital {p['hospital_id']}: "
                f"forecast_time={forecast_time} exceeds max allowed {max_reasonable_future}"
            )
            continue

        stmt = (
            insert(Forecast)
            .values(
                hospital_id=int(to_python(p["hospital_id"])),
                predicted_pressure=to_python(p["predicted_pressure"]),
                forecast_time=forecast_time,
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

