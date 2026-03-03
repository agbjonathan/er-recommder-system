import pytest
import pandas as pd
from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from app.services.forecast_service import train_and_forecast


def make_mock_df(hospital_id: int = 1, n: int = 24) -> pd.DataFrame:
    """Build a realistic mock dataset for a single hospital."""
    now = datetime.now(timezone.utc)
    times = [now - timedelta(hours=i) for i in range(n - 1, -1, -1)]
    return pd.DataFrame({
        "hospital_id": [hospital_id] * n,
        "snapshot_time": times,
        "pressure_score": [0.55 + (i % 5) * 0.04 for i in range(n)],
        "true_latest_snapshot_time": [times[-1]] * n,  # most recent = last
    })


def make_multi_hospital_df(n_hospitals: int = 3, n: int = 24) -> pd.DataFrame:
    return pd.concat(
        [make_mock_df(hospital_id=i, n=n) for i in range(1, n_hospitals + 1)],
        ignore_index=True,
    )


# ── forecast_time correctness ─────────────────────────────────────────────────

def test_forecast_time_is_in_future(db):
    with patch("app.services.forecast_service.build_ml_dataset", return_value=make_mock_df()):
        results = train_and_forecast(db, horizon_hours=1)
    now = datetime.now(timezone.utc)
    for r in results:
        assert r["forecast_time"] > now, (
            f"forecast_time {r['forecast_time']} should be in the future"
        )


def test_forecast_time_offset_matches_horizon(db):
    """forecast_time should be approximately latest_snapshot + horizon_hours."""
    df = make_mock_df(n=24)
    latest = df["true_latest_snapshot_time"].iloc[-1]

    with patch("app.services.forecast_service.build_ml_dataset", return_value=df):
        results = train_and_forecast(db, horizon_hours=1)

    assert len(results) == 1
    expected = latest + timedelta(hours=1)
    diff = abs((results[0]["forecast_time"] - expected).total_seconds())
    assert diff < 60, f"forecast_time offset is off by {diff}s"


def test_forecast_time_respects_horizon_4h(db):
    df = make_mock_df(n=24)
    latest = df["true_latest_snapshot_time"].iloc[-1]

    with patch("app.services.forecast_service.build_ml_dataset", return_value=df):
        results = train_and_forecast(db, horizon_hours=4)

    assert len(results) == 1
    expected = latest + timedelta(hours=4)
    diff = abs((results[0]["forecast_time"] - expected).total_seconds())
    assert diff < 60


# ── output structure ──────────────────────────────────────────────────────────

def test_forecast_has_required_keys(db):
    with patch("app.services.forecast_service.build_ml_dataset", return_value=make_mock_df()):
        results = train_and_forecast(db, horizon_hours=1)

    assert len(results) > 0
    required = {"hospital_id", "predicted_pressure", "forecast_time", "horizon_hours", "risk_level"}
    for r in results:
        assert required.issubset(r.keys()), f"Missing keys: {required - r.keys()}"


def test_risk_level_is_valid(db):
    with patch("app.services.forecast_service.build_ml_dataset", return_value=make_mock_df()):
        results = train_and_forecast(db, horizon_hours=1)
    for r in results:
        assert r["risk_level"] in ("LOW", "MEDIUM", "HIGH")


def test_predicted_pressure_is_float(db):
    with patch("app.services.forecast_service.build_ml_dataset", return_value=make_mock_df()):
        results = train_and_forecast(db, horizon_hours=1)
    for r in results:
        assert isinstance(r["predicted_pressure"], float)


def test_horizon_hours_stored_correctly(db):
    with patch("app.services.forecast_service.build_ml_dataset", return_value=make_mock_df()):
        results = train_and_forecast(db, horizon_hours=2)
    for r in results:
        assert r["horizon_hours"] == 2


# ── edge cases ────────────────────────────────────────────────────────────────

def test_skips_hospitals_with_insufficient_data(db):
    small_df = make_mock_df(n=5)  # below threshold of 10
    with patch("app.services.forecast_service.build_ml_dataset", return_value=small_df):
        results = train_and_forecast(db, horizon_hours=1)
    assert results == []


def test_handles_multiple_hospitals(db):
    df = make_multi_hospital_df(n_hospitals=3, n=24)
    with patch("app.services.forecast_service.build_ml_dataset", return_value=df):
        results = train_and_forecast(db, horizon_hours=1)
    assert len(results) == 3
    hospital_ids = {r["hospital_id"] for r in results}
    assert hospital_ids == {1, 2, 3}


def test_empty_dataset_returns_empty_list(db):
    empty_df = pd.DataFrame(columns=[
        "hospital_id", "snapshot_time", "pressure_score", "true_latest_snapshot_time"
    ])
    with patch("app.services.forecast_service.build_ml_dataset", return_value=empty_df):
        results = train_and_forecast(db, horizon_hours=1)
    assert results == []