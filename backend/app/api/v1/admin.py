import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import RequireAdmin, get_admin_service
from app.models.user import UserRole
from app.schemas.admin import PlatformAnalytics
from app.schemas.common import MessageResponse
from app.schemas.user import AdminUserUpdate, UserRead
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

AdminSvc = Annotated[AdminService, Depends(get_admin_service)]


@router.get("/users", response_model=list[UserRead])
async def list_users(
    admin_service: AdminSvc,
    _admin: RequireAdmin,
    role: UserRole | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    return await admin_service.list_users(offset, limit, role)


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: uuid.UUID, payload: AdminUserUpdate, admin_service: AdminSvc, _admin: RequireAdmin):
    """Promote/demote roles or activate/deactivate an account."""
    return await admin_service.update_user(user_id, payload)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(user_id: uuid.UUID, admin_service: AdminSvc, _admin: RequireAdmin):
    await admin_service.delete_user(user_id)
    return MessageResponse(message="User deleted.")


@router.get("/analytics", response_model=PlatformAnalytics)
async def get_analytics(admin_service: AdminSvc, _admin: RequireAdmin):
    """Platform-wide usage analytics: users, searches, popular colleges, transport-mode breakdown, ratings."""
    return await admin_service.get_analytics()
