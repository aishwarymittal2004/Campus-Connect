import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import RequireAdmin, get_college_service
from app.schemas.college import CollegeCreate, CollegeRead, CollegeUpdate
from app.schemas.common import MessageResponse
from app.services.college_service import CollegeService

router = APIRouter(prefix="/colleges", tags=["Colleges"])

CollegeSvc = Annotated[CollegeService, Depends(get_college_service)]


@router.get("", response_model=list[CollegeRead])
async def list_colleges(
    college_service: CollegeSvc,
    q: str | None = Query(default=None, description="Search by college name or city"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    if q:
        return await college_service.search(q, offset, limit)
    return await college_service.list(offset, limit)


@router.get("/{college_id}", response_model=CollegeRead)
async def get_college(college_id: uuid.UUID, college_service: CollegeSvc):
    """Includes location, nearby landmarks, and emergency contacts."""
    return await college_service.get(college_id)


@router.post("", response_model=CollegeRead, status_code=status.HTTP_201_CREATED)
async def create_college(payload: CollegeCreate, college_service: CollegeSvc, _admin: RequireAdmin):
    return await college_service.create(payload)


@router.patch("/{college_id}", response_model=CollegeRead)
async def update_college(
    college_id: uuid.UUID, payload: CollegeUpdate, college_service: CollegeSvc, _admin: RequireAdmin
):
    return await college_service.update(college_id, payload)


@router.delete("/{college_id}", response_model=MessageResponse)
async def delete_college(college_id: uuid.UUID, college_service: CollegeSvc, _admin: RequireAdmin):
    await college_service.delete(college_id)
    return MessageResponse(message="College deleted successfully.")
