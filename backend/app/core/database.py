"""
Database engine & session management.

Uses SQLAlchemy 2.0 async style. A single async engine is created at import
time and reused across the app; sessions are created per-request via the
`get_db` dependency (see app/api/deps.py).
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    """
    Yields a new async DB session scoped to a single request.

    Commit-per-request: if the request handler completes without raising,
    the transaction is committed here. Any exception rolls the whole
    request back, so a single request either fully succeeds or leaves no
    partial writes.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
