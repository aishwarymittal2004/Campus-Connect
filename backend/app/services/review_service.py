import uuid

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.review import ReviewType
from app.models.user import UserRole
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    async def create(self, user_id: uuid.UUID, payload: ReviewCreate):
        return await self.review_repo.create(user_id=user_id, **payload.model_dump())

    async def list_for_target(self, review_type: ReviewType, target_id: uuid.UUID, offset: int, limit: int):
        return await self.review_repo.list_for_target(review_type, target_id, offset=offset, limit=limit)

    async def update(self, user_id: uuid.UUID, review_id: uuid.UUID, payload: ReviewUpdate):
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review not found.")
        if review.user_id != user_id:
            raise PermissionDeniedError("You can only edit your own reviews.")
        return await self.review_repo.update(review, **payload.model_dump(exclude_unset=True))

    async def delete(self, user_id: uuid.UUID, user_role: UserRole, review_id: uuid.UUID) -> None:
        review = await self.review_repo.get_by_id(review_id)
        if not review:
            raise NotFoundError("Review not found.")
        if review.user_id != user_id and user_role != UserRole.ADMIN:
            raise PermissionDeniedError("You can only delete your own reviews.")
        await self.review_repo.delete(review)
