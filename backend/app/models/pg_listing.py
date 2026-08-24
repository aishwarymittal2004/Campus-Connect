import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class AccommodationType(str, enum.Enum):
    PG = "pg"
    HOSTEL = "hostel"


class PGListing(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "pg_listings"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    accommodation_type: Mapped[AccommodationType] = mapped_column(
        Enum(AccommodationType, name="accommodation_type", values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=AccommodationType.PG, nullable=False
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    rent: Mapped[float] = mapped_column(Float, nullable=False)
    contact: Mapped[str] = mapped_column(String(50), nullable=False)
    amenities: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True, default=list)
    has_mess: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gender_preference: Mapped[str | None] = mapped_column(String(20), nullable=True)  # male | female | any
    distance_from_college_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    college: Mapped["College"] = relationship(back_populates="pg_listings")
    reviews: Mapped[list["Review"]] = relationship(back_populates="pg_listing", cascade="all, delete-orphan")


class LocalServiceCategory(str, enum.Enum):
    MESS = "mess"
    MEDICAL_STORE = "medical_store"
    ATM = "atm"
    GROCERY = "grocery"
    CAFE = "cafe"
    HOTEL = "hotel"


class LocalService(Base, UUIDPKMixin, TimestampMixin):
    """Mess facilities, medical stores, ATMs, and grocery stores near a college."""
    __tablename__ = "local_services"

    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    category: Mapped[LocalServiceCategory] = mapped_column(
        Enum(LocalServiceCategory, name="local_service_category", values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    contact: Mapped[str | None] = mapped_column(String(50), nullable=True)
    distance_from_college_km: Mapped[float | None] = mapped_column(Float, nullable=True)
    opening_hours: Mapped[str | None] = mapped_column(String(120), nullable=True)

    college: Mapped["College"] = relationship()
