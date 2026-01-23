"""
Region schema definitions.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict


class Coordinates(BaseModel):
    """Geographic coordinates."""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class RegionBounds(BaseModel):
    """Region boundary coordinates."""
    north: float = Field(..., description="Northern boundary")
    south: float = Field(..., description="Southern boundary")
    east: float = Field(..., description="Eastern boundary")
    west: float = Field(..., description="Western boundary")


class RegionCoordinates(BaseModel):
    """Region coordinate information."""
    center: Coordinates = Field(..., description="Region center point")
    bounds: RegionBounds = Field(..., description="Region boundaries")


class Region(BaseModel):
    """Region configuration schema."""
    name: str = Field(..., description="Region name")
    code: str = Field(..., description="Region code")
    timezone: str = Field(..., description="Timezone identifier")
    coordinates: RegionCoordinates = Field(..., description="Geographic coordinates")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Longueuil",
                "code": "LNG",
                "timezone": "America/Montreal",
                "coordinates": {
                    "center": {"latitude": 45.5312, "longitude": -73.5185},
                    "bounds": {
                        "north": 45.60,
                        "south": 45.46,
                        "east": -73.40,
                        "west": -73.60
                    }
                }
            }
        }


class RegionList(BaseModel):
    """List of regions."""
    regions: list[str] = Field(..., description="List of region codes")
    total: int = Field(..., description="Total number of regions")
