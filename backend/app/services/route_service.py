import hashlib
import uuid

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.core.logging_config import get_logger
from app.core.redis_client import RedisCache
from app.models.route import RouteQuery, TransportType
from app.repositories.college_repository import CollegeRepository
from app.repositories.route_repository import RouteRepository
from app.schemas.route import RouteOption, RouteSearchRequest, RouteSearchResponse, RouteStep
from app.services import routing_engine as engine

logger = get_logger(__name__)


class RouteService:
    def __init__(self, route_repo: RouteRepository, college_repo: CollegeRepository, cache: RedisCache):
        self.route_repo = route_repo
        self.college_repo = college_repo
        self.cache = cache

    @staticmethod
    def _cache_key(payload: RouteSearchRequest) -> str:
        raw = f"{payload.source_location}|{payload.source_type}|{payload.college_id}|{payload.source_latitude}|{payload.source_longitude}"
        return "route_search:" + hashlib.sha256(raw.encode()).hexdigest()

    async def search_routes(self, user_id: uuid.UUID, payload: RouteSearchRequest) -> RouteSearchResponse:
        college = await self.college_repo.get_by_id(payload.college_id)
        if not college:
            raise NotFoundError("College not found.")

        cache_key = self._cache_key(payload)
        cached = await self.cache.get_json(cache_key)
        if cached:
            logger.info("route_search_cache_hit", cache_key=cache_key)
            options = [RouteOption(**opt) for opt in cached]
        else:
            options = await self._compute_routes(payload, college)
            await self.cache.set_json(cache_key, [opt.model_dump(mode="json") for opt in options], ttl=1800)

        # Persist this search to the user's route history regardless of cache hit
        rows = [
            {
                "user_id": user_id,
                "college_id": college.id,
                "source_location": payload.source_location,
                "source_type": payload.source_type,
                "source_latitude": payload.source_latitude,
                "source_longitude": payload.source_longitude,
                "transport_type": opt.transport_type,
                "distance_km": opt.distance_km,
                "duration_minutes": opt.duration_minutes,
                "estimated_cost_inr": opt.estimated_cost_inr,
                "steps": [s.model_dump() for s in opt.steps],
                "polyline": opt.polyline,
            }
            for opt in options
        ]
        saved_rows = await self.route_repo.bulk_create(rows)
        for opt, saved in zip(options, saved_rows):
            opt.id = saved.id

        return RouteSearchResponse(
            source_location=payload.source_location,
            college_id=college.id,
            college_name=college.name,
            options=options,
        )

    async def _compute_routes(self, payload: RouteSearchRequest, college) -> list[RouteOption]:
        provider = engine.get_routing_engine()

        origin_lat = payload.source_latitude
        origin_lng = payload.source_longitude
        # If the frontend didn't resolve precise coordinates (e.g. Places Autocomplete
        # unavailable without a Maps key), use the routing provider to geocode it.
        # Fall back to free Nominatim API, and then to college centroid offset if all geocoding fails.
        if origin_lat is None or origin_lng is None:
            coords = await provider.geocode(payload.source_location)
            if coords:
                origin_lat, origin_lng = coords
            else:
                import httpx
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        resp = await client.get(
                            "https://nominatim.openstreetmap.org/search",
                            params={"q": payload.source_location + ", India", "format": "json", "limit": 1},
                            headers={"User-Agent": "CampusConnectApp/1.0"}
                        )
                        if resp.status_code == 200 and resp.json():
                            origin_lat = float(resp.json()[0]["lat"])
                            origin_lng = float(resp.json()[0]["lon"])
                        else:
                            origin_lat, origin_lng = college.latitude + 0.05, college.longitude + 0.05
                except Exception:
                    origin_lat, origin_lng = college.latitude + 0.05, college.longitude + 0.05

        driving = await provider.get_distance(origin_lat, origin_lng, college.latitude, college.longitude, "driving")
        walking = await provider.get_distance(origin_lat, origin_lng, college.latitude, college.longitude, "walking")
        transit = await provider.get_distance(origin_lat, origin_lng, college.latitude, college.longitude, "transit")

        options: list[RouteOption] = []
        is_intercity = driving.distance_km > 60

        # --- Metro (Local only) ---
        if not is_intercity and transit.distance_km < 60:
            metro_duration, metro_fare = engine.estimate_metro(transit.distance_km)
            options.append(
                RouteOption(
                    transport_type=TransportType.METRO,
                    distance_km=transit.distance_km,
                    duration_minutes=metro_duration,
                    estimated_cost_inr=metro_fare,
                    steps=[
                        RouteStep(instruction=f"Walk to the nearest metro station from {payload.source_location}.", duration_minutes=8),
                        RouteStep(instruction=f"Take the metro towards {college.name} area ({transit.distance_km} km).", distance_km=transit.distance_km, duration_minutes=metro_duration - 15),
                        RouteStep(instruction=f"Walk/auto from the nearest metro station to {college.name}.", duration_minutes=7),
                    ],
                    polyline=transit.polyline,
                )
            )

        # --- Bus ---
        if is_intercity:
            # Intercity Bus
            bus_duration = round((transit.distance_km / 45) * 60)
            bus_fare = max(150.0, round(transit.distance_km * 1.8))
            options.append(
                RouteOption(
                    transport_type=TransportType.BUS,
                    distance_km=transit.distance_km,
                    duration_minutes=bus_duration,
                    estimated_cost_inr=bus_fare,
                    steps=[
                        RouteStep(instruction=f"Board an intercity/state transport bus near {payload.source_location}.", duration_minutes=15),
                        RouteStep(instruction=f"Intercity travel to {college.city} ({transit.distance_km} km).", distance_km=transit.distance_km, duration_minutes=bus_duration - 30),
                        RouteStep(instruction=f"Alight at the bus stand and take local transport to {college.name}.", duration_minutes=15),
                    ],
                )
            )
        else:
            # Local City Bus
            bus_duration, bus_fare = engine.estimate_bus(transit.distance_km)
            options.append(
                RouteOption(
                    transport_type=TransportType.BUS,
                    distance_km=transit.distance_km,
                    duration_minutes=bus_duration,
                    estimated_cost_inr=bus_fare,
                    steps=[
                        RouteStep(instruction=f"Board a city bus near {payload.source_location}.", duration_minutes=5),
                        RouteStep(instruction=f"Ride towards {college.name} ({transit.distance_km} km).", distance_km=transit.distance_km, duration_minutes=bus_duration - 10),
                        RouteStep(instruction=f"Alight and walk to {college.name} campus gate.", duration_minutes=5),
                    ],
                )
            )

        # --- Cab (Available both local and intercity) ---
        cab_cost = engine.estimate_cab(driving.distance_km, driving.duration_minutes)
        if is_intercity:
            cab_cost = round(driving.distance_km * 11 + 250) # Intercity cab estimate
            
        options.append(
            RouteOption(
                transport_type=TransportType.CAB,
                distance_km=driving.distance_km,
                duration_minutes=driving.duration_minutes,
                estimated_cost_inr=cab_cost,
                steps=[
                    RouteStep(instruction=f"Book a cab from {payload.source_location}.", duration_minutes=10),
                    RouteStep(instruction=f"Direct drive to {college.name} ({driving.distance_km} km).", distance_km=driving.distance_km, duration_minutes=driving.duration_minutes),
                ],
                polyline=driving.polyline,
            )
        )

        # --- Train ---
        if is_intercity:
            # Attempt to find actual real-world stations
            from app.services.places_service import PlacesService
            from app.services.train_api_service import TrainAPIService
            places = PlacesService()
            train_api = TrainAPIService()
            
            origin_station = await places.get_nearest_train_station(origin_lat, origin_lng)
            if origin_station == "Unknown Station":
                origin_station = "nearest major Railway Station"
                
            dest_station = await places.get_nearest_train_station(college.latitude, college.longitude)
            if dest_station == "Unknown Station":
                dest_station = f"{college.city} station"

            train_duration = (driving.distance_km / 65) * 60 + 45 # 65km/h avg + 45m buffer
            train_fare = round(driving.distance_km * 2.5) # Sleeper/3AC approx
            
            # Use RapidAPI Train Service to compute connecting route
            train_steps = await train_api.get_train_route(
                origin_station, origin_lat, origin_lng,
                dest_station, college.latitude, college.longitude,
                driving.distance_km
            )
            
            if not train_steps:
                train_steps = [
                    RouteStep(instruction=f"Take local transport from {payload.source_location} to {origin_station}.", duration_minutes=30),
                    RouteStep(instruction=f"Train journey towards {dest_station} ({driving.distance_km} km).", distance_km=driving.distance_km, duration_minutes=round(train_duration - 60)),
                    RouteStep(instruction=f"Alight at {dest_station} and take a cab/auto to {college.name}.", duration_minutes=30),
                ]
                
            # If train steps were generated via API, adjust duration sum
            if train_steps:
                api_duration = sum(s.duration_minutes or 0 for s in train_steps)
                train_duration = api_duration if api_duration > 0 else train_duration

            options.append(
                RouteOption(
                    transport_type=TransportType.TRAIN,
                    distance_km=driving.distance_km,
                    duration_minutes=round(train_duration),
                    estimated_cost_inr=max(250.0, train_fare),
                    steps=train_steps,
                    polyline=driving.polyline,
                )
            )

        # --- Flight ---
        if driving.distance_km > 350:
            from app.services.places_service import PlacesService
            places = PlacesService()
            
            origin_airport = "nearest Airport"
            dest_airport = f"airport nearest to {college.city}"
            
            origin_air_results = await places.search_nearby(origin_lat, origin_lng, radius=100000, keyword="airport")
            if origin_air_results:
                origin_airport = origin_air_results[0].get("name", origin_airport)
                
            dest_air_results = await places.search_nearby(college.latitude, college.longitude, radius=100000, keyword="airport")
            if dest_air_results:
                dest_airport = dest_air_results[0].get("name", dest_airport)

            flight_duration = (driving.distance_km / 700) * 60 # 700km/h
            flight_fare = round(driving.distance_km * 8 + 1500)
            options.append(
                RouteOption(
                    transport_type=TransportType.FLIGHT,
                    distance_km=driving.distance_km,
                    duration_minutes=round(flight_duration + 180), # 3 hours airport time
                    estimated_cost_inr=max(3500.0, flight_fare),
                    steps=[
                        RouteStep(instruction=f"Travel from {payload.source_location} to {origin_airport}.", duration_minutes=60),
                        RouteStep(instruction=f"Check-in, security, and boarding at {origin_airport}.", duration_minutes=90),
                        RouteStep(instruction=f"Flight to {dest_airport} ({driving.distance_km} km).", distance_km=driving.distance_km, duration_minutes=round(flight_duration)),
                        RouteStep(instruction=f"Exit {dest_airport} and travel to {college.name}.", duration_minutes=60),
                    ],
                    polyline=driving.polyline,
                )
            )

        # --- Auto (Local only) ---
        if driving.distance_km < 30:
            auto_fare = engine.estimate_auto(driving.distance_km)
            auto_duration = driving.duration_minutes * 1.1  # autos are slightly slower in mixed traffic
            options.append(
                RouteOption(
                    transport_type=TransportType.AUTO,
                    distance_km=driving.distance_km,
                    duration_minutes=round(auto_duration, 1),
                    estimated_cost_inr=auto_fare,
                    steps=[
                        RouteStep(instruction=f"Hail or book an auto-rickshaw from {payload.source_location}.", duration_minutes=5),
                        RouteStep(instruction=f"Ride to {college.name} ({driving.distance_km} km). Negotiate fare or use a metered/app auto.", distance_km=driving.distance_km, duration_minutes=round(auto_duration, 1)),
                    ],
                )
            )

        # --- Walking (Local only) ---
        if walking.distance_km <= 4:
            options.append(
                RouteOption(
                    transport_type=TransportType.WALK,
                    distance_km=walking.distance_km,
                    duration_minutes=walking.duration_minutes,
                    estimated_cost_inr=0,
                    steps=[
                        RouteStep(instruction=f"Walk directly from {payload.source_location} to {college.name}.", distance_km=walking.distance_km, duration_minutes=walking.duration_minutes),
                    ],
                )
            )

        # --- Mixed (walk + metro, local only) ---
        if not is_intercity and transit.distance_km > 3:
            mixed_walk_minutes = 6
            mixed_metro_duration, mixed_metro_fare = engine.estimate_metro(max(transit.distance_km - 1, 0.5))
            options.append(
                RouteOption(
                    transport_type=TransportType.MIXED,
                    distance_km=transit.distance_km,
                    duration_minutes=round(mixed_walk_minutes + mixed_metro_duration + 10, 1),
                    estimated_cost_inr=mixed_metro_fare + 15,  # + a short auto leg at the end
                    steps=[
                        RouteStep(instruction=f"Walk {mixed_walk_minutes} min to the nearest metro/bus interchange.", duration_minutes=mixed_walk_minutes),
                        RouteStep(instruction="Take the metro for the main stretch of the journey.", duration_minutes=mixed_metro_duration),
                        RouteStep(instruction=f"Take a short auto ride for the last mile to {college.name}.", duration_minutes=10),
                    ],
                )
            )

        return sorted(options, key=lambda o: o.duration_minutes)

    async def get_history(self, user_id: uuid.UUID, only_bookmarked: bool, offset: int, limit: int) -> list[RouteQuery]:
        return await self.route_repo.list_for_user(user_id, only_bookmarked=only_bookmarked, offset=offset, limit=limit)

    async def toggle_bookmark(self, user_id: uuid.UUID, route_id: uuid.UUID, is_bookmarked: bool) -> RouteQuery:
        route = await self.route_repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route not found.")
        if route.user_id != user_id:
            raise PermissionDeniedError("You can only bookmark your own routes.")
        return await self.route_repo.update(route, is_bookmarked=is_bookmarked)

    async def delete_route(self, user_id: uuid.UUID, route_id: uuid.UUID) -> None:
        route = await self.route_repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route not found.")
        if route.user_id != user_id:
            raise PermissionDeniedError("You can only delete your own routes.")
        await self.route_repo.delete(route)
