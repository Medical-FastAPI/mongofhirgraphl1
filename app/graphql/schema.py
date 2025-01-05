# app/graphql/schema.py
import strawberry
from .queries.observation import ObservationQueries
from .queries.allergy_intolerance import AllergyIntoleranceQueries
from .mutations.observation import ObservationMutations
from .mutations.allergy_intolerance import AllergyIntoleranceMutations

@strawberry.type
class Query(ObservationQueries, AllergyIntoleranceQueries):
    pass

@strawberry.type
class Mutation(ObservationMutations, AllergyIntoleranceMutations):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)