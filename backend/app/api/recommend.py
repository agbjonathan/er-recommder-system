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
    db : Session = Depends(get_db),
):
    """
    Get ER facility recommendations based on location and criteria.
    
    Args:
        latitude: User's latitude coordinate
        longitude: User's longitude coordinate
        max_distance: Maximum distance to search for facilities
        
    Returns:
        dict: List of recommended ER facilities
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
        if distance <= max_distance:
            forecast = (
                db.query(Forecast)
                .filter(
                    Forecast.hospital_id == h.id,
                    Forecast.forecast_time >= now,
                ).order_by(Forecast.forecast_time.asc()).first()
            )

            candidates.append({
                "hospital_id": h.id,
                "name": h.name,
                "distance_km": round(distance, 2),
                "predicted_pressure": forecast.predicted_pressure if forecast else None,
                "forecast_time": forecast.forecast_time if forecast else None,
            })

    candidates.sort(
        key=lambda x: (x["predicted_pressure"], x["distance_km"])
    )
    return { "results": candidates[:limit] ,
            "user_location": {"latitude": latitude, "longitude": longitude}
            }