import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.api.deps import RequireAdmin, get_offer_service
from app.models.offer import OfferCategory, OfferPlatform
from app.schemas.common import MessageResponse
from app.schemas.offer import OfferCreate, OfferRead, OfferUpdate
from app.services.offer_service import OfferService

router = APIRouter(prefix="/offers", tags=["Offers"])

OfferSvc = Annotated[OfferService, Depends(get_offer_service)]


@router.get("", response_model=list[OfferRead])
async def list_offers(
    offer_service: OfferSvc,
    platform: OfferPlatform | None = Query(default=None),
    category: OfferCategory | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    """Active, non-expired offers - optionally filtered by platform (zomato/swiggy/amazon/flipkart) or category."""
    return await offer_service.list_active(platform, category, offset, limit)


@router.post("", response_model=OfferRead, status_code=status.HTTP_201_CREATED)
async def create_offer(payload: OfferCreate, offer_service: OfferSvc, _admin: RequireAdmin):
    return await offer_service.create(payload)


@router.patch("/{offer_id}", response_model=OfferRead)
async def update_offer(offer_id: uuid.UUID, payload: OfferUpdate, offer_service: OfferSvc, _admin: RequireAdmin):
    return await offer_service.update(offer_id, payload)


@router.delete("/{offer_id}", response_model=MessageResponse)
async def delete_offer(offer_id: uuid.UUID, offer_service: OfferSvc, _admin: RequireAdmin):
    await offer_service.delete(offer_id)
    return MessageResponse(message="Offer deleted.")
