from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.deps import CurrentUser, get_auth_service
from app.schemas.common import MessageResponse
from app.schemas.user import (
    PasswordChange,
    RefreshRequest,
    TokenPair,
    UserLogin,
    UserRead,
    UserSignup,
    UserUpdate,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

AuthSvc = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(payload: UserSignup, auth_service: AuthSvc):
    """Register a new student account."""
    user = await auth_service.signup(payload)
    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, auth_service: AuthSvc):
    """Exchange email + password for an access/refresh token pair."""
    _, tokens = await auth_service.login(payload.email, payload.password)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, auth_service: AuthSvc):
    """Exchange a valid refresh token for a new access/refresh token pair (rotation)."""
    return await auth_service.refresh(payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: RefreshRequest, auth_service: AuthSvc):
    """Revoke a refresh token, ending the session it belongs to."""
    await auth_service.logout(payload.refresh_token)
    return MessageResponse(message="Logged out successfully.")


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: CurrentUser):
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_my_profile(payload: UserUpdate, current_user: CurrentUser, auth_service: AuthSvc):
    return await auth_service.update_profile(current_user.id, **payload.model_dump(exclude_unset=True))


@router.post("/me/change-password", response_model=MessageResponse)
async def change_password(payload: PasswordChange, current_user: CurrentUser, auth_service: AuthSvc):
    await auth_service.change_password(current_user.id, payload)
    return MessageResponse(message="Password updated successfully.")
