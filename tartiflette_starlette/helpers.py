from starlette.requests import Request
from .datastructures import GraphQLRequestState


class StateHelper:
    @staticmethod
    def get(request: Request) -> GraphQLRequestState:
        return request.state.graphql

    @staticmethod
    def set(request: Request, state: GraphQLRequestState) -> None:
        request.state.graphql = state
