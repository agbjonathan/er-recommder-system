import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("DISABLE_SCHEDULER", "true")
import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone, timedelta

from app.main import app
from app.db.base import Base
from app.db.session import get_db


SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSession = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_hospital(db):
    from app.db.models import Hospital
    h = Hospital(
        name="Hôpital Test",
        region="Montréal",
        permit_id=f"TEST-{uuid.uuid4().hex[:8]}",
        latitude=45.5,
        longitude=-73.6,
        is_active=True,
    )
    db.add(h)
    db.commit()
    db.refresh(h)
    return h


@pytest.fixture
def sample_forecast(db, sample_hospital):
    from app.db.models import Forecast
    now = datetime.now(timezone.utc)
    f = Forecast(
        hospital_id=sample_hospital.id,
        horizon_hours=1,
        predicted_pressure=0.80,
        risk_level="HIGH",
        forecast_time=now + timedelta(hours=1),
        evaluated=False,
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@pytest.fixture
def sample_forecast_error(db, sample_hospital, sample_forecast):
    from app.db.models import ForecastError
    now = datetime.now(timezone.utc)
    err = ForecastError(
        forecast_id=sample_forecast.id,
        hospital_id=sample_hospital.id,
        observed_pressure=0.78,
        predicted_pressure=0.80,
        absolute_error=0.02,
        squared_error=0.0004,
        horizon_hours=1,
        forecast_time=sample_forecast.forecast_time,
        evaluated_at=now,
    )
    db.add(err)
    db.commit()
    db.refresh(err)
    return err