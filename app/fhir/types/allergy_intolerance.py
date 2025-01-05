# app/fhir/types/allergy_intolerance.py
from typing import List, Optional, Dict
import strawberry
from datetime import datetime
from .base import CodeableConcept, Reference, Meta

@strawberry.type
class Age:
    value: float
    unit: str
    system: str = "http://unitsofmeasure.org"
    code: str

    @classmethod
    def from_dict(cls, data: Dict) -> 'Age':
        if not data:
            return None
        return cls(
            value=data.get('value'),
            unit=data.get('unit'),
            system=data.get('system', "http://unitsofmeasure.org"),
            code=data.get('code')
        )

@strawberry.type
class Reaction:
    manifestation: List[CodeableConcept]
    onsetAge: Optional[Age] = None

    @classmethod
    def from_dict(cls, data: Dict) -> 'Reaction':
        if not data:
            return None
        return cls(
            manifestation=[CodeableConcept.from_dict(m) for m in data.get('manifestation', [])],
            onsetAge=Age.from_dict(data.get('onsetAge')) if data.get('onsetAge') else None
        )

@strawberry.type
class AllergyIntolerance:
    id: str
    resourceType: str = "AllergyIntolerance"
    meta: Meta
    code: CodeableConcept
    clinicalStatus: CodeableConcept
    verificationStatus: CodeableConcept
    patient: Reference
    criticality: str
    reaction: Optional[List[Reaction]] = None
    recordedDate: str

    @classmethod
    def from_mongo(cls, data: Dict) -> Optional['AllergyIntolerance']:
        if not data:
            return None
            
        return cls(
            id=str(data.get('id')),
            meta=Meta.from_dict(data.get('meta', {})),
            code=CodeableConcept.from_dict(data.get('code', {})),
            clinicalStatus=CodeableConcept.from_dict(data.get('clinicalStatus', {})),
            verificationStatus=CodeableConcept.from_dict(data.get('verificationStatus', {})),
            patient=Reference.from_dict(data.get('patient', {})),
            criticality=data.get('criticality'),
            reaction=[Reaction.from_dict(r) for r in data.get('reaction', [])] if data.get('reaction') else None,
            recordedDate=data.get('recordedDate')
        )