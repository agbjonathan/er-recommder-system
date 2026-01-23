"""
Routing service for calculating distances and travel times.
"""
import math
from typing import Dict, List, Tuple
from app.core.logging import logger


def calculate_haversine_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float
) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        float: Distance in kilometers
    """
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    return distance


def estimate_travel_time(distance_km: float, mode: str = "car") -> float:
    """
    Estimate travel time based on distance and transportation mode.
    
    Args:
        distance_km: Distance in kilometers
        mode: Transportation mode (car, public_transport, walk)
        
    Returns:
        float: Estimated travel time in minutes
    """
    # Average speeds in km/h
    speeds = {
        "car": 50.0,
        "public_transport": 30.0,
        "walk": 5.0
    }
    
    speed = speeds.get(mode, 50.0)
    time_hours = distance_km / speed
    time_minutes = time_hours * 60
    
    return time_minutes


def get_route_info(
    origin: Tuple[float, float],
    destination: Tuple[float, float]
) -> Dict:
    """
    Get routing information between two points.
    
    Args:
        origin: (latitude, longitude) of starting point
        destination: (latitude, longitude) of destination
        
    Returns:
        Dict: Route information including distance and travel time
    """
    distance = calculate_haversine_distance(
        origin[0], origin[1],
        destination[0], destination[1]
    )
    
    travel_time = estimate_travel_time(distance)
    
    return {
        "distance_km": round(distance, 2),
        "estimated_time_minutes": round(travel_time, 0),
        "mode": "car"
    }
