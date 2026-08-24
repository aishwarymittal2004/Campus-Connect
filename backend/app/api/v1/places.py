from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_places_service
from app.services.places_service import PlacesService

router = APIRouter(prefix="/places", tags=["Google Places"])

PlacesSvc = Annotated[PlacesService, Depends(get_places_service)]

@router.get("/nearby", response_model=list[dict[str, Any]])
async def get_nearby_places(
    places_service: PlacesSvc,
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(default=2000, description="Radius in meters"),
    keyword: str = Query(default="", description="Keyword to search, e.g., PG, Hostel, Hotel"),
    place_type: str = Query(default="", description="Type of place, e.g., restaurant, cafe"),
):
    """
    Search for nearby places using Google Places API.
    Used for finding PGs, Hostels, and Hotels around a specific location.
    """
    return await places_service.search_nearby(lat=lat, lng=lng, radius=radius, keyword=keyword, place_type=place_type)

@router.get("/food", response_model=list[dict[str, Any]])
async def get_nearby_food(
    places_service: PlacesSvc,
    lat: float = Query(...),
    lng: float = Query(...),
    radius: int = Query(default=3000, description="Radius in meters"),
    keyword: str = Query(default="", description="Specific food type, e.g., pizza, biryani"),
):
    """
    Search for nearby food places (restaurants, cafes) using Google Places API.
    """
    return await places_service.search_nearby(
        lat=lat, 
        lng=lng, 
        radius=radius, 
        keyword=keyword, 
        place_type="restaurant"
    )
