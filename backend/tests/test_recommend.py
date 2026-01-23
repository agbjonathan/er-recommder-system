"""
Tests for recommendation functionality.
"""
import pytest
from app.services.scoring import calculate_hospital_score, rank_hospitals, apply_filters


class TestRecommendations:
    """Test cases for hospital recommendations."""
    
    def test_calculate_hospital_score_moderate_severity(self):
        """Test score calculation with moderate severity."""
        score = calculate_hospital_score(
            distance_km=5.0,
            wait_time_minutes=60,
            severity="moderate"
        )
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_calculate_hospital_score_critical_severity(self):
        """Test that critical severity prioritizes wait time."""
        score_critical = calculate_hospital_score(
            distance_km=10.0,
            wait_time_minutes=30,
            severity="critical"
        )
        score_low = calculate_hospital_score(
            distance_km=10.0,
            wait_time_minutes=30,
            severity="low"
        )
        # With same parameters but different severity, scores should differ
        assert score_critical != score_low
    
    def test_rank_hospitals(self):
        """Test hospital ranking by score."""
        hospitals = [
            {"name": "Hospital A", "score": 80},
            {"name": "Hospital B", "score": 95},
            {"name": "Hospital C", "score": 70}
        ]
        ranked = rank_hospitals(hospitals)
        assert ranked[0]["name"] == "Hospital B"
        assert ranked[1]["name"] == "Hospital A"
        assert ranked[2]["name"] == "Hospital C"
    
    def test_apply_filters_distance(self):
        """Test filtering by maximum distance."""
        hospitals = [
            {"name": "Close Hospital", "distance_km": 3.0},
            {"name": "Far Hospital", "distance_km": 15.0}
        ]
        filtered = apply_filters(hospitals, max_distance=10.0)
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Close Hospital"
    
    def test_apply_filters_wait_time(self):
        """Test filtering by maximum wait time."""
        hospitals = [
            {"name": "Short Wait", "wait_time_minutes": 30},
            {"name": "Long Wait", "wait_time_minutes": 120}
        ]
        filtered = apply_filters(hospitals, max_wait_time=60)
        assert len(filtered) == 1
        assert filtered[0]["name"] == "Short Wait"
