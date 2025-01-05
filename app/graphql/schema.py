import strawberry
from .queries.observation import ObservationQueries
from .mutations.observation import ObservationMutations

@strawberry.type
class Query(ObservationQueries):
    pass

@strawberry.type
class Mutation(ObservationMutations):
    pass

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)