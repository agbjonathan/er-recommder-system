"""
Scoring service for ranking and recommending hospitals.
"""
from typing import List, Dict, Any
from app.core.logging import logger


def calculate_hospital_score(
    distance_km: float,
    wait_time_minutes: int,
    severity: str = "moderate"
) -> float:
    """
    Calculate a composite score for hospital recommendation.
    
    Args:
        distance_km: Distance to hospital in kilometers
        wait_time_minutes: Current or predicted wait time
        severity: Medical severity level (low, moderate, high, critical)
        
    Returns:
        float: Composite score (higher is better)
    """
    # Weights based on severity
    severity_weights = {
        "low": {"distance": 0.7, "wait_time": 0.3},
        "moderate": {"distance": 0.5, "wait_time": 0.5},
        "high": {"distance": 0.3, "wait_time": 0.7},
        "critical": {"distance": 0.2, "wait_time": 0.8}
    }
    
    weights = severity_weights.get(severity, severity_weights["moderate"])
    
    # Normalize distance (inverse scoring - closer is better)
    distance_score = max(0, 100 - (distance_km * 5))
    
    # Normalize wait time (inverse scoring - shorter is better)
    wait_time_score = max(0, 100 - (wait_time_minutes * 0.5))
    
    # Calculate weighted score
    composite_score = (
        distance_score * weights["distance"] +
        wait_time_score * weights["wait_time"]
    )
    
    return round(composite_score, 2)


def rank_hospitals(hospitals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank hospitals by their recommendation scores.
    
    Args:
        hospitals: List of hospital data with scores
        
    Returns:
        List[Dict[str, Any]]: Sorted list of hospitals (best first)
    """
    return sorted(
        hospitals,
        key=lambda h: h.get("score", 0),
        reverse=True
    )


def apply_filters(
    hospitals: List[Dict[str, Any]],
    max_distance: float = None,
    max_wait_time: int = None
) -> List[Dict[str, Any]]:
    """
    Filter hospitals based on criteria.
    
    Args:
        hospitals: List of hospital data
        max_distance: Maximum acceptable distance in km
        max_wait_time: Maximum acceptable wait time in minutes
        
    Returns:
        List[Dict[str, Any]]: Filtered list of hospitals
    """
    filtered = hospitals.copy()
    
    if max_distance is not None:
        filtered = [h for h in filtered if h.get("distance_km", float("inf")) <= max_distance]
    
    if max_wait_time is not None:
        filtered = [h for h in filtered if h.get("wait_time_minutes", float("inf")) <= max_wait_time]
    
    logger.info(f"Filtered {len(hospitals)} hospitals to {len(filtered)} results")
    return filtered
