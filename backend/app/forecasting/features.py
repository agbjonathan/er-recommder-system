"""
Feature engineering for forecasting models.
"""
from typing import List, Dict, Any
from datetime import datetime
import math


def extract_temporal_features(timestamp: datetime) -> Dict[str, Any]:
    """
    Extract temporal features from a timestamp.
    
    Args:
        timestamp: Datetime object
        
    Returns:
        Dict[str, Any]: Dictionary of temporal features
    """
    return {
        "hour": timestamp.hour,
        "day_of_week": timestamp.weekday(),
        "day_of_month": timestamp.day,
        "month": timestamp.month,
        "is_weekend": timestamp.weekday() >= 5,
        "is_business_hours": 8 <= timestamp.hour <= 17,
        "quarter": (timestamp.month - 1) // 3 + 1
    }


def create_lag_features(
    values: List[float],
    lags: List[int]
) -> Dict[str, List[float]]:
    """
    Create lagged features for time series data.
    
    Args:
        values: Time series values
        lags: List of lag periods to create
        
    Returns:
        Dict[str, List[float]]: Dictionary of lagged features
    """
    features = {}
    
    for lag in lags:
        lag_values = [None] * lag + values[:-lag] if lag < len(values) else [None] * len(values)
        features[f"lag_{lag}"] = lag_values
    
    return features


def calculate_rolling_statistics(
    values: List[float],
    window: int
) -> Dict[str, List[float]]:
    """
    Calculate rolling statistics for time series.
    
    Args:
        values: Time series values
        window: Window size for rolling calculations
        
    Returns:
        Dict[str, List[float]]: Rolling statistics (mean, std, min, max)
    """
    rolling_mean = []
    rolling_std = []
    rolling_min = []
    rolling_max = []
    
    for i in range(len(values)):
        if i < window - 1:
            rolling_mean.append(None)
            rolling_std.append(None)
            rolling_min.append(None)
            rolling_max.append(None)
        else:
            window_values = values[i - window + 1:i + 1]
            rolling_mean.append(sum(window_values) / len(window_values))
            
            mean = rolling_mean[-1]
            variance = sum((x - mean) ** 2 for x in window_values) / len(window_values)
            rolling_std.append(math.sqrt(variance))
            
            rolling_min.append(min(window_values))
            rolling_max.append(max(window_values))
    
    return {
        "rolling_mean": rolling_mean,
        "rolling_std": rolling_std,
        "rolling_min": rolling_min,
        "rolling_max": rolling_max
    }
