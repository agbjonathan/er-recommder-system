"""
Geocoding service — wraps Nominatim forward and reverse geocoding.
Isolates the third-party dependency so swapping providers only requires changes here.
"""
import httpx
from typing import Optional

NOMINATIM_BASE = "https://nominatim.openstreetmap.org"
HEADERS = {
    "User-Agent": "er-recommender/1.1.0 (contact: contact@jonathan-agba.com)",
    "Accept-Language": "en",
}


async def forward_geocode(query: str) -> Optional[dict]:
    """
    Convert an address string to coordinates.

    Args:
        query: Human-readable address string.

    Returns:
        dict with keys: lat (float), lng (float), display_name (str)
        or None if no result was found.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NOMINATIM_BASE}/search",
            params={
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "ca",  
            },
            headers=HEADERS,
            timeout=8.0,
        )
        response.raise_for_status()
        data = response.json()

    if not data:
        return None

    return {
        "lat": float(data[0]["lat"]),
        "lng": float(data[0]["lon"]),
        "display_name": data[0]["display_name"],
    }


async def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    """
    Convert coordinates to a human-readable address.

    Args:
        lat: Latitude.
        lng: Longitude.

    Returns:
        display_name string, or None if reverse geocoding failed.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NOMINATIM_BASE}/reverse",
            params={
                "lat": lat,
                "lon": lng,
                "format": "json",
            },
            headers=HEADERS,
            timeout=8.0,
        )
        response.raise_for_status()
        data = response.json()

    return data.get("display_name")