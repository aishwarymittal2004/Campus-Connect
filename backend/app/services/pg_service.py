import uuid

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.models.pg_listing import LocalServiceCategory
from app.models.user import UserRole
from app.repositories.pg_repository import LocalServiceRepository, PGListingRepository
from app.schemas.pg_listing import LocalServiceCreate, PGListingCreate, PGListingUpdate


class PGService:
    def __init__(self, pg_repo: PGListingRepository, local_service_repo: LocalServiceRepository):
        self.pg_repo = pg_repo
        self.local_service_repo = local_service_repo

    async def list_for_college(self, college_id: uuid.UUID, max_rent: float | None, offset: int, limit: int):
        return await self.pg_repo.list_for_college(college_id, max_rent=max_rent, offset=offset, limit=limit)

    async def create(self, payload: PGListingCreate):
        return await self.pg_repo.create(**payload.model_dump())

    async def update(self, user_role: UserRole, listing_id: uuid.UUID, payload: PGListingUpdate):
        if user_role != UserRole.ADMIN:
            raise PermissionDeniedError("Only admins can edit PG/hostel listings.")
        listing = await self.pg_repo.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Listing not found.")
        return await self.pg_repo.update(listing, **payload.model_dump(exclude_unset=True))

    async def delete(self, user_role: UserRole, listing_id: uuid.UUID) -> None:
        if user_role != UserRole.ADMIN:
            raise PermissionDeniedError("Only admins can delete PG/hostel listings.")
        listing = await self.pg_repo.get_by_id(listing_id)
        if not listing:
            raise NotFoundError("Listing not found.")
        await self.pg_repo.delete(listing)

    async def list_local_services(self, college_id: uuid.UUID, category: LocalServiceCategory | None):
        return await self.local_service_repo.list_for_college(college_id, category=category)

    async def create_local_service(self, payload: LocalServiceCreate):
        return await self.local_service_repo.create(**payload.model_dump())
