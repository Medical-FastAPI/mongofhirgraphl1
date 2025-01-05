# app/graphql/queries/allergy_intolerance.py
from typing import List, Optional
import strawberry
from app.fhir.types.allergy_intolerance import AllergyIntolerance
from app.config.database import get_database

@strawberry.type
class AllergyIntoleranceQueries:
    @strawberry.field
    async def allergy_intolerance(self, id: str) -> Optional[AllergyIntolerance]:
        db = await get_database()
        data = await db.allergyIntolerance.find_one({"id": id, "resourceType": "AllergyIntolerance"})
        return AllergyIntolerance.from_mongo(data)

    @strawberry.field
    async def search_allergies(
        self,
        patient_id: Optional[str] = None,
        clinical_status: Optional[str] = None,
        criticality: Optional[str] = None,
        code: Optional[str] = None
    ) -> List[AllergyIntolerance]:
        db = await get_database()
        query = {"resourceType": "AllergyIntolerance"}
        
        if patient_id:
            query["patient.reference"] = f"Patient/{patient_id}"
        if clinical_status:
            query["clinicalStatus.coding.code"] = clinical_status
        if criticality:
            query["criticality"] = criticality
        if code:
            query["code.coding.code"] = code
            
        cursor = db.allergyIntolerance.find(query)
        allergies = []
        async for doc in cursor:
            allergies.append(AllergyIntolerance.from_mongo(doc))
        return allergies