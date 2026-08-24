import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pg_listing import LocalService, LocalServiceCategory, PGListing
from app.repositories.base import BaseRepository


class PGListingRepository(BaseRepository[PGListing]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, PGListing)

    async def list_for_college(
        self, college_id: uuid.UUID, max_rent: float | None = None, offset: int = 0, limit: int = 20
    ) -> list[PGListing]:
        stmt = select(PGListing).where(PGListing.college_id == college_id)
        if max_rent is not None:
            stmt = stmt.where(PGListing.rent <= max_rent)
        stmt = stmt.order_by(PGListing.rent).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class LocalServiceRepository(BaseRepository[LocalService]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, LocalService)

    async def list_for_college(
        self, college_id: uuid.UUID, category: LocalServiceCategory | None = None
    ) -> list[LocalService]:
        stmt = select(LocalService).where(LocalService.college_id == college_id)
        if category:
            stmt = stmt.where(LocalService.category == category)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
