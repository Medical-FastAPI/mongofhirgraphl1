from typing import List, Optional, Dict
import strawberry

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
    type: str

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
