"""
Routing engine abstraction.

Campus Connect needs multi-modal route estimates (metro / bus / cab / auto /
walk / mixed) between an arrival point (station/airport/bus stand) and a
college. There is no single API that returns all of these modes with cost
estimates for Indian cities, so this module:

  1. Uses Google Distance Matrix / Directions API (if GOOGLE_MAPS_API_KEY is
     configured) to get real distance & duration for driving/walking/transit.
  2. Falls back to a haversine-distance heuristic estimator otherwise, so the
     app is fully functional in local/dev environments without any API key.
  3. Applies mode-specific cost/time heuristics (typical Indian urban
     auto/cab fare slabs, metro fare bands, bus fare bands) on top of
     whichever distance source was used, since none of the transit APIs
     return fare estimates for autos/shared modes.

Swap `HeuristicRoutingProvider` for a real provider (Google/Ola/Uber/ONDC
Mobility) by implementing `RoutingProvider` and wiring it in `get_routing_engine()`.
"""
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import httpx

from app.core.config import settings
from app.core.logging_config import get_logger
from app.models.route import TransportType

logger = get_logger(__name__)


@dataclass
class DistanceResult:
    distance_km: float
    duration_minutes: float
    polyline: str | None = None
    source: str = "heuristic"


class RoutingProvider(ABC):
    @abstractmethod
    async def get_distance(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> DistanceResult:
        ...

    @abstractmethod
    async def get_directions(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> dict | None:
        ...

    @abstractmethod
    async def geocode(self, address: str) -> tuple[float, float] | None:
        ...


def haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class HeuristicRoutingProvider(RoutingProvider):
    """Zero-dependency fallback. Straight-line distance * a road-network detour factor."""

    DETOUR_FACTOR = 1.35  # real road distance is typically ~1.2-1.5x straight-line in Indian cities
    AVG_SPEED_KMH = {
        "driving": 22,
        "walking": 4.5,
        "transit": 28,
    }

    async def get_distance(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> DistanceResult:
        straight_line = haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)
        road_distance = straight_line if mode == "walking" else straight_line * self.DETOUR_FACTOR
        speed = self.AVG_SPEED_KMH.get(mode, self.AVG_SPEED_KMH["driving"])
        duration_minutes = (road_distance / speed) * 60
        return DistanceResult(distance_km=round(road_distance, 2), duration_minutes=round(duration_minutes, 1))

    async def get_directions(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> dict | None:
        return None  # Fallback does not provide turn-by-turn directions

    async def geocode(self, address: str) -> tuple[float, float] | None:
        return None  # Fallback does not provide geocoding


class GoogleRoutingProvider(RoutingProvider):
    """Real Google Distance Matrix API - used automatically once GOOGLE_MAPS_API_KEY is set."""

    BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._fallback = HeuristicRoutingProvider()

    async def get_distance(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> DistanceResult:
        params = {
            "origins": f"{origin_lat},{origin_lng}",
            "destinations": f"{dest_lat},{dest_lng}",
            "mode": mode,
            "key": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                data = resp.json()
                element = data["rows"][0]["elements"][0]
                if element["status"] != "OK":
                    raise ValueError(f"Distance Matrix element status: {element['status']}")
                distance_km = element["distance"]["value"] / 1000
                duration_minutes = element["duration"]["value"] / 60
                return DistanceResult(
                    distance_km=round(distance_km, 2),
                    duration_minutes=round(duration_minutes, 1),
                    source="google",
                )
        except Exception as exc:  # network error, quota, malformed response, etc.
            logger.warning("google_distance_matrix_failed", error=str(exc), mode=mode)
            return await self._fallback.get_distance(origin_lat, origin_lng, dest_lat, dest_lng, mode)

    async def get_directions(
        self, origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, mode: str
    ) -> dict | None:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": f"{origin_lat},{origin_lng}",
            "destination": f"{dest_lat},{dest_lng}",
            "mode": mode,
            "key": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "OK" and data.get("routes"):
                    return data["routes"][0]
        except Exception as exc:
            logger.warning("google_directions_failed", error=str(exc), mode=mode)
        return await self._fallback.get_directions(origin_lat, origin_lng, dest_lat, dest_lng, mode)

    async def geocode(self, address: str) -> tuple[float, float] | None:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "OK" and data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    return location["lat"], location["lng"]
        except Exception as exc:
            logger.warning("google_geocoding_failed", error=str(exc), address=address)
        return await self._fallback.geocode(address)


# --- Mode-specific cost heuristics (INR), tuned for tier-1/2 Indian cities ---
# These are intentionally simple, transparent slab formulas so the numbers
# shown to students are explainable and easy to recalibrate per-city later.

def estimate_metro(distance_km: float) -> tuple[float, float]:
    duration = (distance_km / 33) * 60 + 8  # ~33 km/h average incl. dwell time, +8 min buffer for boarding
    if distance_km <= 2:
        fare = 10
    elif distance_km <= 5:
        fare = 20
    elif distance_km <= 12:
        fare = 30
    elif distance_km <= 21:
        fare = 40
    else:
        fare = 60
    return round(duration, 1), float(fare)


def estimate_bus(distance_km: float) -> tuple[float, float]:
    duration = (distance_km / 18) * 60 + 5
    fare = max(10, round(distance_km * 1.5))
    return round(duration, 1), float(fare)


def estimate_cab(distance_km: float, duration_minutes: float) -> float:
    base_fare = 60
    per_km = 13
    per_min = 1.5
    return round(base_fare + distance_km * per_km + duration_minutes * per_min)


def estimate_auto(distance_km: float) -> float:
    base_fare = 30
    per_km = 17
    return round(base_fare + max(0, distance_km - 1.5) * per_km)


def get_routing_engine() -> RoutingProvider:
    if settings.GOOGLE_MAPS_API_KEY:
        return GoogleRoutingProvider(settings.GOOGLE_MAPS_API_KEY)
    return HeuristicRoutingProvider()
