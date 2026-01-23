"""
Hospital schema definitions for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HospitalBase(BaseModel):
    """Base hospital schema."""
    name: str = Field(..., description="Hospital name")
    region: str = Field(..., description="Region name")
    address: Optional[str] = Field(None, description="Street address")
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    phone: Optional[str] = Field(None, description="Contact phone number")


class HospitalCreate(HospitalBase):
    """Schema for creating a new hospital."""
    pass


class HospitalUpdate(BaseModel):
    """Schema for updating hospital information."""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class Hospital(HospitalBase):
    """Complete hospital schema with database fields."""
    id: int = Field(..., description="Hospital ID")
    is_active: bool = Field(True, description="Whether hospital is active")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HospitalWithWaitTime(Hospital):
    """Hospital schema with current wait time."""
    current_wait_minutes: Optional[int] = Field(None, description="Current wait time in minutes")
    distance_km: Optional[float] = Field(None, description="Distance from user in kilometers")
    estimated_travel_minutes: Optional[float] = Field(None, description="Estimated travel time")


class HospitalList(BaseModel):
    """Response schema for hospital list."""
    hospitals: List[Hospital]
    total: int
    skip: int
    limit: int
