import enum
import uuid

from sqlalchemy import Boolean, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class SourceType(str, enum.Enum):
    RAILWAY_STATION = "railway_station"
    AIRPORT = "airport"
    BUS_STAND = "bus_stand"
    OTHER = "other"


class TransportType(str, enum.Enum):
    METRO = "metro"
    BUS = "bus"
    CAB = "cab"
    AUTO = "auto"
    WALK = "walk"
    MIXED = "mixed"
    TRAIN = "train"
    FLIGHT = "flight"


class RouteQuery(Base, UUIDPKMixin, TimestampMixin):
    """
    One route *option* returned for a source -> college search.
    A single search typically produces several rows (one per transport_type).
    `is_bookmarked` implements the "Saved Routes" feature; every row is also
    implicitly part of the user's route history.
    """
    __tablename__ = "routes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=False, index=True
    )

    source_location: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type", values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False)
    source_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    transport_type: Mapped[TransportType] = mapped_column(Enum(TransportType, name="transport_type", values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, nullable=False)
    duration_minutes: Mapped[float] = mapped_column(Float, nullable=False)
    estimated_cost_inr: Mapped[float] = mapped_column(Float, nullable=False)

    # Ordered list of {"instruction": "...", "distance_km": .., "duration_minutes": ..}
    steps: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    polyline: Mapped[str | None] = mapped_column(String, nullable=True)  # encoded polyline for map rendering

    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="route_history")
    college: Mapped["College"] = relationship(back_populates="route_queries")
