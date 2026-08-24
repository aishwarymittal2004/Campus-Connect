import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import hash_password
from sqlalchemy import select

async def main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == 'system_reviewer@campusconnect.local'))
        user = result.scalars().first()
        if not user:
            user = User(
                name='Google Maps Reviewer',
                email='system_reviewer@campusconnect.local',
                password_hash=hash_password('system_pass_123!'),
                role=UserRole.ADMIN
            )
            session.add(user)
            await session.commit()
            print("System user created.")
        else:
            print("System user already exists.")

if __name__ == "__main__":
    asyncio.run(main())
