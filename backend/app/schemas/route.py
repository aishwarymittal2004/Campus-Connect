import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.route import SourceType, TransportType
from app.schemas.common import ORMBase


class RouteSearchRequest(BaseModel):
    source_location: str = Field(min_length=2, max_length=255, description="e.g. 'Lucknow Charbagh Railway Station'")
    source_type: SourceType
    college_id: uuid.UUID
    # Optional precise coordinates if the frontend already resolved them via Places Autocomplete
    source_latitude: float | None = None
    source_longitude: float | None = None


class RouteStep(BaseModel):
    instruction: str
    distance_km: float | None = None
    duration_minutes: float | None = None


class RouteOption(ORMBase):
    id: uuid.UUID | None = None
    transport_type: TransportType
    distance_km: float
    duration_minutes: float
    estimated_cost_inr: float
    steps: list[RouteStep]
    polyline: str | None = None
    is_bookmarked: bool = False


class RouteSearchResponse(BaseModel):
    source_location: str
    college_id: uuid.UUID
    college_name: str
    options: list[RouteOption]


class SavedRouteRead(ORMBase):
    id: uuid.UUID
    source_location: str
    source_type: SourceType
    transport_type: TransportType
    distance_km: float
    duration_minutes: float
    estimated_cost_inr: float
    steps: list[RouteStep]
    is_bookmarked: bool
    created_at: datetime
    college_id: uuid.UUID


class BookmarkToggleRequest(BaseModel):
    is_bookmarked: bool

class TrainScheduleLeg(BaseModel):
    train_number: str
    train_name: str
    departure_station: str
    arrival_station: str
    departure_time: str
    arrival_time: str
    duration: str
    classes: list[str]

class TrainScheduleOption(BaseModel):
    id: str
    legs: list[TrainScheduleLeg]
    total_duration: str
    price_estimate: str
class FlightScheduleLeg(BaseModel):
    flight_number: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str

class FlightScheduleOption(BaseModel):
    id: str
    legs: list[FlightScheduleLeg]
    total_duration: str
    price_estimate: str
