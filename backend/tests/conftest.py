"""
Test configuration.

Tests run against a real, separate Postgres database (`campus_connect_test`)
rather than SQLite, because several models use Postgres-native types
(UUID, JSONB, ARRAY) that don't have SQLite equivalents.

Each test function gets its own async engine (bound to whatever event loop
pytest-asyncio spins up for that test) and a freshly dropped+recreated
schema, so tests are fully isolated from one another and never hit
cross-event-loop asyncpg errors.
"""
import os
import uuid
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://campus:campus@localhost:5432/campus_connect_test"
)
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")  # separate Redis DB index for test isolation

from app.core.database import Base, get_session  # noqa: E402
from app.core import redis_client as redis_module  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import UserRole  # noqa: E402

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


@pytest_asyncio.fixture(autouse=True)
async def _isolated_redis():
    """
    The Redis wrapper is a process-wide singleton whose connections are tied
    to the event loop they were opened on. Since each test function gets its
    own event loop, we must close out any connections from the previous
    test's loop before this test starts, so the client reconnects fresh.
    """
    yield
    try:
        await redis_module.redis_pool.disconnect()
    except Exception:
        pass
    redis_module.cache._client = None



@pytest_asyncio.fixture
async def db_session_maker():
    """A fresh engine + schema per test, bound to this test's event loop."""
    engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    yield session_maker
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session_maker) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with db_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_session] = _override_get_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.pop(get_session, None)


async def _signup_and_login(client: AsyncClient, email: str, password: str = "TestPass123", name: str = "Test User"):
    await client.post("/api/v1/auth/signup", json={"name": name, "email": email, "password": password})
    resp = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.json()


@pytest_asyncio.fixture
async def student_tokens(client: AsyncClient):
    return await _signup_and_login(client, email=f"student-{uuid.uuid4().hex[:8]}@test.com")


@pytest_asyncio.fixture
async def admin_tokens(client: AsyncClient, db_session_maker):
    email = f"admin-{uuid.uuid4().hex[:8]}@test.com"
    await _signup_and_login(client, email=email)

    async with db_session_maker() as session:
        from sqlalchemy import update

        from app.models.user import User

        await session.execute(update(User).where(User.email == email).values(role=UserRole.ADMIN))
        await session.commit()

    # role is embedded in the JWT, so we must re-login to get a token reflecting the new role
    resp_login = await client.post("/api/v1/auth/login", json={"email": email, "password": "TestPass123"})
    return resp_login.json()


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}
