from typing import Optional
import strawberry
from datetime import datetime
from bson import ObjectId
from app.fhir.types.observation import Observation
from app.core.constants import VITAL_CODES, VALUE_RANGES
from app.config.database import get_database
import random

@strawberry.type
class ObservationMutations:
    @strawberry.mutation
    async def create_random_vital_signs_panel(self, patient_id: str) -> Observation:
        db = await get_database()
        
        # Generate a new ObjectId for the observation
        _id = str(ObjectId())
        
        # Get counter for versioning
        counter = await db.counters.find_one_and_update(
            {"_id": "Observation"},
            {"$inc": {"next": 1}},
            upsert=True,
            return_document=True
        )
        
        # Create meta information
        meta = {
            "versionId": str(counter["next"]),
            "lastUpdated": datetime.utcnow().isoformat(),
            "source": f"urn:uuid:{_id}",
            "profile": ["http://hl7.org/fhir/StructureDefinition/vitalsigns"]
        }
        
        # Generate components for each vital sign
        components = []
        for vital_type, vital_info in VITAL_CODES.items():
            # Generate random value within appropriate range
            value = random.uniform(*VALUE_RANGES[vital_type])
            if vital_type not in ['body_temperature', 'bmi']:
                value = round(value)
            else:
                value = round(value, 1)
            
            component = {
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": vital_info["code"],
                        "display": vital_info["display"]
                    }]
                },
                "valueQuantity": {
                    "value": value,
                    "unit": vital_info["unit"],
                    "system": "http://unitsofmeasure.org",
                    "code": vital_info["unit"]
                }
            }
            components.append(component)
        
        # Create the complete vital signs panel observation
        observation_doc = {
            "_id": ObjectId(_id),
            "id": _id,
            "resourceType": "Observation",
            "meta": meta,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "85353-1",
                    "display": "Vital signs panel"
                }],
                "text": "Vital Signs Panel"
            },
            "subject": {
                "reference": f"Patient/{patient_id}",
                "type": "Patient"
            },
            "effectiveDateTime": datetime.utcnow().isoformat(),
            "performer": [{
                "reference": "Practitioner/example",
                "display": "Nurse Practitioner"
            }],
            "device": {
                "reference": "Device/vital-signs-monitor",
                "display": "Vital Signs Monitor"
            },
            "component": components,
            # Flattened search fields
            "patient_id": patient_id,
            "date": datetime.utcnow().isoformat()[:10]  # YYYY-MM-DD
        }

        await db.observations.insert_one(observation_doc)
        return Observation.from_mongo(observation_doc)

    @strawberry.mutation
    async def delete_observation(self, id: str) -> bool:
        db = await get_database()
        result = await db.observations.delete_one({"id": id, "resourceType": "Observation"})
        return result.deleted_count > 0
