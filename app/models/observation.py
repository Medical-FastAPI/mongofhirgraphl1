import strawberry
from typing import List, Optional, Dict
from datetime import datetime

@strawberry.type
class Coding:
    system: str
    code: str
    display: str

@strawberry.type
class CodeableConcept:
    coding: List[Coding]
    text: Optional[str]

@strawberry.type
class Quantity:
    value: float
    unit: str
    system: str
    code: str

@strawberry.type
class Reference:
    reference: str
    type: str

@strawberry.type
class Meta:
    versionId: str
    lastUpdated: str
    source: Optional[str]
    profile: Optional[List[str]]

@strawberry.type
class Component:
    code: CodeableConcept
    valueQuantity: Quantity

@strawberry.type
class Observation:
    id: str
    resourceType: str
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
        # Convert MongoDB document to Observation type
        return cls(**data) 