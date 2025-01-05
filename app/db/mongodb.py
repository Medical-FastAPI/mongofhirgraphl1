from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database

async def get_db() -> AsyncIOMotorDatabase:
    return await get_database()
