from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.offer import Offer, OfferCategory, OfferPlatform
from app.repositories.base import BaseRepository


class OfferRepository(BaseRepository[Offer]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Offer)

    async def list_active(
        self,
        platform: OfferPlatform | None = None,
        category: OfferCategory | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[Offer]:
        stmt = select(Offer).where(Offer.is_active.is_(True))
        stmt = stmt.where((Offer.expiry_date.is_(None)) | (Offer.expiry_date >= date.today()))
        if platform:
            stmt = stmt.where(Offer.platform == platform)
        if category:
            stmt = stmt.where(Offer.category == category)
        stmt = stmt.order_by(Offer.created_at.desc()).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
