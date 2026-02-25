"""
Recommendation endpoint for ER facilities.
"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Hospital, Forecast
from app.utils.time import get_current_time
from app.services.routing import haversine_distance

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get("")
async def get_recommendations(
    latitude: float = Query(..., description="User's latitude"),
    longitude: float = Query(..., description="User's longitude"),
    max_distance: Optional[float] = Query(10.0, description="Maximum distance in km"),
    limit: int = Query(5, description="Maximum number of recommendations to return"),
    db: Session = Depends(get_db),
):
    """
    Recommend nearby ER facilities based on predicted congestion and distance.
    
    Args:
        latitude (float): User's current latitude.
        longitude (float): User's current longitude.
        max_distance (float, optional): Max distance in km to consider. Defaults to 10 km.
        limit (int, optional): Max number of recommendations to return. Defaults to 5.
    Returns:
        dict: {
            "results": [
                {
                    "hospital_id": int,
                    "name": str,
                    "hospital_latitude": float,
                    "hospital_longitude": float,
                    "distance_km": float,
                    "predicted_pressure": float or None,
                    "risk_level": str or None,
                    "forecast_time": datetime or None,
                },
                ...
            ],
            "user_location": {
                "latitude": float,
                "longitude": float
            }
        }

    """

    now = get_current_time()

    hospitals = (
        db.query(Hospital)
        .filter(
            Hospital.latitude != 0,
            Hospital.longitude != 0,
            Hospital.is_active == True,
        )
        .all()
    )

    candidates = []

    for h in hospitals:
        distance = haversine_distance(latitude, longitude, h.latitude, h.longitude)
        if distance > max_distance:
            continue

        forecast = (
            db.query(Forecast)
            .filter(
                Forecast.hospital_id == h.id,
                Forecast.forecast_time >= now,
            )
            .order_by(Forecast.forecast_time.asc())  # nearest future forecast
            .first()
        )

        predicted_pressure = forecast.predicted_pressure if forecast else None

        # Composite score: 60% congestion, 40% distance (normalized)
        # Hospitals with no forecast sort last
        if predicted_pressure is not None:
            score = predicted_pressure * 0.6 + (distance / max_distance) * 0.4
        else:
            score = float('inf')

        candidates.append({
            "hospital_id": h.id,
            "name": h.name,
            "hospital_latitude": h.latitude,
            "hospital_longitude": h.longitude,
            "distance_km": round(distance, 2),
            "predicted_pressure": predicted_pressure,
            "risk_level": forecast.risk_level if forecast else None,
            "forecast_time": forecast.forecast_time if forecast else None,
            "_score": score,
        })

    candidates.sort(key=lambda x: x["_score"])

    # Strip internal score before returning
    results = [
        {k: v for k, v in c.items() if k != "_score"}
        for c in candidates[:limit]
    ]

    return {
        "results": results,
        "user_location": {"latitude": latitude, "longitude": longitude},
    }