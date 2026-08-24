import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMBase


class StudentTipCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    content: str = Field(min_length=5, max_length=3000)
    college_id: uuid.UUID | None = None


class StudentTipRead(ORMBase):
    id: uuid.UUID
    user_id: uuid.UUID
    college_id: uuid.UUID | None
    title: str
    content: str
    upvotes: int
    created_at: datetime


class StudentTipUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
