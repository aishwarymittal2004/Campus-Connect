import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, get_review_service
from app.models.review import ReviewType
from app.schemas.common import MessageResponse
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews & Community"])

ReviewSvc = Annotated[ReviewService, Depends(get_review_service)]


@router.post("", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
async def create_review(payload: ReviewCreate, current_user: CurrentUser, review_service: ReviewSvc):
    """Create a review for a college, PG, hostel, or a specific route."""
    return await review_service.create(current_user.id, payload)


@router.get("", response_model=list[ReviewRead])
async def list_reviews(
    review_service: ReviewSvc,
    review_type: ReviewType = Query(...),
    target_id: uuid.UUID = Query(..., description="college_id, pg_listing_id, or route_id depending on review_type"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await review_service.list_for_target(review_type, target_id, offset, limit)


@router.patch("/{review_id}", response_model=ReviewRead)
async def update_review(
    review_id: uuid.UUID, payload: ReviewUpdate, current_user: CurrentUser, review_service: ReviewSvc
):
    return await review_service.update(current_user.id, review_id, payload)


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(review_id: uuid.UUID, current_user: CurrentUser, review_service: ReviewSvc):
    await review_service.delete(current_user.id, current_user.role, review_id)
    return MessageResponse(message="Review deleted.")
