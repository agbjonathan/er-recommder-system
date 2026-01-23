"""
Risk assessment and overcrowding prediction.
"""
from typing import Dict, List
from datetime import datetime
from app.core.logging import logger


def assess_overcrowding_risk(
    current_wait_time: int,
    predicted_wait_time: int,
    capacity_threshold: int = 120
) -> Dict:
    """
    Assess the risk of ER overcrowding.
    
    Args:
        current_wait_time: Current wait time in minutes
        predicted_wait_time: Predicted wait time in minutes
        capacity_threshold: Wait time threshold indicating overcrowding
        
    Returns:
        Dict: Risk assessment with level and details
    """
    risk_levels = [
        ("low", 60, "green"),
        ("moderate", 90, "yellow"),
        ("high", 120, "orange"),
        ("critical", float("inf"), "red")
    ]
    
    max_wait = max(current_wait_time, predicted_wait_time)
    
    risk_level = "low"
    risk_color = "green"
    for level, threshold, color in risk_levels:
        if max_wait < threshold:
            risk_level = level
            risk_color = color
            break
    
    return {
        "risk_level": risk_level,
        "current_wait_minutes": current_wait_time,
        "predicted_wait_minutes": predicted_wait_time,
        "max_wait_minutes": max_wait,
        "color": risk_color,
        "is_overcrowded": max_wait >= capacity_threshold
    }


def calculate_risk_score(hospital_metrics: Dict) -> float:
    """
    Calculate a composite risk score for a hospital.
    
    Args:
        hospital_metrics: Dictionary of hospital metrics
        
    Returns:
        float: Risk score from 0 (low risk) to 100 (high risk)
    """
    wait_time = hospital_metrics.get("wait_time_minutes", 0)
    trend = hospital_metrics.get("trend", "stable")
    occupancy = hospital_metrics.get("occupancy_rate", 0.5)
    
    # Base score from wait time
    wait_score = min(wait_time / 2, 50)
    
    # Trend adjustment
    trend_adjustments = {
        "decreasing": -10,
        "stable": 0,
        "increasing": 10,
        "rapidly_increasing": 20
    }
    trend_score = trend_adjustments.get(trend, 0)
    
    # Occupancy score
    occupancy_score = occupancy * 30
    
    risk_score = wait_score + trend_score + occupancy_score
    return min(max(risk_score, 0), 100)


def predict_peak_times(historical_data: List[Dict]) -> List[Dict]:
    """
    Predict peak usage times for an ER.
    
    Args:
        historical_data: List of historical usage data points
        
    Returns:
        List[Dict]: Predicted peak time periods
    """
    # Placeholder implementation
    # In production, analyze patterns to identify peak times
    logger.info(f"Analyzing {len(historical_data)} historical records for peak times")
    
    return [
        {
            "day": "Monday",
            "start_hour": 18,
            "end_hour": 21,
            "average_wait": 90,
            "confidence": 0.85
        },
        {
            "day": "Friday",
            "start_hour": 19,
            "end_hour": 23,
            "average_wait": 105,
            "confidence": 0.80
        }
    ]
