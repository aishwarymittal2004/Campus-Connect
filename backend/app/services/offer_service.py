import uuid

from app.core.exceptions import NotFoundError
from app.models.offer import OfferCategory, OfferPlatform
from app.repositories.offer_repository import OfferRepository
from app.schemas.offer import OfferCreate, OfferUpdate


class OfferService:
    """
    Offers are stored in Postgres and served from there - this is the
    correct architecture regardless of where the data originates, because:

      - Amazon PA-API / Flipkart Affiliate API require signed requests +
        approved affiliate accounts (cannot be called anonymously).
      - Zomato and Swiggy do not currently expose any public partner API
        for third-party discount aggregation.

    In production, a scheduled worker (Celery beat / cron) would call
    `sync_from_external_platforms()` periodically to refresh this table from
    whichever affiliate feeds you have credentials for, using the
    `RAPIDAPI_KEY_AMAZON` / `RAPIDAPI_KEY_FLIPKART` settings.
    Until those credentials are supplied, admins manage offers manually via
    the Admin Dashboard, and this table is the single source of truth the
    frontend reads from either way.
    """

    def __init__(self, offer_repo: OfferRepository):
        self.offer_repo = offer_repo

    async def list_active(
        self, platform: OfferPlatform | None, category: OfferCategory | None, offset: int, limit: int
    ):
        return await self.offer_repo.list_active(platform=platform, category=category, offset=offset, limit=limit)

    async def create(self, payload: OfferCreate):
        return await self.offer_repo.create(**payload.model_dump())

    async def update(self, offer_id: uuid.UUID, payload: OfferUpdate):
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundError("Offer not found.")
        return await self.offer_repo.update(offer, **payload.model_dump(exclude_unset=True))

    async def delete(self, offer_id: uuid.UUID) -> None:
        offer = await self.offer_repo.get_by_id(offer_id)
        if not offer:
            raise NotFoundError("Offer not found.")
        await self.offer_repo.delete(offer)
