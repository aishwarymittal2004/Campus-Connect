import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.pg_listing import AccommodationType, LocalServiceCategory
from app.schemas.common import ORMBase


class PGListingCreate(BaseModel):
    college_id: uuid.UUID
    name: str = Field(min_length=2, max_length=255)
    accommodation_type: AccommodationType = AccommodationType.PG
    address: str
    latitude: float | None = None
    longitude: float | None = None
    rent: float = Field(gt=0)
    contact: str
    amenities: list[str] = Field(default_factory=list)
    has_mess: bool = False
    gender_preference: str | None = None
    distance_from_college_km: float | None = None


class PGListingUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    rent: float | None = Field(default=None, gt=0)
    contact: str | None = None
    amenities: list[str] | None = None
    has_mess: bool | None = None
    gender_preference: str | None = None
    is_verified: bool | None = None


class PGListingRead(ORMBase):
    id: uuid.UUID
    college_id: uuid.UUID
    name: str
    accommodation_type: AccommodationType
    address: str
    latitude: float | None
    longitude: float | None
    rent: float
    contact: str
    amenities: list[str] = Field(default_factory=list)
    has_mess: bool
    gender_preference: str | None
    distance_from_college_km: float | None
    is_verified: bool
    created_at: datetime


class LocalServiceCreate(BaseModel):
    college_id: uuid.UUID
    category: LocalServiceCategory
    name: str
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    contact: str | None = None
    distance_from_college_km: float | None = None
    opening_hours: str | None = None


class LocalServiceRead(ORMBase):
    id: uuid.UUID
    college_id: uuid.UUID
    category: LocalServiceCategory
    name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    contact: str | None
    distance_from_college_km: float | None
    opening_hours: str | None
