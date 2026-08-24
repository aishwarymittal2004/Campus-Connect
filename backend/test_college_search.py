import asyncio
from app.core.database import AsyncSessionLocal
from app.repositories.college_repository import CollegeRepository
from app.services.college_service import CollegeService

async def main():
    async with AsyncSessionLocal() as session:
        repo = CollegeRepository(session)
        svc = CollegeService(repo)
        try:
            res = await svc.search('IIT delhi', 0, 10)
            print("Results:", res)
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
