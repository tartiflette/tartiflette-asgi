from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Receive, Scope, Send

from ._datastructures import GraphQLConfig


class GraphQLMiddleware:
    def __init__(self, app: ASGIApp, config: GraphQLConfig):
        self.app = app
        self.config = config

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["graphql"] = self.config
        await self.app(scope, receive, send)


def get_graphql_config(conn: HTTPConnection) -> GraphQLConfig:
    config = conn["graphql"]
    assert isinstance(config, GraphQLConfig)
    return config
