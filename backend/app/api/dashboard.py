from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from app.db.session import get_db
from app.db.models import Hospital, Forecast, ForecastError
from app.ml.risk import pressure_to_risk

TIMEZONE = ZoneInfo("America/Montreal")

router = APIRouter(prefix="/dashboard", tags=["dashboard"])



@router.get("/congestion/map")
def get_congestion_map(horizon: int = 1, db: Session = Depends(get_db)):
    """
    Latest forecast per hospital as a GeoJSON FeatureCollection.
    """
    latest = (
        db.query(
            Forecast.hospital_id,
            func.max(Forecast.forecast_time).label("latest_time"),
        )
        .filter(Forecast.horizon_hours == horizon)
        .group_by(Forecast.hospital_id)
        .subquery()
    )

    rows = (
        db.query(Hospital, Forecast)
        .join(latest, Hospital.id == latest.c.hospital_id)
        .join(
            Forecast,
            (Forecast.hospital_id == latest.c.hospital_id)
            & (Forecast.forecast_time == latest.c.latest_time),
        )
        .filter(Hospital.is_active == True)
        .all()
    )

    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [h.longitude, h.latitude],
            },
            "properties": {
                "hospital_id": h.id,
                "name": h.name,
                "region": h.region,
                "current_pressure": None,
                "predicted_pressure": f.predicted_pressure,
                "risk_level": f.risk_level,
            },
        }
        for h, f in rows
    ]

    return {
        "type": "FeatureCollection",
        "features": features,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }



@router.get("/stats")
def get_dashboard_stats(
    horizon_hours: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Aggregated chart data for the analytics dashboard.
    Returns:
      - global_series:    hourly predicted vs observed pressure (last 24h)
      - risk_comparison:  predicted vs observed counts per risk level
      - hospital_stats:   per-hospital mean predicted/observed and risk level
    """
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    forecasts_24h = (
        db.query(
            func.date_trunc("hour", Forecast.forecast_time).label("hour"),
            func.avg(Forecast.predicted_pressure).label("avg_predicted"),
        )
        .filter(
            Forecast.horizon_hours == horizon_hours,
            Forecast.forecast_time >= since,
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    errors_24h = (
        db.query(
            func.date_trunc("hour", ForecastError.forecast_time).label("hour"),
            func.avg(ForecastError.observed_pressure).label("avg_observed"),
        )
        .filter(
            ForecastError.horizon_hours == horizon_hours,
            ForecastError.evaluated_at >= since,
        )
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    observed_by_hour = {
        row.hour: row.avg_observed for row in errors_24h
    }

    global_series = [
        {
            "label": row.hour.astimezone(TIMEZONE).strftime("%H:%M"),
            "predicted": round(row.avg_predicted, 4),
            "observed": round(observed_by_hour[row.hour], 4)
            if row.hour in observed_by_hour else None,
        }
        for row in forecasts_24h
    ]

    predicted_risk_counts = (
        db.query(
            Forecast.risk_level,
            func.count(Forecast.id).label("count"),
        )
        .filter(
            Forecast.horizon_hours == horizon_hours,
            Forecast.forecast_time >= since,
        )
        .group_by(Forecast.risk_level)
        .all()
    )

    observed_risk_counts = (
        db.query(
            case(
                (ForecastError.observed_pressure < 0.4, "LOW"),
                (ForecastError.observed_pressure < 0.7, "MEDIUM"),
                else_="HIGH",
            ).label("risk_level"),
            func.count(ForecastError.id).label("count"),
        )
        .filter(
            ForecastError.horizon_hours == horizon_hours,
            ForecastError.evaluated_at >= since, 
        )
        .group_by("risk_level")
        .all()
    )

    observed_risk_map = {row.risk_level: row.count for row in observed_risk_counts}

    risk_comparison = [
        {
            "risk": row.risk_level,
            "predicted": row.count,
            "observed": observed_risk_map.get(row.risk_level, 0),
        }
        for row in predicted_risk_counts
    ]

    mean_predicted = (
        db.query(
            Forecast.hospital_id,
            func.avg(Forecast.predicted_pressure).label("mean_predicted"),
        )
        .filter(
        Forecast.horizon_hours == horizon_hours,
        Forecast.forecast_time >= since,    
        )
        .group_by(Forecast.hospital_id)
        .subquery()
    )

    mean_observed = (
        db.query(
            ForecastError.hospital_id,
            func.avg(ForecastError.observed_pressure).label("mean_observed"),
        )
        .filter(
        ForecastError.horizon_hours == horizon_hours,
        ForecastError.evaluated_at >= since,  
        )
        .group_by(ForecastError.hospital_id)
        .subquery()
    )

    rows = (
        db.query(
            Hospital.id,
            Hospital.name,
            mean_predicted.c.mean_predicted,
            mean_observed.c.mean_observed,
        )
        .join(mean_predicted, Hospital.id == mean_predicted.c.hospital_id)
        .outerjoin(mean_observed, Hospital.id == mean_observed.c.hospital_id)
        .filter(Hospital.is_active == True)
        .order_by(mean_predicted.c.mean_predicted.desc())
        .all()
    )

    seen = set()
    hospital_stats = []
    for row in rows:
        if row.id in seen:
            continue
        seen.add(row.id)
        hospital_stats.append({
            "hospital_id": row.id,
            "name": row.name,
            "mean_predicted": round(row.mean_predicted, 4),
            "mean_observed": round(row.mean_observed, 4) if row.mean_observed else None,
            "risk_level": pressure_to_risk(row.mean_predicted),
        })

    return {
        "global_series": global_series,
        "risk_comparison": risk_comparison,
        "hospital_stats": hospital_stats,
        "generated_at": now.isoformat(),
    }