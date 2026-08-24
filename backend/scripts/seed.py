"""
Idempotent seed script.

Run with:  python -m scripts.seed
(or automatically via the `backend` container's entrypoint.sh on first boot)

Creates:
  - One admin account (from FIRST_ADMIN_EMAIL / FIRST_ADMIN_PASSWORD)
  - A handful of demo colleges, PG listings, local services, and offers
    so a fresh install of Campus Connect isn't completely empty.

Safe to run multiple times - it checks for existing rows before inserting.
"""
import asyncio
from datetime import date, timedelta

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.logging_config import get_logger
from app.core.security import hash_password
from app.models.college import College
from app.models.offer import Offer, OfferCategory, OfferPlatform
from app.models.pg_listing import LocalService, LocalServiceCategory, PGListing
from app.models.user import User, UserRole

logger = get_logger(__name__)

DEMO_COLLEGES = [
    {
        "name": "Rajiv Gandhi Institute of Petroleum Technology",
        "city": "Amethi",
        "state": "Uttar Pradesh",
        "address": "Jais, Amethi, Uttar Pradesh 229304",
        "latitude": 26.2358,
        "longitude": 81.6486,
        "nearby_landmarks": [
            {"name": "Jais Railway Station", "type": "railway_station", "distance_km": 3.5},
            {"name": "Amethi Bus Stand", "type": "bus_stand", "distance_km": 8.0},
        ],
        "emergency_contacts": [
            {"label": "Campus Security", "phone": "+91-9999900001"},
            {"label": "Warden Office", "phone": "+91-9999900002"},
        ],
        "tags": ["engineering", "ministry-of-petroleum"],
    },
    {
        "name": "Indian Institute of Technology Lucknow Extension",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "address": "Lucknow, Uttar Pradesh",
        "latitude": 26.8467,
        "longitude": 80.9462,
        "nearby_landmarks": [
            {"name": "Lucknow Charbagh Railway Station", "type": "railway_station", "distance_km": 6.0},
            {"name": "Chaudhary Charan Singh Airport", "type": "airport", "distance_km": 14.0},
        ],
        "emergency_contacts": [{"label": "Campus Security", "phone": "+91-9999900003"}],
        "tags": ["engineering"],
    },
]

DEMO_OFFERS = [
    {
        "platform": OfferPlatform.ZOMATO,
        "category": OfferCategory.FOOD,
        "title": "Flat 50% off on your first 3 orders",
        "description": "New user offer for students ordering near campus.",
        "discount": "50% OFF",
        "promo_code": "ZOMSTUDENT50",
        "url": "https://www.zomato.com/",
        "expiry_date": date.today() + timedelta(days=60),
        "student_only": True,
    },
    {
        "platform": OfferPlatform.SWIGGY,
        "category": OfferCategory.FOOD,
        "title": "Free delivery on orders above ₹149",
        "description": "Applicable at select restaurants near hostels.",
        "discount": "Free Delivery",
        "promo_code": None,
        "url": "https://www.swiggy.com/",
        "expiry_date": date.today() + timedelta(days=45),
        "student_only": False,
    },
    {
        "platform": OfferPlatform.AMAZON,
        "category": OfferCategory.SHOPPING,
        "title": "Amazon Prime Student - 90 day free trial",
        "description": "Free fast delivery and Prime Video for verified students.",
        "discount": "90 days free",
        "promo_code": None,
        "url": "https://www.amazon.in/amazonprime",
        "expiry_date": None,
        "student_only": True,
    },
    {
        "platform": OfferPlatform.FLIPKART,
        "category": OfferCategory.SHOPPING,
        "title": "Extra 10% off on electronics with SBI cards",
        "description": "Applicable during Big Billion Days and select sales.",
        "discount": "10% OFF",
        "promo_code": None,
        "url": "https://www.flipkart.com/",
        "expiry_date": date.today() + timedelta(days=90),
        "student_only": False,
    },
]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        # --- Admin user ---
        result = await session.execute(select(User).where(User.email == settings.FIRST_ADMIN_EMAIL.lower()))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                name="Campus Connect Admin",
                email=settings.FIRST_ADMIN_EMAIL.lower(),
                password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
                role=UserRole.ADMIN,
            )
            session.add(admin)
            logger.info("seed_admin_created", email=settings.FIRST_ADMIN_EMAIL)
        else:
            logger.info("seed_admin_exists", email=settings.FIRST_ADMIN_EMAIL)

        # --- Demo colleges ---
        college_ids = {}
        for college_data in DEMO_COLLEGES:
            result = await session.execute(select(College).where(College.name == college_data["name"]))
            college = result.scalar_one_or_none()
            if not college:
                college = College(**college_data)
                session.add(college)
                await session.flush()
                logger.info("seed_college_created", name=college.name)
            college_ids[college.name] = college.id

        rgipt_id = college_ids.get(DEMO_COLLEGES[0]["name"])

        # --- Demo PG listing + local services (attached to the first college) ---
        if rgipt_id:
            result = await session.execute(select(PGListing).where(PGListing.college_id == rgipt_id))
            if not result.scalars().first():
                session.add_all(
                    [
                        PGListing(
                            college_id=rgipt_id,
                            name="Shanti Boys PG",
                            address="Near Jais Railway Station Road, Amethi",
                            rent=6000,
                            contact="+91-9876500001",
                            amenities=["wifi", "laundry", "mess"],
                            has_mess=True,
                            gender_preference="male",
                            distance_from_college_km=1.2,
                            is_verified=True,
                        ),
                        PGListing(
                            college_id=rgipt_id,
                            name="Green Valley Girls Hostel",
                            address="College Road, Jais, Amethi",
                            rent=7500,
                            contact="+91-9876500002",
                            amenities=["wifi", "security", "mess"],
                            has_mess=True,
                            gender_preference="female",
                            distance_from_college_km=0.8,
                            is_verified=True,
                        ),
                    ]
                )
                logger.info("seed_pg_listings_created", college_id=str(rgipt_id))

            result = await session.execute(select(LocalService).where(LocalService.college_id == rgipt_id))
            if not result.scalars().first():
                session.add_all(
                    [
                        LocalService(
                            college_id=rgipt_id,
                            category=LocalServiceCategory.MEDICAL_STORE,
                            name="Jais Medical Store",
                            address="Main Market, Jais",
                            contact="+91-9876500010",
                            distance_from_college_km=1.5,
                            opening_hours="8:00 AM - 10:00 PM",
                        ),
                        LocalService(
                            college_id=rgipt_id,
                            category=LocalServiceCategory.ATM,
                            name="SBI ATM - Jais Branch",
                            address="Jais Main Road",
                            distance_from_college_km=1.8,
                        ),
                        LocalService(
                            college_id=rgipt_id,
                            category=LocalServiceCategory.GROCERY,
                            name="Campus Grocery Mart",
                            address="Near College Gate",
                            distance_from_college_km=0.3,
                            opening_hours="7:00 AM - 11:00 PM",
                        ),
                    ]
                )
                logger.info("seed_local_services_created", college_id=str(rgipt_id))

        # --- Demo offers ---
        result = await session.execute(select(Offer))
        if not result.scalars().first():
            session.add_all([Offer(**offer_data) for offer_data in DEMO_OFFERS])
            logger.info("seed_offers_created", count=len(DEMO_OFFERS))

        await session.commit()
        logger.info("seed_complete")


if __name__ == "__main__":
    asyncio.run(seed())
