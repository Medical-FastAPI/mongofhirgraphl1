from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .settings import get_settings
from typing import Optional

settings = get_settings()

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
async def get_database() -> AsyncIOMotorDatabase:
    if not Database.client:
        Database.client = AsyncIOMotorClient(settings.MONGODB_URL)
        Database.db = Database.client[settings.DATABASE_NAME]
    return Database.db

async def close_database():
    if Database.client:
        Database.client.close()
        Database.client = None
        Database.db = None