import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.student_tip import StudentTip
from app.repositories.base import BaseRepository


class StudentTipRepository(BaseRepository[StudentTip]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StudentTip)

    async def list_for_college(self, college_id: uuid.UUID, offset: int = 0, limit: int = 20) -> list[StudentTip]:
        stmt = (
            select(StudentTip)
            .where(StudentTip.college_id == college_id)
            .order_by(StudentTip.upvotes.desc(), StudentTip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
