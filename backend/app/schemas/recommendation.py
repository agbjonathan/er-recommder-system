"""
Recommendation schema definitions for API responses.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone


class LocationInput(BaseModel):
    """User location input."""
    latitude: float = Field(..., description="User's latitude")
    longitude: float = Field(..., description="User's longitude")


class RecommendationRequest(BaseModel):
    """Request schema for hospital recommendations."""
    location: LocationInput
    severity: Optional[str] = Field("moderate", description="Medical severity level")
    max_distance_km: float = Field(10.0, description="Maximum search distance")
    max_wait_time_minutes: Optional[int] = Field(None, description="Maximum acceptable wait time")


class HospitalRecommendation(BaseModel):
    """Single hospital recommendation."""
    hospital_id: int
    hospital_name: str
    region: str
    address: Optional[str] = None
    latitude: float
    longitude: float
    distance_km: float = Field(..., description="Distance from user")
    current_wait_minutes: int = Field(..., description="Current wait time")
    predicted_wait_minutes: Optional[int] = Field(None, description="Predicted wait time")
    travel_time_minutes: float = Field(..., description="Estimated travel time")
    recommendation_score: float = Field(..., description="Composite recommendation score")
    risk_level: Optional[str] = Field(None, description="Overcrowding risk level")


class RecommendationResponse(BaseModel):
    """Response schema for recommendations."""
    recommendations: List[HospitalRecommendation]
    user_location: LocationInput
    search_radius_km: float
    severity: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    total_results: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "hospital_id": 1,
                        "hospital_name": "Example Hospital",
                        "region": "Longueuil",
                        "distance_km": 3.5,
                        "current_wait_minutes": 45,
                        "travel_time_minutes": 10,
                        "recommendation_score": 85.5,
                        "risk_level": "low"
                    }
                ],
                "user_location": {"latitude": 45.5312, "longitude": -73.5185},
                "search_radius_km": 10.0,
                "severity": "moderate",
                "total_results": 1
            }
        }
