"""
Geocoding endpoints — proxy for Nominatim forward and reverse geocoding.
Frontend calls these instead of hitting Nominatim directly.
"""
from fastapi import APIRouter, Query, HTTPException
from app.services.geocoding import forward_geocode, reverse_geocode

router = APIRouter(prefix="/geocode", tags=["geocoding"])


@router.get("/forward")
async def geocode_forward(q: str = Query(..., description="Address string to geocode")):
    """
    Convert an address string to coordinates.

    Returns:
        { lat, lng, display_name }
    """
    result = await forward_geocode(q)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Address not found. Please try a more specific address.",
        )
    return result


@router.get("/reverse")
async def geocode_reverse(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
):
    """
    Convert coordinates to a human-readable address.

    Returns:
        { address }
    """
    address = await reverse_geocode(lat, lng)
    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Could not resolve address for the given coordinates.",
        )
    return {"address": address}