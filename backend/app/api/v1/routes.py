import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, get_route_service
from app.schemas.common import MessageResponse
from app.schemas.route import (
    BookmarkToggleRequest,
    RouteSearchRequest,
    RouteSearchResponse,
    SavedRouteRead,
    TrainScheduleOption,
    FlightScheduleOption,
)
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["Route Finder"])

RouteSvc = Annotated[RouteService, Depends(get_route_service)]


@router.post("/search", response_model=RouteSearchResponse)
async def search_routes(payload: RouteSearchRequest, current_user: CurrentUser, route_service: RouteSvc):
    """
    Given a source (railway station / airport / bus stand) and a college,
    returns metro, bus, cab, auto, walking and mixed route options - each
    with distance, estimated time, estimated cost, and turn-by-turn steps.
    """
    return await route_service.search_routes(current_user.id, payload)


@router.get("/history", response_model=list[SavedRouteRead])
async def get_route_history(
    current_user: CurrentUser,
    route_service: RouteSvc,
    bookmarked_only: bool = Query(default=False),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await route_service.get_history(current_user.id, bookmarked_only, offset, limit)

@router.get("/train-schedules", response_model=list[TrainScheduleOption])
async def get_train_schedules(
    source: str = Query(..., description="Source location name"),
    dest: str = Query(..., description="Destination location name")
):
    from app.services.train_api_service import TrainAPIService
    train_api = TrainAPIService()
    schedules = await train_api.get_train_schedules(source, dest)
    return schedules


@router.patch("/{route_id}/bookmark", response_model=SavedRouteRead)
async def toggle_bookmark(
    route_id: uuid.UUID, payload: BookmarkToggleRequest, current_user: CurrentUser, route_service: RouteSvc
):
    return await route_service.toggle_bookmark(current_user.id, route_id, payload.is_bookmarked)


@router.delete("/{route_id}", response_model=MessageResponse)
async def delete_route(route_id: uuid.UUID, current_user: CurrentUser, route_service: RouteSvc):
    await route_service.delete_route(current_user.id, route_id)
    return MessageResponse(message="Route removed.")

@router.get("/flight-schedules", response_model=list[FlightScheduleOption])
async def get_flight_schedules(
    source: str = Query(..., description="Source location name"),
    dest: str = Query(..., description="Destination location name")
):
    from app.services.flight_api_service import FlightAPIService
    flight_api = FlightAPIService()
    schedules = await flight_api.get_flight_schedules(source, dest)
    return schedules
