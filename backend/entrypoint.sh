#!/bin/bash
set -e

echo "Waiting for database..."
python - << 'PYEOF'
import asyncio
import sys
import time

from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

async def wait_for_db(retries: int = 30, delay: float = 2.0):
    for attempt in range(1, retries + 1):
        try:
            engine = create_async_engine(settings.DATABASE_URL)
            async with engine.connect() as conn:
                pass
            await engine.dispose()
            print("Database is ready.")
            return
        except Exception as exc:
            print(f"[{attempt}/{retries}] Database not ready yet: {exc}")
            time.sleep(delay)
    print("Database never became ready - exiting.")
    sys.exit(1)

asyncio.run(wait_for_db())
PYEOF

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding initial data (idempotent)..."
python -m scripts.seed || echo "Seed step failed or was skipped - continuing startup."

echo "Starting application..."
exec "$@"
