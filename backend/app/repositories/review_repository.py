import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review, ReviewType
from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Review)

    async def list_for_target(
        self, review_type: ReviewType, target_id: uuid.UUID, offset: int = 0, limit: int = 20
    ) -> list[Review]:
        field = {
            ReviewType.COLLEGE: Review.college_id,
            ReviewType.HOSTEL: Review.college_id,
            ReviewType.PG: Review.pg_listing_id,
            ReviewType.ROUTE: Review.route_id,
        }[review_type]
        stmt = (
            select(Review)
            .where(Review.review_type == review_type, field == target_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def average_rating_for_college(self, college_id: uuid.UUID) -> float | None:
        stmt = select(func.avg(Review.rating)).where(Review.college_id == college_id)
        result = await self.session.execute(stmt)
        avg = result.scalar_one_or_none()
        return round(float(avg), 2) if avg is not None else None

    async def platform_average_rating(self) -> float | None:
        stmt = select(func.avg(Review.rating))
        result = await self.session.execute(stmt)
        avg = result.scalar_one_or_none()
        return round(float(avg), 2) if avg is not None else None
