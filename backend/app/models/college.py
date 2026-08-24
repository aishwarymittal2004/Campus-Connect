from sqlalchemy import Float, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class College(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "colleges"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    state: Mapped[str | None] = mapped_column(String(120), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    # Nearby landmarks stored as JSON: [{"name": "...", "type": "...", "distance_km": 1.2}]
    nearby_landmarks: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    # Emergency contacts stored as JSON: [{"label": "Campus Security", "phone": "..."}]
    emergency_contacts: Mapped[list | None] = mapped_column(JSONB, nullable=True, default=list)

    website: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True, default=list)

    reviews: Mapped[list["Review"]] = relationship(back_populates="college", cascade="all, delete-orphan")
    pg_listings: Mapped[list["PGListing"]] = relationship(back_populates="college", cascade="all, delete-orphan")
    route_queries: Mapped[list["RouteQuery"]] = relationship(back_populates="college", cascade="all, delete-orphan")
