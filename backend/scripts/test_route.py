import asyncio
import uuid
from app.core.database import AsyncSessionLocal
from app.models.college import College
from app.schemas.route import RouteSearchRequest
from app.services.route_service import RouteService
from app.repositories.route_repository import RouteRepository
from app.repositories.college_repository import CollegeRepository
from app.core.redis_client import RedisCache
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(College).where(College.name.ilike('%Madhav%')))
        college = result.scalars().first()
        if not college:
            print("College not found")
            return
            
        print(f"College: {college.name} ID: {college.id}")
        
        route_repo = RouteRepository(session)
        college_repo = CollegeRepository(session)
        cache = RedisCache()
        
        service = RouteService(route_repo, college_repo, cache)
        req = RouteSearchRequest(
            source_location="Bikaner",
            source_type="other",
            college_id=college.id,
            source_latitude=28.0229,  # Bikaner approx
            source_longitude=73.3119
        )
        
        # Bypass cache
        options = await service._compute_routes(req, college)
        for opt in options:
            if opt.transport_type == "train":
                print("TRAIN ROUTE:")
                for step in opt.steps:
                    print(f"- {step.instruction} ({step.duration_minutes}m, {step.distance_km}km)")

if __name__ == "__main__":
    asyncio.run(main())
