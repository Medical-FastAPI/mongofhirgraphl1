from . import resources

async def create_indexes():
    # Create indexes for the resources collection
    await resources.create_index([("resourceType", 1)])
    await resources.create_index([("patient_id", 1)])
    await resources.create_index([("date", 1)]) 