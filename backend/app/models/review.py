import enum
import uuid

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class ReviewType(str, enum.Enum):
    COLLEGE = "college"
    PG = "pg"
    HOSTEL = "hostel"
    ROUTE = "route"


class Review(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "reviews"
    __table_args__ = (CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    college_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="CASCADE"), nullable=True, index=True
    )
    pg_listing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("pg_listings.id", ondelete="CASCADE"), nullable=True, index=True
    )
    route_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("routes.id", ondelete="CASCADE"), nullable=True, index=True
    )

    review_type: Mapped[ReviewType] = mapped_column(Enum(ReviewType, name="review_type", values_callable=lambda enum_cls: [e.value for e in enum_cls]), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship(back_populates="reviews")
    college: Mapped["College"] = relationship(back_populates="reviews")
    pg_listing: Mapped["PGListing"] = relationship(back_populates="reviews")
