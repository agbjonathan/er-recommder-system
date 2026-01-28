"""
Database models for the ER Recommender System.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base import Base


class Hospital(Base):
    """Hospital model for storing ER facility information."""
    
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True)
    establishment = Column(String)
    name = Column(String, nullable=False)
    region = Column(String, index=True)
    permit_id = Column(String, unique=True, index=True, nullable=False)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ERSnapshot(Base):
    __tablename__ = "er_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "hospital_id",
            "snapshot_time",
            name="uq_er_snapshot_hospital_time"
        ),
    )

    id = Column(Integer, primary_key=True)
    hospital_id = Column(
        Integer,
        ForeignKey("hospitals.id"),
        index=True,
        nullable=False
    )

    functional_stretchers = Column(Integer, nullable=False)
    occupied_stretchers = Column(Integer, nullable=False)

    patients_total = Column(Integer, nullable=False)
    patients_waiting_mc = Column(Integer, nullable=False)

    patients_over_24h = Column(Integer, nullable=False)
    patients_over_48h = Column(Integer, nullable=False)

    avg_stay_stretcher = Column(Float)      
    avg_stay_ambulatory = Column(Float)     

    snapshot_time = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    



class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, index=True)

    horizon_hours = Column(Integer, nullable=False)  # 1, 3, 6
    predicted_pressure = Column(Float, nullable=False)

    lower_bound = Column(Float)
    upper_bound = Column(Float)

    forecast_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())



class ForecastError(Base):
    __tablename__ = "forecast_errors"

    id = Column(Integer, primary_key=True)
    forecast_id = Column(Integer, index=True)
    hospital_id = Column(Integer, index=True)

    observed_pressure = Column(Float, nullable=False)
    predicted_pressure = Column(Float, nullable=False)

    absolute_error = Column(Float, nullable=False)
    squared_error = Column(Float, nullable=False)

    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
