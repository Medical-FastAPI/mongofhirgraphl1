# app/graphql/mutations/allergy_intolerance.py
from typing import List, Optional
import strawberry
from datetime import datetime
from bson import ObjectId
from app.fhir.types.allergy_intolerance import AllergyIntolerance
from app.config.database import get_database

@strawberry.input
class ManifestationInput:
    system: str
    code: str
    display: str

@strawberry.input
class ReactionInput:
    manifestation: List[ManifestationInput]
    onset_age_value: Optional[float] = None
    onset_age_unit: Optional[str] = None

@strawberry.input
class AllergyIntoleranceInput:
    patient_id: str
    code_system: str = "http://snomed.info/sct"
    code: str
    code_display: str
    clinical_status: str = "active"
    verification_status: str = "confirmed"
    criticality: str = "moderate"
    reactions: Optional[List[ReactionInput]] = None

@strawberry.type
class AllergyIntoleranceMutations:
    @strawberry.mutation
    async def create_allergy_intolerance(self, allergy_data: AllergyIntoleranceInput) -> AllergyIntolerance:
        db = await get_database()
        
        # Generate a new ObjectId
        _id = str(ObjectId())
        
        # Get counter for versioning
        counter = await db.counters.find_one_and_update(
            {"_id": "AllergyIntolerance"},
            {"$inc": {"next": 1}},
            upsert=True,
            return_document=True
        )
        
        # Create the allergy document
        allergy_doc = {
            "_id": ObjectId(_id),
            "id": _id,
            "resourceType": "AllergyIntolerance",
            "meta": {
                "versionId": str(counter["next"]),
                "lastUpdated": datetime.utcnow().isoformat(),
                "profile": ["http://hl7.org/fhir/StructureDefinition/AllergyIntolerance"]
            },
            "code": {
                "coding": [{
                    "system": allergy_data.code_system,
                    "code": allergy_data.code,
                    "display": allergy_data.code_display
                }]
            },
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical",
                    "code": allergy_data.clinical_status
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification",
                    "code": allergy_data.verification_status
                }]
            },
            "patient": {
                "reference": f"Patient/{allergy_data.patient_id}"
            },
            "criticality": allergy_data.criticality,
            "recordedDate": datetime.utcnow().isoformat()[:10]
        }

        # Add reactions if provided
        if allergy_data.reactions:
            allergy_doc["reaction"] = []
            for reaction in allergy_data.reactions:
                reaction_data = {
                    "manifestation": [
                        {
                            "coding": [{
                                "system": m.system,
                                "code": m.code,
                                "display": m.display
                            }]
                        } for m in reaction.manifestation
                    ]
                }
                if reaction.onset_age_value and reaction.onset_age_unit:
                    reaction_data["onsetAge"] = {
                        "value": reaction.onset_age_value,
                        "unit": reaction.onset_age_unit,
                        "system": "http://unitsofmeasure.org",
                        "code": reaction.onset_age_unit[0]  # First letter of unit
                    }
                allergy_doc["reaction"].append(reaction_data)

        await db.allergyIntolerance.insert_one(allergy_doc)
        return AllergyIntolerance.from_mongo(allergy_doc)

    @strawberry.mutation
    async def delete_allergy(self, id: str) -> bool:
        db = await get_database()
        result = await db.allergyIntolerance.delete_one({"id": id, "resourceType": "AllergyIntolerance"})
        return result.deleted_count > 0