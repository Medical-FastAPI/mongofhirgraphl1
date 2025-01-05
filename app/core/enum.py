from enum import Enum
import strawberry

@strawberry.enum
class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"

@strawberry.enum
class ResourceType(Enum):
    OBSERVATION = "Observation"
    PATIENT = "Patient"
    PRACTITIONER = "Practitioner"