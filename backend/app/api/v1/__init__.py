from fastapi import APIRouter

from app.api.v1 import admin, auth, colleges, offers, reviews, routes, services, tips, places, travel

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(colleges.router)
api_router.include_router(routes.router)
api_router.include_router(places.router)
api_router.include_router(travel.router)
api_router.include_router(services.router)
api_router.include_router(tips.router)
api_router.include_router(reviews.router)
api_router.include_router(offers.router)
api_router.include_router(admin.router)
