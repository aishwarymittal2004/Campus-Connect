from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college import College
from app.repositories.base import BaseRepository


class CollegeRepository(BaseRepository[College]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, College)

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> list[College]:
        stmt = (
            select(College)
            .where(or_(College.name.ilike(f"%{query}%"), College.city.ilike(f"%{query}%")))
            .order_by(College.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
