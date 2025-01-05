from typing import List, Optional
import strawberry
from app.fhir.types.observation import Observation
from app.config.database import get_database

@strawberry.type
class ObservationQueries:
    @strawberry.field
    async def observation(self, id: str) -> Optional[Observation]:
        db = await get_database()
        data = await db.resources.find_one({"id": id, "resourceType": "Observation"})
        return Observation.from_mongo(data)

    @strawberry.field
    async def search_observations(
        self,
        patient_id: Optional[str] = None,
        code: Optional[str] = None,
        date: Optional[str] = None,
        value_min: Optional[float] = None,
        value_max: Optional[float] = None
    ) -> List[Observation]:
        db = await get_database()
        query = {"resourceType": "Observation"}
        
        if patient_id:
            query["patient_id"] = patient_id
        if code:
            query["code_loinc"] = code
        if date:
            query["date"] = date
        if value_min is not None or value_max is not None:
            query["value"] = {}
            if value_min is not None:
                query["value"]["$gte"] = value_min
            if value_max is not None:
                query["value"]["$lte"] = value_max
            
        cursor = db.resources.find(query)
        observations = []
        async for doc in cursor:
            observations.append(Observation.from_mongo(doc))
        return observations
