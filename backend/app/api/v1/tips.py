import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import CurrentUser, get_student_tip_service
from app.schemas.common import MessageResponse
from app.schemas.student_tip import StudentTipCreate, StudentTipRead, StudentTipUpdate
from app.services.student_tip_service import StudentTipService

router = APIRouter(prefix="/tips", tags=["Reviews & Community"])

TipSvc = Annotated[StudentTipService, Depends(get_student_tip_service)]


@router.post("", response_model=StudentTipRead, status_code=status.HTTP_201_CREATED)
async def create_tip(payload: StudentTipCreate, current_user: CurrentUser, tip_service: TipSvc):
    return await tip_service.create(current_user.id, payload)


@router.get("", response_model=list[StudentTipRead])
async def list_tips(
    tip_service: TipSvc,
    college_id: uuid.UUID = Query(...),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await tip_service.list_for_college(college_id, offset, limit)


@router.post("/{tip_id}/upvote", response_model=StudentTipRead)
async def upvote_tip(tip_id: uuid.UUID, tip_service: TipSvc, _current_user: CurrentUser):
    return await tip_service.upvote(tip_id)


@router.patch("/{tip_id}", response_model=StudentTipRead)
async def update_tip(tip_id: uuid.UUID, payload: StudentTipUpdate, current_user: CurrentUser, tip_service: TipSvc):
    return await tip_service.update(current_user.id, tip_id, payload)


@router.delete("/{tip_id}", response_model=MessageResponse)
async def delete_tip(tip_id: uuid.UUID, current_user: CurrentUser, tip_service: TipSvc):
    await tip_service.delete(current_user.id, current_user.role, tip_id)
    return MessageResponse(message="Tip deleted.")
