import uuid
import asyncio

from app.core.exceptions import NotFoundError
from app.repositories.college_repository import CollegeRepository
from app.schemas.college import CollegeCreate, CollegeUpdate


class CollegeService:
    def __init__(self, college_repo: CollegeRepository):
        self.college_repo = college_repo

    async def create(self, payload: CollegeCreate):
        return await self.college_repo.create(
            name=payload.name,
            city=payload.city,
            state=payload.state,
            address=payload.address,
            latitude=payload.latitude,
            longitude=payload.longitude,
            nearby_landmarks=[l.model_dump() for l in payload.nearby_landmarks],
            emergency_contacts=[c.model_dump() for c in payload.emergency_contacts],
            website=payload.website,
            tags=payload.tags,
        )

    async def get(self, college_id: uuid.UUID):
        college = await self.college_repo.get_by_id(college_id)
        if not college:
            raise NotFoundError("College not found.")
        return college

    async def list(self, offset: int, limit: int):
        return await self.college_repo.list(offset=offset, limit=limit, order_by=None)

    async def search(self, query: str, offset: int, limit: int):
        results = await self.college_repo.search(query, offset=offset, limit=limit)
        
        # If we didn't find anything locally, try fetching from Google Places Text Search dynamically
        if not results and offset == 0 and len(query) >= 3:
            from app.core.config import settings
            import httpx
            import asyncio
            
            if settings.GOOGLE_MAPS_API_KEY:
                try:
                    async with httpx.AsyncClient(timeout=8.0) as client:
                        payload = {
                            "textQuery": f"{query} college university institute",
                            "locationBias": {
                                "circle": {
                                    "center": {"latitude": 20.5937, "longitude": 78.9629}, # India center approx
                                    "radius": 50000.0
                                }
                            }
                        }
                        headers = {
                            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
                            "X-Goog-FieldMask": "places.id,places.displayName,places.location,places.formattedAddress"
                        }
                        
                        resp = await client.post(
                            "https://places.googleapis.com/v1/places:searchText",
                            json=payload,
                            headers=headers
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        
                        if data.get("places"):
                            imported_names = []
                            # take the top 3 and insert them
                            for place in data["places"][:3]:
                                name = place.get("displayName", {}).get("text", "")
                                lat = place.get("location", {}).get("latitude")
                                lng = place.get("location", {}).get("longitude")
                                address = place.get("formattedAddress", "")
                                
                                if name:
                                    imported_names.append(name)
                                
                                # Try to extract city and state from address roughly
                                parts = address.split(",")
                                city = parts[-3].strip() if len(parts) >= 3 else "Unknown"
                                state = parts[-2].strip() if len(parts) >= 2 else "Unknown"
                                
                                existing = await self.college_repo.search(name, 0, 1)
                                if not existing:
                                    try:
                                        payload_create = CollegeCreate(
                                            name=name[:120],
                                            city=city[:60],
                                            state=state[:60],
                                            address=address,
                                            latitude=lat,
                                            longitude=lng,
                                            nearby_landmarks=[],
                                            emergency_contacts=[],
                                            website=None,
                                            tags=["auto_imported"]
                                        )
                                        new_college = await self.create(payload_create)
                                        
                                        # Trigger enrichment in background
                                        from app.services.enrichment_service import enrich_college_data
                                        place_id = place.get("name") # Wait, Places API v1 uses 'name' for the resource name which is 'places/PLACE_ID'
                                        # Actually in Places API v1, place.id is the place_id. Let's get it.
                                        real_place_id = place.get("id")
                                        if real_place_id:
                                            asyncio.create_task(enrich_college_data(new_college.id, real_place_id, lat, lng))
                                    except Exception:
                                        pass
                                        
                            # Re-run local search now that we imported
                            results = await self.college_repo.search(query, offset=offset, limit=limit)
                            
                            # If the query (e.g. "IIT Delhi") didn't literally substring-match the full name 
                            # (e.g. "Indian Institute..."), manually fetch the ones we just imported to return them!
                            if not results and imported_names:
                                for n in imported_names:
                                    res = await self.college_repo.search(n, 0, 1)
                                    if res:
                                        results.extend(res)
                except Exception:
                    pass

        return results

    async def update(self, college_id: uuid.UUID, payload: CollegeUpdate):
        college = await self.get(college_id)
        data = payload.model_dump(exclude_unset=True)
        if "nearby_landmarks" in data and data["nearby_landmarks"] is not None:
            data["nearby_landmarks"] = [l if isinstance(l, dict) else l.model_dump() for l in payload.nearby_landmarks]
        if "emergency_contacts" in data and data["emergency_contacts"] is not None:
            data["emergency_contacts"] = [c if isinstance(c, dict) else c.model_dump() for c in payload.emergency_contacts]
        return await self.college_repo.update(college, **data)

    async def delete(self, college_id: uuid.UUID) -> None:
        college = await self.get(college_id)
        await self.college_repo.delete(college)
