from app.db.session import SessionLocal
from datetime import datetime
from app.core.logging import logger

from app.db.models import Forecast, ERSnapshot, ForecastError
from app.ml.features.pressure import compute_pressure_score


def evaluate_forecasts():

    db = SessionLocal()
    try : 
        # Get latest snapshot time in DB
        latest_snapshot_time = db.query(ERSnapshot.snapshot_time) \
            .order_by(ERSnapshot.snapshot_time.desc()) \
            .first()

        if not latest_snapshot_time:
            # print("No snapshots yet.")
            return

        latest_snapshot_time = latest_snapshot_time[0]

        # Get forecasts ready for evaluation
        forecasts = db.query(Forecast).filter(
            Forecast.forecast_time <= latest_snapshot_time,
            Forecast.evaluated == False
        ).all()

        # print(f"Found {len(forecasts)} forecasts to evaluate")

        for f in forecasts:

            # Get real snapshot at forecast time
            snapshot = db.query(ERSnapshot).filter(
                ERSnapshot.hospital_id == f.hospital_id,
                ERSnapshot.snapshot_time == f.forecast_time
            ).first()

            if not snapshot:
                continue  # Missing snapshot (data gap)

            # Compute real pressure
            observed_pressure = compute_pressure_score(snapshot)

            error = observed_pressure - f.predicted_pressure

            # Save error record
            error_record = ForecastError(
                hospital_id=f.hospital_id,
                forecast_id=f.id,
                predicted_pressure=f.predicted_pressure,
                observed_pressure=observed_pressure,
                absolute_error=abs(error),
                squared_error=error**2,
                # horizon_hours=f.horizon_hours,
                # forecast_time=f.forecast_time,
            )

            db.add(error_record)

            # Mark forecast as evaluated
            f.evaluated = True

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error during forecast evaluation: {e}")
    finally:
        db.close()
