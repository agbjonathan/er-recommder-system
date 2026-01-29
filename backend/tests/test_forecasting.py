"""
Tests for forecasting functionality.
"""
import pytest
from app.ml.arima import ARIMAForecaster, auto_arima
from app.ml.risk import assess_overcrowding_risk, calculate_risk_score
from backend.app.ml.features.feature_builder import extract_temporal_features
from datetime import datetime


class TestARIMA:
    """Test cases for ARIMA forecasting."""
    
    def test_arima_initialization(self):
        """Test ARIMA model initialization."""
        forecaster = ARIMAForecaster(order=(1, 1, 1))
        assert forecaster.order == (1, 1, 1)
        assert not forecaster.is_fitted
    
    def test_arima_fit(self):
        """Test ARIMA model fitting."""
        forecaster = ARIMAForecaster()
        data = [60, 65, 70, 68, 72, 75, 80]
        forecaster.fit(data)
        assert forecaster.is_fitted
    
    def test_arima_forecast(self):
        """Test ARIMA forecast generation."""
        forecaster = ARIMAForecaster()
        data = [60, 65, 70, 68, 72, 75, 80]
        forecaster.fit(data)
        
        forecast = forecaster.forecast(steps=3)
        assert "forecast" in forecast
        assert "lower_bound" in forecast
        assert "upper_bound" in forecast
        assert len(forecast["forecast"]) == 3
    
    def test_auto_arima(self):
        """Test automatic ARIMA parameter selection."""
        data = [60, 65, 70, 68, 72, 75, 80]
        forecaster = auto_arima(data)
        assert forecaster.is_fitted


class TestRiskAssessment:
    """Test cases for risk assessment."""
    
    def test_assess_low_risk(self):
        """Test low overcrowding risk assessment."""
        risk = assess_overcrowding_risk(
            current_wait_time=30,
            predicted_wait_time=35
        )
        assert risk["risk_level"] == "low"
        assert not risk["is_overcrowded"]
    
    def test_assess_high_risk(self):
        """Test high overcrowding risk assessment."""
        risk = assess_overcrowding_risk(
            current_wait_time=90,
            predicted_wait_time=95
        )
        assert risk["risk_level"] in ["high", "moderate"]
    
    def test_calculate_risk_score(self):
        """Test risk score calculation."""
        metrics = {
            "wait_time_minutes": 90,
            "trend": "increasing",
            "occupancy_rate": 0.8
        }
        score = calculate_risk_score(metrics)
        assert 0 <= score <= 100


class TestFeatureEngineering:
    """Test cases for feature engineering."""
    
    def test_extract_temporal_features(self):
        """Test temporal feature extraction."""
        dt = datetime(2024, 1, 15, 14, 30)  # Monday, 2:30 PM
        features = extract_temporal_features(dt)
        
        assert features["hour"] == 14
        assert features["day_of_week"] == 0  # Monday
        assert features["month"] == 1
        assert not features["is_weekend"]
        assert features["is_business_hours"]
