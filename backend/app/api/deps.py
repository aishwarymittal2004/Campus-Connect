"""
Central dependency-injection wiring.

Every request-scoped repository/service is constructed here via FastAPI's
`Depends`, so:
  - Routers only ever depend on *services*, never repositories or the DB session directly.
  - Swapping an implementation (e.g. a different cache, a mock repo in tests) means overriding one function.
  - `get_current_user` / `require_role` implement the JWT auth + RBAC guard used across all protected endpoints.
"""
import uuid
from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.exceptions import PermissionDeniedError, TokenError
from app.core.redis_client import RedisCache, cache
from app.core.security import TokenType, decode_token
from app.models.user import User, UserRole
from app.repositories.college_repository import CollegeRepository
from app.repositories.offer_repository import OfferRepository
from app.repositories.pg_repository import LocalServiceRepository, PGListingRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.student_tip_repository import StudentTipRepository
from app.repositories.user_repository import UserRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.college_service import CollegeService
from app.services.offer_service import OfferService
from app.services.pg_service import PGService
from app.services.review_service import ReviewService
from app.services.route_service import RouteService
from app.services.student_tip_service import StudentTipService
from app.services.places_service import PlacesService
from app.services.travel_service import TravelService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ---- Infra ----
DbSession = Annotated[AsyncSession, Depends(get_session)]


def get_cache() -> RedisCache:
    return cache


Cache = Annotated[RedisCache, Depends(get_cache)]


# ---- Repositories ----
def get_user_repository(session: DbSession) -> UserRepository:
    return UserRepository(session)


def get_college_repository(session: DbSession) -> CollegeRepository:
    return CollegeRepository(session)


def get_route_repository(session: DbSession) -> RouteRepository:
    return RouteRepository(session)


def get_offer_repository(session: DbSession) -> OfferRepository:
    return OfferRepository(session)


def get_review_repository(session: DbSession) -> ReviewRepository:
    return ReviewRepository(session)


def get_pg_repository(session: DbSession) -> PGListingRepository:
    return PGListingRepository(session)


def get_local_service_repository(session: DbSession) -> LocalServiceRepository:
    return LocalServiceRepository(session)


def get_student_tip_repository(session: DbSession) -> StudentTipRepository:
    return StudentTipRepository(session)


# ---- Services ----
def get_auth_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)], cache_: Cache
) -> AuthService:
    return AuthService(user_repo, cache_)


def get_college_service(
    college_repo: Annotated[CollegeRepository, Depends(get_college_repository)]
) -> CollegeService:
    return CollegeService(college_repo)


def get_route_service(
    route_repo: Annotated[RouteRepository, Depends(get_route_repository)],
    college_repo: Annotated[CollegeRepository, Depends(get_college_repository)],
    cache_: Cache,
) -> RouteService:
    return RouteService(route_repo, college_repo, cache_)


def get_offer_service(offer_repo: Annotated[OfferRepository, Depends(get_offer_repository)]) -> OfferService:
    return OfferService(offer_repo)


def get_review_service(review_repo: Annotated[ReviewRepository, Depends(get_review_repository)]) -> ReviewService:
    return ReviewService(review_repo)


def get_pg_service(
    pg_repo: Annotated[PGListingRepository, Depends(get_pg_repository)],
    local_service_repo: Annotated[LocalServiceRepository, Depends(get_local_service_repository)],
) -> PGService:
    return PGService(pg_repo, local_service_repo)


def get_student_tip_service(
    tip_repo: Annotated[StudentTipRepository, Depends(get_student_tip_repository)]
) -> StudentTipService:
    return StudentTipService(tip_repo)


def get_admin_service(
    session: DbSession,
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    college_repo: Annotated[CollegeRepository, Depends(get_college_repository)],
    route_repo: Annotated[RouteRepository, Depends(get_route_repository)],
) -> AdminService:
    return AdminService(session, user_repo, college_repo, route_repo)


def get_places_service() -> PlacesService:
    return PlacesService()


def get_travel_service() -> TravelService:
    return TravelService()


# ---- Auth / RBAC guards ----
async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    cache_: Cache,
) -> User:
    if not token:
        raise TokenError("Not authenticated.")
    try:
        payload = decode_token(token)
    except JWTError:
        raise TokenError("Invalid or expired access token.")

    if payload.token_type != TokenType.ACCESS.value:
        raise TokenError("Provided token is not an access token.")

    if await cache_.is_blacklisted(payload.jti):
        raise TokenError("This token has been revoked.")

    user = await user_repo.get_by_id(uuid.UUID(payload.sub))
    if not user or not user.is_active:
        raise TokenError("User no longer exists or is inactive.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*allowed_roles: UserRole):
    """Usage: `Depends(require_role(UserRole.ADMIN))` on any admin-only route."""

    async def _guard(user: CurrentUser) -> User:
        if user.role not in allowed_roles:
            raise PermissionDeniedError("You do not have permission to access this resource.")
        return user

    return _guard


RequireAdmin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
