from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB connection settings
MONGODB_URL = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.cursor3
resources = db.full_observations
counters = db.counters