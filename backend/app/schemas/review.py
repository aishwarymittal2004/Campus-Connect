import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.models.review import ReviewType
from app.schemas.common import ORMBase


class ReviewCreate(BaseModel):
    review_type: ReviewType
    rating: int = Field(ge=1, le=5)
    comment: str = Field(min_length=3, max_length=2000)
    college_id: uuid.UUID | None = None
    pg_listing_id: uuid.UUID | None = None
    route_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def check_target_matches_type(self):
        target_map = {
            ReviewType.COLLEGE: self.college_id,
            ReviewType.HOSTEL: self.college_id,
            ReviewType.PG: self.pg_listing_id,
            ReviewType.ROUTE: self.route_id,
        }
        if target_map.get(self.review_type) is None:
            raise ValueError(f"A target id is required for review_type='{self.review_type.value}'")
        return self


class ReviewRead(ORMBase):
    id: uuid.UUID
    user_id: uuid.UUID
    review_type: ReviewType
    rating: int
    comment: str
    college_id: uuid.UUID | None
    pg_listing_id: uuid.UUID | None
    route_id: uuid.UUID | None
    created_at: datetime


class ReviewUpdate(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = Field(default=None, min_length=3, max_length=2000)
