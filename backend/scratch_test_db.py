import asyncio
from app.core.database import async_session_maker
from sqlalchemy import text

async def test_db():
    try:
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1"))
            print("DB OK:", result.scalar())
    except Exception as e:
        print("DB ERROR:", str(e))

asyncio.run(test_db())
