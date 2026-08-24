import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import RequireAdmin, get_pg_service
from app.models.pg_listing import LocalServiceCategory
from app.schemas.common import MessageResponse
from app.schemas.pg_listing import (
    LocalServiceCreate,
    LocalServiceRead,
    PGListingCreate,
    PGListingRead,
    PGListingUpdate,
)
from app.services.pg_service import PGService

router = APIRouter(prefix="/services", tags=["Local Student Services"])

PgSvc = Annotated[PGService, Depends(get_pg_service)]


@router.get("/pg-listings", response_model=list[PGListingRead])
async def list_pg_listings(
    pg_service: PgSvc,
    college_id: uuid.UUID = Query(...),
    max_rent: float | None = Query(default=None, gt=0),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    """PGs and hostels near a college, sorted by rent (ascending)."""
    return await pg_service.list_for_college(college_id, max_rent, offset, limit)


@router.post("/pg-listings", response_model=PGListingRead, status_code=status.HTTP_201_CREATED)
async def create_pg_listing(payload: PGListingCreate, pg_service: PgSvc, _admin: RequireAdmin):
    return await pg_service.create(payload)


@router.patch("/pg-listings/{listing_id}", response_model=PGListingRead)
async def update_pg_listing(listing_id: uuid.UUID, payload: PGListingUpdate, pg_service: PgSvc, admin: RequireAdmin):
    return await pg_service.update(admin.role, listing_id, payload)


@router.delete("/pg-listings/{listing_id}", response_model=MessageResponse)
async def delete_pg_listing(listing_id: uuid.UUID, pg_service: PgSvc, admin: RequireAdmin):
    await pg_service.delete(admin.role, listing_id)
    return MessageResponse(message="Listing deleted.")


@router.get("/local", response_model=list[LocalServiceRead])
async def list_local_services(
    pg_service: PgSvc,
    college_id: uuid.UUID = Query(...),
    category: LocalServiceCategory | None = Query(default=None),
):
    """Mess facilities, medical stores, ATMs, and grocery stores near a college."""
    return await pg_service.list_local_services(college_id, category)


@router.post("/local", response_model=LocalServiceRead, status_code=status.HTTP_201_CREATED)
async def create_local_service(payload: LocalServiceCreate, pg_service: PgSvc, _admin: RequireAdmin):
    return await pg_service.create_local_service(payload)
