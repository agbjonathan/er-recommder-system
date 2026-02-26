from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.session import get_db
from app.db.models import Forecast, Hospital
from app.ml.risk import pressure_to_risk

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.get("/latest")
def get_latest_forecasts(horizon: int = 1, db: Session = Depends(get_db)):
    """
    Return latest forecast per hospital.
    """

    subquery = (
        db.query(
            Forecast.hospital_id,
            func.max(Forecast.forecast_time).label("latest_time")
        )
        .filter(Forecast.horizon_hours == horizon)
        .group_by(Forecast.hospital_id)
        .subquery()
    )

    results = (
        db.query(Forecast, Hospital)
        .join(
            subquery,
            (Forecast.hospital_id == subquery.c.hospital_id) &
            (Forecast.forecast_time == subquery.c.latest_time)
        )
        .join(Hospital, Hospital.id == Forecast.hospital_id)
        .all()
    )

    response = []

    for forecast, hospital in results:
        response.append({
            "hospital_id": hospital.id,
            "hospital_name": hospital.name,
            "predicted_pressure": round(forecast.predicted_pressure, 3),
            "risk_level": forecast.risk_level,
            "forecast_time": forecast.forecast_time
        })

    return response
