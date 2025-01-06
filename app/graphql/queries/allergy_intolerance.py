# app/graphql/queries/allergy_intolerance.py
from typing import List, Optional
import strawberry
from app.fhir.types.allergy_intolerance import AllergyIntolerance
from app.config.database import get_database
from app.db.versioning import VersionManager

@strawberry.type
class AllergyIntoleranceQueries:
    @strawberry.field
    async def allergy_intolerance(self, id: str) -> Optional[AllergyIntolerance]:
        db = await get_database()
        data = await db.allergyintolerance.find_one({"id": id})
        return AllergyIntolerance.from_mongo(data)

    @strawberry.field
    async def allergy_intolerance_version(
        self, 
        id: str, 
        version: str
    ) -> Optional[AllergyIntolerance]:
        db = await get_database()
        data = await VersionManager.get_version(
            db=db,
            resource_type="AllergyIntolerance",
            id=id,
            version=version
        )
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
            
        cursor = db.allergyintolerance.find(query)
        allergies = []
        async for doc in cursor:
            allergies.append(AllergyIntolerance.from_mongo(doc))
        return allergies

    @strawberry.field
    async def allergy_intolerance_history(self, id: str) -> List[AllergyIntolerance]:
        """Get version history of an allergy intolerance resource"""
        db = await get_database()
        history = await VersionManager.get_resource_history(
            db=db,
            resource_type="AllergyIntolerance",
            id=id
        )
        return [AllergyIntolerance.from_mongo(doc) for doc in history]