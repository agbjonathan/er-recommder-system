from app.db.session import SessionLocal
from app.services.forecast_service import train_and_forecast
from app.services.forecast_storage import save_forecasts


def run_forecasting():
    db = SessionLocal()

    horizon_hours = [1,2,4]

    for h in horizon_hours: 
        predictions = train_and_forecast(db, h)
        if predictions:
            save_forecasts(db, predictions,h)


    db.close()


if __name__ == "__main__":
    run_forecasting()
