from sqlalchemy.orm import Session
from app.db.models import ForecastError
from app.utils.time import get_current_time, delta_hours

def get_recent_bias(
    db: Session,
    hospital_id: int,
    horizon_hours: int,
    lookback_hours: int = 24,
) -> float:
    """Mean signed error over recent window. Positive = model over-predicts."""
    cutoff = get_current_time() - delta_hours(lookback_hours)
    errors = (
        db.query(ForecastError)
        .filter(
            ForecastError.hospital_id == hospital_id,
            ForecastError.horizon_hours == horizon_hours,
            ForecastError.evaluated_at >= cutoff,
        )
        .all()
    )
    if len(errors) < 3:  # not enough signal
        return 0.0
    return sum(e.predicted_pressure - e.observed_pressure for e in errors) / len(errors)


def should_retrain(
    db: Session,
    hospital_id: int,
    horizon_hours: int,
    mae_threshold: float = 0.15,  # tune from your actual error table
    lookback_hours: int = 24,
) -> bool:
    """Returns True if recent MAE exceeds threshold."""
    cutoff = get_current_time() - delta_hours(lookback_hours)
    errors = (
        db.query(ForecastError)
        .filter(
            ForecastError.hospital_id == hospital_id,
            ForecastError.horizon_hours == horizon_hours,
            ForecastError.evaluated_at >= cutoff,
        )
        .all()
    )
    if len(errors) < 5:
        return False  # not enough data to judge
    mae = sum(e.absolute_error for e in errors) / len(errors)
    return mae > mae_threshold