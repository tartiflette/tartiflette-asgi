import typing

from starlette.routing import Route, Router
from starlette.types import Receive, Scope, Send
from tartiflette import Engine

from .datastructures import GraphiQL, GraphQLRequestState
from .endpoints import GraphiQLEndpoint, GraphQLEndpoint
from .middleware import GraphQLMiddleware


class TartifletteApp:
    def __init__(
        self,
        *,
        engine: Engine = None,
        sdl: str = None,
        graphiql: typing.Union[bool, GraphiQL] = True,
        path: str = "/",
        schema_name: str = "default",
    ):
        if engine is None:
            assert sdl, "`sdl` expected if `engine` not given"
            engine = Engine(sdl, schema_name)

        assert engine, "`engine` expected if `sdl` not given"

        if graphiql is True:
            graphiql = GraphiQL()

        routes = []

        if graphiql and graphiql.path is not None:
            routes.append(Route(path=graphiql.path, endpoint=GraphiQLEndpoint))

        graphql_route = Route(path=path, endpoint=GraphQLEndpoint)
        routes.append(graphql_route)

        self.app = GraphQLMiddleware(
            Router(routes=routes),
            state=GraphQLRequestState(
                engine=engine,
                graphiql=graphiql,
                graphql_endpoint_path=graphql_route.path,
            ),
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)
