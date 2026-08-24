import uuid

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import RouteQuery
from app.repositories.base import BaseRepository


class RouteRepository(BaseRepository[RouteQuery]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, RouteQuery)

    async def list_for_user(
        self, user_id: uuid.UUID, only_bookmarked: bool = False, offset: int = 0, limit: int = 20
    ) -> list[RouteQuery]:
        stmt = select(RouteQuery).where(RouteQuery.user_id == user_id)
        if only_bookmarked:
            stmt = stmt.where(RouteQuery.is_bookmarked.is_(True))
        stmt = stmt.order_by(desc(RouteQuery.created_at)).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def bulk_create(self, rows: list[dict]) -> list[RouteQuery]:
        instances = [RouteQuery(**row) for row in rows]
        self.session.add_all(instances)
        await self.session.flush()
        for instance in instances:
            await self.session.refresh(instance)
        return instances

    async def most_searched_colleges(self, limit: int = 5) -> list[dict]:
        stmt = (
            select(RouteQuery.college_id, func.count(RouteQuery.id).label("search_count"))
            .group_by(RouteQuery.college_id)
            .order_by(desc("search_count"))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return [{"college_id": str(row.college_id), "search_count": row.search_count} for row in result.all()]

    async def transport_type_breakdown(self) -> dict[str, int]:
        stmt = select(RouteQuery.transport_type, func.count(RouteQuery.id)).group_by(RouteQuery.transport_type)
        result = await self.session.execute(stmt)
        return {row[0].value: row[1] for row in result.all()}
