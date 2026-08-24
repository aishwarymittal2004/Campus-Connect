import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.models.college import College
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(College).where(College.name.ilike('%Nagpur%')))
        cols = result.scalars().all()
        for c in cols:
            print(f"College: {c.name} ID: {c.id}")

if __name__ == "__main__":
    asyncio.run(main())
