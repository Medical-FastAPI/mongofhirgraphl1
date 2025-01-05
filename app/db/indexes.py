from motor.motor_asyncio import AsyncIOMotorDatabase

async def create_indexes(db: AsyncIOMotorDatabase):
    resources = db.resources
    
    # Base indexes
    await resources.create_index("resourceType", background=True)
    await resources.create_index("id", background=True)
    await resources.create_index(
        [("resourceType", 1), ("id", 1)],
        unique=True,
        background=True
    )
    
    # Observation-specific indexes
    await resources.create_index("patient_id")
    await resources.create_index("code_loinc")
    await resources.create_index("date")
    await resources.create_index("value")
    await resources.create_index([("patient_id", 1), ("code_loinc", 1)])
    await resources.create_index([("patient_id", 1), ("date", 1)])
    await resources.create_index("meta.lastUpdated")