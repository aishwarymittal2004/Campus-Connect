import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def main():
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("ALTER TYPE transport_type ADD VALUE 'train'"))
        except Exception as e:
            print("train:", e)
        try:
            await session.execute(text("ALTER TYPE transport_type ADD VALUE 'flight'"))
        except Exception as e:
            print("flight:", e)
        await session.commit()
        print("Done.")

if __name__ == "__main__":
    asyncio.run(main())
