from fastapi import FastAPI
import strawberry
from strawberry.asgi import GraphQL
from typing import List, Optional, Dict, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from bson import ObjectId
import random
from contextlib import asynccontextmanager
from enum import Enum 
from app.db.indexes import create_indexes

# MongoDB connection settings
MONGODB_URL = "mongodb://mongo:UmxHXTOOXKBaiFQUnsawgcTQSmwkOHBw@autorack.proxy.rlwy.net:54479"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.cursor3
resources = db.full_observations
counters = db.counters

# LOINC Codes for vital signs and anthropometric measurements
VITAL_CODES = {
    "blood_pressure_systolic": {
        "code": "8480-6",
        "display": "Systolic blood pressure",
        "unit": "mm[Hg]"
    },
    "blood_pressure_diastolic": {
        "code": "8462-4",
        "display": "Diastolic blood pressure",
        "unit": "mm[Hg]"
    },
    "heart_rate": {
        "code": "8867-4",
        "display": "Heart rate",
        "unit": "/min"
    },
    "body_temperature": {
        "code": "8310-5",
        "display": "Body temperature",
        "unit": "Cel"
    },
    "respiratory_rate": {
        "code": "9279-1",
        "display": "Respiratory rate",
        "unit": "/min"
    },
    "oxygen_saturation": {
        "code": "2708-6",
        "display": "Oxygen saturation",
        "unit": "%"
    },
    "body_weight": {
        "code": "29463-7",
        "display": "Body weight",
        "unit": "kg"
    },
    "body_height": {
        "code": "8302-2",
        "display": "Body height",
        "unit": "cm"
    },
    "bmi": {
        "code": "39156-5",
        "display": "Body mass index",
        "unit": "kg/m2"
    }
}

# SNOMED CT codes for observation methods
METHODS = {
    "automatic": "702869007",  # Automatic blood pressure reading
    "manual": "37931006",      # Manual blood pressure reading
    "auscultation": "113011001", # Auscultation
    "calculated": "703858009",  # Calculated
}

# Value ranges for random generation
VALUE_RANGES = {
    "blood_pressure_systolic": (90, 180),
    "blood_pressure_diastolic": (60, 120),
    "heart_rate": (60, 100),
    "body_temperature": (36.0, 38.0),
    "respiratory_rate": (12, 20),
    "oxygen_saturation": (94, 100),
    "body_weight": (45.0, 120.0),
    "body_height": (150.0, 190.0),
    "bmi": (18.5, 35.0)
}

# Define the enum properly by inheriting from Enum
class SortOrderEnum(Enum):
    ASC = "asc"
    DESC = "desc"

# Now create the Strawberry enum type
SortOrder = strawberry.enum(SortOrderEnum)

@strawberry.input
class ObservationFilter:
    patient_id: Optional[str] = None
    code: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    value_min: Optional[float] = None
    value_max: Optional[float] = None
    status: Optional[str] = None
    category: Optional[str] = None

@strawberry.input
class ObservationSort:
    field: str
    order: SortOrder = SortOrder.ASC  # Now using the properly defined enum


@strawberry.type
class Coding:
    system: str
    code: str
    display: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'Coding':
        return cls(
            system=data.get('system'),
            code=data.get('code'),
            display=data.get('display')
        )

@strawberry.type
class CodeableConcept:
    coding: List[Coding]
    text: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> 'CodeableConcept':
        return cls(
            coding=[Coding.from_dict(c) for c in data.get('coding', [])],
            text=data.get('text')
        )

@strawberry.type
class Quantity:
    value: float
    unit: str
    system: str = "http://unitsofmeasure.org"
    code: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'Quantity':
        return cls(
            value=data.get('value'),
            unit=data.get('unit'),
            system=data.get('system', "http://unitsofmeasure.org"),
            code=data.get('code')
        )

@strawberry.type
class Reference:
    reference: str
    type: str = "Patient"

    @classmethod
    def from_dict(cls, data: Dict) -> 'Reference':
        return cls(
            reference=data.get('reference'),
            type=data.get('type', "Patient")
        )

