# app/graphql/mutations/allergy_intolerance.py
from typing import List, Optional
import strawberry
from datetime import datetime
from bson import ObjectId
from app.fhir.types.allergy_intolerance import AllergyIntolerance
from app.config.database import get_database
from app.db.versioning import VersionManager

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
    async def create_allergy_intolerance(
        self, 
        allergy_data: AllergyIntoleranceInput
    ) -> AllergyIntolerance:
        db = await get_database()
        
        # Prepare the allergy document
        allergy_doc = {
            "resourceType": "AllergyIntolerance",
            "meta": {
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
                        "code": reaction.onset_age_unit[0]
                    }
                allergy_doc["reaction"].append(reaction_data)

        # Create versioned resource
        result = await VersionManager.create_versioned_resource(
            db=db,
            resource_type="AllergyIntolerance",
            data=allergy_doc
        )

        return AllergyIntolerance.from_mongo(result)

    @strawberry.mutation
    async def update_allergy_intolerance(
        self,
        id: str,
        allergy_data: AllergyIntoleranceInput,
        is_major_update: bool = False
    ) -> AllergyIntolerance:
        db = await get_database()
        
        # Prepare the updated allergy document
        updated_doc = {
            "resourceType": "AllergyIntolerance",
            "meta": {
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

        if allergy_data.reactions:
            updated_doc["reaction"] = []
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
                        "code": reaction.onset_age_unit[0]
                    }
                updated_doc["reaction"].append(reaction_data)

        # Update versioned resource
        result = await VersionManager.update_versioned_resource(
            db=db,
            resource_type="AllergyIntolerance",
            id=id,
            data=updated_doc,
            is_major_update=is_major_update
        )

        return AllergyIntolerance.from_mongo(result)

    @strawberry.mutation
    async def delete_allergy_intolerance(self, id: str) -> bool:
        db = await get_database()
        # Delete from both main and history collections
        result1 = await db.allergyintolerance.delete_one({"id": id})
        result2 = await db.allergyintolerance_history.delete_many({"id": id})
        return result1.deleted_count > 0