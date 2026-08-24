import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class LandmarkItem(BaseModel):
    name: str
    type: str = "landmark"
    distance_km: float | None = None


class EmergencyContactItem(BaseModel):
    label: str
    phone: str


class CollegeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    city: str = Field(min_length=2, max_length=120)
    state: str | None = None
    address: str | None = None
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    nearby_landmarks: list[LandmarkItem] = Field(default_factory=list)
    emergency_contacts: list[EmergencyContactItem] = Field(default_factory=list)
    website: str | None = None
    tags: list[str] = Field(default_factory=list)


class CollegeUpdate(BaseModel):
    name: str | None = None
    city: str | None = None
    state: str | None = None
    address: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    nearby_landmarks: list[LandmarkItem] | None = None
    emergency_contacts: list[EmergencyContactItem] | None = None
    website: str | None = None
    tags: list[str] | None = None


class CollegeRead(ORMBase):
    id: uuid.UUID
    name: str
    city: str
    state: str | None
    address: str | None
    latitude: float
    longitude: float
    nearby_landmarks: list[LandmarkItem] = Field(default_factory=list)
    emergency_contacts: list[EmergencyContactItem] = Field(default_factory=list)
    website: str | None
    tags: list[str] = Field(default_factory=list)
    created_at: datetime


class CollegeSummary(ORMBase):
    id: uuid.UUID
    name: str
    city: str
    latitude: float
    longitude: float
