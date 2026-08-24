from pydantic import BaseModel


class PlatformAnalytics(BaseModel):
    total_users: int
    total_students: int
    total_admins: int
    total_colleges: int
    total_route_searches: int
    total_bookmarked_routes: int
    total_reviews: int
    average_rating: float | None
    total_pg_listings: int
    total_active_offers: int
    most_searched_colleges: list[dict]
    transport_type_breakdown: dict[str, int]
