import uuid

import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.exc import IntegrityError

from app.db.models import Hospital, Forecast, ForecastError


# ── Hospital ──────────────────────────────────────────────────────────────────

def test_hospital_creation(db):
    h = Hospital(
        name="Test Hospital",
        region="Québec",
        permit_id=f"T-{uuid.uuid4().hex[:8]}",
        latitude=46.8,
        longitude=-71.2,
        is_active=True,
    )
    db.add(h)
    db.commit()
    assert h.id is not None


def test_inactive_hospital_can_be_created(db):
    h = Hospital(
        name="Closed Hospital",
        region="Québec",
        permit_id=f"T-{uuid.uuid4().hex[:8]}",
        latitude=46.0,
        longitude=-72.0,
        is_active=False,
    )
    db.add(h)
    db.commit()
    assert h.id is not None
    assert h.is_active is False


# ── Forecast ──────────────────────────────────────────────────────────────────

def test_forecast_creation(db, sample_hospital):
    now = datetime.now(timezone.utc)
    f = Forecast(
        hospital_id=sample_hospital.id,
        horizon_hours=1,
        predicted_pressure=0.65,
        risk_level="MEDIUM",
        forecast_time=now + timedelta(hours=1),
        evaluated=False,
    )
    db.add(f)
    db.commit()
    assert f.id is not None


def test_forecast_unique_constraint_prevents_duplicate(db, sample_forecast):
    duplicate = Forecast(
        hospital_id=sample_forecast.hospital_id,
        horizon_hours=sample_forecast.horizon_hours,
        predicted_pressure=0.5,
        risk_level="LOW",
        forecast_time=sample_forecast.forecast_time,
    )
    db.add(duplicate)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_different_horizon_same_time_allowed(db, sample_hospital, sample_forecast):
    """Same hospital and time but different horizon should be allowed."""
    f2 = Forecast(
        hospital_id=sample_hospital.id,
        horizon_hours=4,  # different horizon
        predicted_pressure=0.70,
        risk_level="HIGH",
        forecast_time=sample_forecast.forecast_time,
    )
    db.add(f2)
    db.commit()
    assert f2.id is not None


def test_different_time_same_horizon_allowed(db, sample_hospital, sample_forecast):
    f2 = Forecast(
        hospital_id=sample_hospital.id,
        horizon_hours=1,
        predicted_pressure=0.60,
        risk_level="MEDIUM",
        forecast_time=sample_forecast.forecast_time + timedelta(hours=1),
    )
    db.add(f2)
    db.commit()
    assert f2.id is not None


# ── ForecastError ─────────────────────────────────────────────────────────────

def test_forecast_error_creation(db, sample_hospital, sample_forecast):
    now = datetime.now(timezone.utc)
    err = ForecastError(
        forecast_id=sample_forecast.id,
        hospital_id=sample_hospital.id,
        observed_pressure=0.75,
        predicted_pressure=0.80,
        absolute_error=0.05,
        squared_error=0.0025,
        horizon_hours=1,
        forecast_time=sample_forecast.forecast_time,
        evaluated_at=now,
    )
    db.add(err)
    db.commit()
    assert err.id is not None


def test_forecast_error_absolute_error_is_correct(db, sample_hospital, sample_forecast):
    now = datetime.now(timezone.utc)
    observed = 0.72
    predicted = 0.80
    err = ForecastError(
        forecast_id=sample_forecast.id,
        hospital_id=sample_hospital.id,
        observed_pressure=observed,
        predicted_pressure=predicted,
        absolute_error=abs(predicted - observed),
        squared_error=(predicted - observed) ** 2,
        horizon_hours=1,
        forecast_time=sample_forecast.forecast_time,
        evaluated_at=now,
    )
    db.add(err)
    db.commit()
    assert round(err.absolute_error, 4) == round(abs(predicted - observed), 4)