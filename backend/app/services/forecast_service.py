import pandas as pd
from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta

from app.ml.datasets.snapshot_dataset import build_ml_dataset
from app.ml.risk import pressure_to_risk



def train_and_forecast(db: Session, horizon_hours: int = 1):
    """
    Train forecasting model for each hospital
    and return next-hour pressure predictions.
    """

    df = build_ml_dataset(db, horizon_hours=horizon_hours)

    predictions = []

    hospitals = df["hospital_id"].unique()

    for hospital_id in hospitals:
        hospital_df = df[df["hospital_id"] == hospital_id].copy()

        # Need enough history
        if len(hospital_df) < 10:
            continue

        hospital_df = hospital_df.sort_values("snapshot_time")

        series = hospital_df["pressure_score"]

        try:
            model = ARIMA(series, order=(2, 1, 2))
            model_fit = model.fit()

            forecast_value = model_fit.forecast(steps=1).iloc[0]
            risk_level = pressure_to_risk(forecast_value)

            last_time = hospital_df["snapshot_time"].max()
            forecast_time = last_time + timedelta(hours=horizon_hours)

            predictions.append({
                "hospital_id": hospital_id,
                "predicted_pressure": float(forecast_value),
                "forecast_time": forecast_time,
                "horizon_hours": horizon_hours,
                "risk_level": risk_level,
            })

        except Exception as e:
            print(f"Model failed for hospital {hospital_id}: {e}")

    return predictions
