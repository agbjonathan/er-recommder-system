from app.db.session import SessionLocal
from app.services.forecast_service import train_and_forecast
from app.services.forecast_storage import save_forecasts


def run_forecasting():
    db = SessionLocal()

    predictions = train_and_forecast(db)

    if predictions:
        save_forecasts(db, predictions)
        print(f"Saved {len(predictions)} forecasts")

    db.close()


if __name__ == "__main__":
    run_forecasting()
