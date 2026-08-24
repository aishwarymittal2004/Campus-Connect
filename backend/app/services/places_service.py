import httpx
from typing import Any

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class PlacesService:
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchNearby"

    async def search_nearby(self, lat: float, lng: float, radius: int = 2000, keyword: str = "", place_type: str = "") -> list[dict[str, Any]]:
        """
        Search for nearby places using New Google Places API.
        If no API key is set, returns an empty list.
        """
        if not self.api_key:
            logger.warning("Places API called but no GOOGLE_MAPS_API_KEY is set")
            return []

        # Convert radius to meters max 50000 for New API
        clamped_radius = float(min(radius, 50000))

        payload = {
            "maxResultCount": 1,
            "rankPreference": "DISTANCE",
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": clamped_radius
                }
            }
        }
        
        if place_type:
            payload["includedTypes"] = [place_type]
            
        # Note: New API doesn't support 'keyword' inside searchNearby easily without TextSearch, 
        # so we rely on includedPrimaryTypes or includedTypes. Airport and train_station work fine.

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.location,places.formattedAddress"
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for place in data.get("places", []):
                    # Map the New API response back to the expected legacy format for compatibility
                    results.append({
                        "name": place.get("displayName", {}).get("text", ""),
                        "formatted_address": place.get("formattedAddress", ""),
                        "geometry": {
                            "location": {
                                "lat": place.get("location", {}).get("latitude"),
                                "lng": place.get("location", {}).get("longitude")
                            }
                        }
                    })
                return results
        except Exception as exc:
            logger.error("places_api_error", error=str(exc))
            return []

    async def fetch_place_details(self, place_id: str) -> dict[str, Any]:
        """Fetch details (including reviews) for a specific place by place_id."""
        if not self.api_key:
            return {}
        
        url = f"https://places.googleapis.com/v1/places/{place_id}"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "id,displayName,reviews,formattedAddress,location"
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                return resp.json()
        except Exception as exc:
            logger.error("places_api_details_error", error=str(exc))
            return {}

    async def search_nearby_detailed(self, lat: float, lng: float, radius: int = 5000, place_types: list[str] = None, max_results: int = 5) -> list[dict[str, Any]]:
        """Search nearby places with custom types and max_results."""
        if not self.api_key:
            return []

        payload = {
            "maxResultCount": min(max_results, 20),
            "rankPreference": "DISTANCE",
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": float(min(radius, 50000))
                }
            }
        }
        
        if place_types:
            payload["includedTypes"] = place_types

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.location,places.formattedAddress"
        }

        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                
                results = []
                for place in data.get("places", []):
                    results.append({
                        "name": place.get("displayName", {}).get("text", ""),
                        "formatted_address": place.get("formattedAddress", ""),
                        "lat": place.get("location", {}).get("latitude"),
                        "lng": place.get("location", {}).get("longitude")
                    })
                return results
        except Exception as exc:
            logger.error("places_api_detailed_error", error=str(exc))
            return []
    async def get_nearest_train_station(self, lat: float, lng: float) -> str:
        """
        Uses the new Google Places API to find the nearest train station and returns its name.
        """
        if not self.api_key:
            return "Unknown Station"

        payload = {
            "maxResultCount": 1,
            "rankPreference": "DISTANCE",
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": lat,
                        "longitude": lng
                    },
                    "radius": 50000.0
                }
            },
            "includedTypes": ["train_station"]
        }

        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName"
        }

        try:
            import httpx
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.post(self.base_url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                places = data.get("places", [])
                if places:
                    name = places[0].get("displayName", {}).get("text", "Unknown Station")
                    # Clean up common suffixes for API searching
                    name = name.replace(" Railway Station", "").replace(" Junction", "").replace(" Station", "")
                    return name
        except Exception as exc:
            logger.error("nearest_train_station_error", error=str(exc))
        return "Unknown Station"