@strawberry.type
class Meta:
    versionId: str
    lastUpdated: str
    source: Optional[str]
    profile: Optional[List[str]]

    @classmethod
    def from_dict(cls, data: Dict) -> 'Meta':
        return cls(
            versionId=data.get('versionId', '1'),
            lastUpdated=data.get('lastUpdated'),
            source=data.get('source'),
            profile=data.get('profile')
        )

# Now we can define Component
@strawberry.type
class Component:
    code: CodeableConcept
    valueQuantity: Quantity

    @classmethod
    def from_dict(cls, data: Dict) -> 'Component':
        return cls(
            code=CodeableConcept.from_dict(data.get('code', {})),
            valueQuantity=Quantity.from_dict(data.get('valueQuantity', {}))
        )

# Finally, the Observation type that uses all the above
@strawberry.type
class Observation:
    id: str
    resourceType: str = "Observation"
    meta: Meta
    status: str
    category: List[CodeableConcept]
    code: CodeableConcept
    subject: Reference
    effectiveDateTime: str
    valueQuantity: Optional[Quantity] = None
    method: Optional[CodeableConcept] = None
    component: Optional[List[Component]] = None
    performer: Optional[List[Reference]] = None
    device: Optional[Reference] = None

    @classmethod
    def from_mongo(cls, data: Dict) -> Optional['Observation']:
        if not data:
            return None
            
        return cls(
            id=str(data.get('id')),
            meta=Meta.from_dict(data.get('meta', {})),
            status=data.get('status'),
            category=[CodeableConcept.from_dict(c) for c in data.get('category', [])],
            code=CodeableConcept.from_dict(data.get('code', {})),
            subject=Reference.from_dict(data.get('subject', {})),
            effectiveDateTime=data.get('effectiveDateTime'),
            valueQuantity=Quantity.from_dict(data.get('valueQuantity', {})) if data.get('valueQuantity') else None,
            method=CodeableConcept.from_dict(data.get('method', {})) if data.get('method') else None,
            component=[Component.from_dict(c) for c in data.get('component', [])] if data.get('component') else None,
            performer=[Reference.from_dict(p) for p in data.get('performer', [])] if data.get('performer') else None,
            device=Reference.from_dict(data.get('device')) if data.get('device') else None
        )

    

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_random_vital_signs_panel(self, patient_id: str) -> Observation:
        # Generate a new ObjectId for the observation
        _id = str(ObjectId())
        
        # Get counter for versioning
        counter = await counters.find_one_and_update(
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

        await resources.insert_one(observation_doc)
        #observations.append(Observation.from_mongo(observation_doc))
            
        return Observation.from_mongo(observation_doc)

@strawberry.type
class Query:
    @strawberry.field
    async def observation(self, id: str) -> Optional[Observation]:
        data = await resources.find_one({"id": id, "resourceType": "Observation"})
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
            
        cursor = resources.find(query)
        observations = []
        async for doc in cursor:
            observations.append(Observation.from_mongo(doc))
        return observations

# Application Lifecycle Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown:
    - Tests database connection
    - Creates database indexes
    - Closes database connection on shutdown
    """
    try:
        # Startup: Test database connection
        print("Testing database connection...")
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
        
        # Create necessary database indexes
        print("Creating indexes...")
        await create_indexes()
        print("Indexes created successfully")
        
        yield  # Application runs here
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise e
    finally:
        # Shutdown: Close database connection
        print("Shutting down...")
        client.close()

# Initialize FastAPI application with lifecycle manager
app = FastAPI(lifespan=lifespan)

# Create GraphQL Schema
# Combines queries and mutations into a single schema
schema = strawberry.Schema(
    query=Query,  # All query resolvers
    mutation=Mutation  # All mutation resolvers
)

# Create GraphQL application instance
graphql_app = GraphQL(schema)

# Mount GraphQL endpoints to FastAPI
app.add_route("/graphql", graphql_app)  # HTTP endpoint for GraphQL queries/mutations
app.add_websocket_route("/graphql", graphql_app)  # WebSocket endpoint for subscriptions

# Development server configurations
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)