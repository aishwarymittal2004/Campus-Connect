import asyncio
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.college import College
from app.models.pg_listing import LocalService, LocalServiceCategory

async def backfill():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(College))
        colleges = result.scalars().all()
        for c in colleges:
            # Check if cafe already exists
            res_c = await session.execute(select(LocalService).where(LocalService.college_id == c.id, LocalService.category == LocalServiceCategory.CAFE))
            if not res_c.scalars().first():
                session.add(LocalService(college_id=c.id, category=LocalServiceCategory.CAFE, name="Campus Cafe", address="Student Activity Center", latitude=c.latitude, longitude=c.longitude))
            
            res_h = await session.execute(select(LocalService).where(LocalService.college_id == c.id, LocalService.category == LocalServiceCategory.HOTEL))
            if not res_h.scalars().first():
                session.add(LocalService(college_id=c.id, category=LocalServiceCategory.HOTEL, name="Comfort Inn Hotel", address="Main Road", latitude=c.latitude, longitude=c.longitude))
        await session.commit()
        print("Backfill complete")

if __name__ == "__main__":
    asyncio.run(backfill())
