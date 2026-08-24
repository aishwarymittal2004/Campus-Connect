import enum

from sqlalchemy import Boolean, Date, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class OfferPlatform(str, enum.Enum):
    ZOMATO = "zomato"
    SWIGGY = "swiggy"
    AMAZON = "amazon"
    FLIPKART = "flipkart"
    OTHER = "other"


class OfferCategory(str, enum.Enum):
    FOOD = "food"
    SHOPPING = "shopping"
    STUDENT = "student"
    OTHER = "other"


class Offer(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "offers"

    platform: Mapped[OfferPlatform] = mapped_column(Enum(OfferPlatform, name="offer_platform", values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False)
    category: Mapped[OfferCategory] = mapped_column(
        Enum(OfferCategory, name="offer_category", values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=OfferCategory.OTHER, nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    discount: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g. "20% OFF" or "Flat ₹100 off"
    promo_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    expiry_date: Mapped[Date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    student_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
