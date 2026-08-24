import uuid

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.user import UserRole
from app.repositories.student_tip_repository import StudentTipRepository
from app.schemas.student_tip import StudentTipCreate, StudentTipUpdate


class StudentTipService:
    def __init__(self, tip_repo: StudentTipRepository):
        self.tip_repo = tip_repo

    async def create(self, user_id: uuid.UUID, payload: StudentTipCreate):
        return await self.tip_repo.create(user_id=user_id, **payload.model_dump())

    async def list_for_college(self, college_id: uuid.UUID, offset: int, limit: int):
        return await self.tip_repo.list_for_college(college_id, offset=offset, limit=limit)

    async def upvote(self, tip_id: uuid.UUID):
        tip = await self.tip_repo.get_by_id(tip_id)
        if not tip:
            raise NotFoundError("Tip not found.")
        return await self.tip_repo.update(tip, upvotes=tip.upvotes + 1)

    async def update(self, user_id: uuid.UUID, tip_id: uuid.UUID, payload: StudentTipUpdate):
        tip = await self.tip_repo.get_by_id(tip_id)
        if not tip:
            raise NotFoundError("Tip not found.")
        if tip.user_id != user_id:
            raise PermissionDeniedError("You can only edit your own tips.")
        return await self.tip_repo.update(tip, **payload.model_dump(exclude_unset=True))

    async def delete(self, user_id: uuid.UUID, user_role: UserRole, tip_id: uuid.UUID) -> None:
        tip = await self.tip_repo.get_by_id(tip_id)
        if not tip:
            raise NotFoundError("Tip not found.")
        if tip.user_id != user_id and user_role != UserRole.ADMIN:
            raise PermissionDeniedError("You can only delete your own tips.")
        await self.tip_repo.delete(tip)
