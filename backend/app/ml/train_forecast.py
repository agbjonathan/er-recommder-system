from sqlalchemy.orm import Session
from statsmodels.tsa.arima.model import ARIMA

from app.db.session import SessionLocal
from app.ml.datasets.snapshot_dataset import build_ml_dataset


def train_arima_for_hospital(hospital_id: int):
    db: Session = SessionLocal()

    print("Loading dataset...")
    df = build_ml_dataset(db)

    # Filter one hospital
    hospital_df = df[df["hospital_id"] == hospital_id].sort_values("snapshot_time")

    if len(hospital_df) < 10:
        print("Not enough data to train model.")
        return

    # Time series = pressure history
    series = hospital_df["pressure_score"]

    print(f"Training ARIMA for hospital {hospital_id} on {len(series)} points")

    # (p,d,q) = (2,1,2) is a good general starting point
    model = ARIMA(series, order=(2, 1, 2))
    model_fit = model.fit()

    print(model_fit.summary())

    # Forecast next hour
    forecast = model_fit.forecast(steps=1)
    predicted_pressure = float(forecast.iloc[0])

    print(f"\n🔮 Predicted pressure next hour: {predicted_pressure:.3f}")

    db.close()


if __name__ == "__main__":
    # Change hospital_id to one you know exists
    train_arima_for_hospital(hospital_id=1)
