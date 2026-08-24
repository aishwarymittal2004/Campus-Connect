import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models.offer import OfferCategory, OfferPlatform
from app.schemas.common import ORMBase


class OfferCreate(BaseModel):
    platform: OfferPlatform
    category: OfferCategory = OfferCategory.OTHER
    title: str = Field(min_length=2, max_length=255)
    description: str | None = None
    discount: str = Field(max_length=100)
    promo_code: str | None = None
    url: str
    expiry_date: date | None = None
    student_only: bool = False
    is_active: bool = True


class OfferUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    discount: str | None = None
    promo_code: str | None = None
    url: str | None = None
    expiry_date: date | None = None
    student_only: bool | None = None
    is_active: bool | None = None
    category: OfferCategory | None = None


class OfferRead(ORMBase):
    id: uuid.UUID
    platform: OfferPlatform
    category: OfferCategory
    title: str
    description: str | None
    discount: str
    promo_code: str | None
    url: str
    expiry_date: date | None
    is_active: bool
    student_only: bool
    created_at: datetime
