"""
Longueuil region configuration and hospital data.
"""
from typing import List, Dict

# Longueuil region configuration
REGION_CONFIG = {
    "name": "Longueuil",
    "code": "LNG",
    "timezone": "America/Montreal",
    "coordinates": {
        "center": {"latitude": 45.5312, "longitude": -73.5185},
        "bounds": {
            "north": 45.60,
            "south": 45.46,
            "east": -73.40,
            "west": -73.60
        }
    }
}


def get_longueuil_hospitals() -> List[Dict]:
    """
    Get list of hospitals in the Longueuil region.
    
    Returns:
        List[Dict]: List of hospital data
    """
    # Placeholder data
    # In production, load from database or configuration
    return [
        {
            "name": "Hôpital Charles-Le Moyne",
            "address": "3120 Boulevard Taschereau, Greenfield Park",
            "latitude": 45.4968,
            "longitude": -73.4633,
            "region": "Longueuil",
            "phone": "+1-450-466-5000",
            "services": ["emergency", "trauma", "pediatric"]
        },
        {
            "name": "Centre hospitalier Pierre-Boucher",
            "address": "1333 Boulevard Jacques-Cartier Est, Longueuil",
            "latitude": 45.5378,
            "longitude": -73.4510,
            "region": "Longueuil",
            "phone": "+1-450-468-8111",
            "services": ["emergency", "general"]
        }
    ]


def is_within_longueuil_region(latitude: float, longitude: float) -> bool:
    """
    Check if coordinates are within the Longueuil region.
    
    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        
    Returns:
        bool: True if within region bounds
    """
    bounds = REGION_CONFIG["coordinates"]["bounds"]
    return (
        bounds["south"] <= latitude <= bounds["north"] and
        bounds["west"] <= longitude <= bounds["east"]
    )
