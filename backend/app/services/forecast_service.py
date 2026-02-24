import pandas as pd
from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta

from app.ml.datasets.snapshot_dataset import build_ml_dataset
from app.ml.risk import pressure_to_risk
from app.core.logging import logger
from app.ml.error_analysis import get_recent_bias, should_retrain

# Module-level cache: {(hospital_id, horizon_hours): model_fit}
_model_cache: dict = {}

def train_and_forecast(db: Session, horizon_hours: int = 1):
    df = build_ml_dataset(db, horizon_hours=horizon_hours)
    predictions = []

    for hospital_id in df["hospital_id"].unique():
        hospital_id = int(hospital_id)  
        hospital_df = (
            df[df["hospital_id"] == hospital_id]
            .sort_values("snapshot_time")
        )

        if len(hospital_df) < 10:
            continue

        cache_key = (hospital_id, horizon_hours)
        
        # Retrain if: no cached model OR error threshold exceeded
        if cache_key not in _model_cache or should_retrain(db, hospital_id, horizon_hours):
            try:
                model = ARIMA(hospital_df["pressure_score"], order=(2, 1, 2))
                _model_cache[cache_key] = model.fit()
                logger.info(f"Retrained model for hospital {hospital_id}")
            except Exception as e:
                logger.warning(f"Training failed for hospital {hospital_id}: {e}")
                continue

        model_fit = _model_cache[cache_key]

        try:
            forecast_series = model_fit.forecast(steps=horizon_hours)
            forecast_value = float(forecast_series.iloc[-1])

            # Apply bias correction from recent errors
            bias = get_recent_bias(db, hospital_id, horizon_hours)
            forecast_value -= bias

            risk_level = pressure_to_risk(forecast_value)
            last_time = hospital_df["true_latest_snapshot_time"].iloc[0]

            predictions.append({
                "hospital_id": hospital_id,
                "predicted_pressure": forecast_value,
                "forecast_time": last_time + timedelta(hours=horizon_hours),
                "horizon_hours": horizon_hours,
                "risk_level": risk_level,
            })

        except Exception as e:
            logger.warning(f"Inference failed for hospital {hospital_id}: {e}")

    return predictions
