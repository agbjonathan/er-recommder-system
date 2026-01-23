"""
Database models for the ER Recommender System.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.session import Base


class Hospital(Base):
    """Hospital model for storing ER facility information."""
    
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, index=True)
    address = Column(String)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WaitTime(Base):
    """Wait time data for ER facilities."""
    
    __tablename__ = "wait_times"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, index=True)
    wait_time_minutes = Column(Integer)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String)  # data source identifier


class Forecast(Base):
    """Forecasted wait times and occupancy predictions."""
    
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, index=True)
    forecast_time = Column(DateTime(timezone=True), nullable=False)
    predicted_wait_minutes = Column(Float)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
