import enum
import uuid

from sqlalchemy import Boolean, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin, UUIDPKMixin


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class User(Base, UUIDPKMixin, TimestampMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda enum_cls: [e.value for e in enum_cls]), default=UserRole.STUDENT, nullable=False
    )
    college_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("colleges.id", ondelete="SET NULL"), nullable=True
    )  # optional - set once user picks their college
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    student_tips: Mapped[list["StudentTip"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    route_history: Mapped[list["RouteQuery"]] = relationship(back_populates="user", cascade="all, delete-orphan")
