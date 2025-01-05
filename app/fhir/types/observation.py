from typing import List, Optional, Dict
import strawberry
from .base import CodeableConcept, Quantity, Reference, Meta

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