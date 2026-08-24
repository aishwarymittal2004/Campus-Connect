import asyncio
import logging
from app.core.database import AsyncSessionLocal
from app.models.college import College
from sqlalchemy import select
from app.services.enrichment_service import enrich_college_data

logging.basicConfig(level=logging.INFO)

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(College).where(College.name.ilike('%IIT Delhi%')))
        c = result.scalars().first()
        if c:
            print("Enriching college:", c.name)
            await asyncio.sleep(2)
            await enrich_college_data(c.id, "", c.latitude, c.longitude)
            print("Done")
        else:
            print("Not found")

if __name__ == "__main__":
    asyncio.run(main())
