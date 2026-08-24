import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.college import College
from app.models.offer import Offer
from app.models.pg_listing import PGListing
from app.models.review import Review
from app.models.route import RouteQuery
from app.models.user import User, UserRole
from app.repositories.college_repository import CollegeRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.schemas.admin import PlatformAnalytics
from app.schemas.user import AdminUserUpdate


class AdminService:
    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository,
        college_repo: CollegeRepository,
        route_repo: RouteRepository,
    ):
        self.session = session
        self.user_repo = user_repo
        self.college_repo = college_repo
        self.route_repo = route_repo

    async def list_users(self, offset: int, limit: int, role: UserRole | None = None):
        filters = {"role": role} if role else {}
        return await self.user_repo.list(offset=offset, limit=limit, order_by=User.created_at.desc(), **filters)

    async def update_user(self, user_id: uuid.UUID, payload: AdminUserUpdate):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        return await self.user_repo.update(user, **payload.model_dump(exclude_unset=True))

    async def delete_user(self, user_id: uuid.UUID) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found.")
        await self.user_repo.delete(user)

    async def get_analytics(self) -> PlatformAnalytics:
        async def scalar(stmt):
            result = await self.session.execute(stmt)
            return result.scalar_one()

        total_users = await scalar(select(func.count()).select_from(User))
        total_students = await scalar(select(func.count()).select_from(User).where(User.role == UserRole.STUDENT))
        total_admins = await scalar(select(func.count()).select_from(User).where(User.role == UserRole.ADMIN))
        total_colleges = await scalar(select(func.count()).select_from(College))
        total_route_searches = await scalar(select(func.count()).select_from(RouteQuery))
        total_bookmarked = await scalar(
            select(func.count()).select_from(RouteQuery).where(RouteQuery.is_bookmarked.is_(True))
        )
        total_reviews = await scalar(select(func.count()).select_from(Review))
        avg_rating_result = await self.session.execute(select(func.avg(Review.rating)))
        avg_rating = avg_rating_result.scalar_one_or_none()
        total_pg = await scalar(select(func.count()).select_from(PGListing))
        total_offers = await scalar(select(func.count()).select_from(Offer).where(Offer.is_active.is_(True)))

        most_searched = await self.route_repo.most_searched_colleges(limit=5)
        breakdown = await self.route_repo.transport_type_breakdown()

        return PlatformAnalytics(
            total_users=total_users,
            total_students=total_students,
            total_admins=total_admins,
            total_colleges=total_colleges,
            total_route_searches=total_route_searches,
            total_bookmarked_routes=total_bookmarked,
            total_reviews=total_reviews,
            average_rating=round(float(avg_rating), 2) if avg_rating is not None else None,
            total_pg_listings=total_pg,
            total_active_offers=total_offers,
            most_searched_colleges=most_searched,
            transport_type_breakdown=breakdown,
        )
