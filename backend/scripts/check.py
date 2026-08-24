import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.models.pg_listing import PGListing
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(PGListing))
        pgs = result.scalars().all()
        print(f"Total PGs: {len(pgs)}")
        for pg in pgs:
            print(f"PG: {pg.name} for college {pg.college_id}")

if __name__ == "__main__":
    asyncio.run(main())
