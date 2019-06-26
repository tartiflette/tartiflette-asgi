import typing

from tartiflette import Engine
from starlette.routing import Router, Route
from starlette.types import Scope, Receive, Send

from .datastructures import GraphiQL
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

        routes = [Route(path=path, endpoint=GraphQLEndpoint)]

        if graphiql and graphiql.path is not None:
            routes.append(Route(path=graphiql.path, endpoint=GraphiQLEndpoint))

        self.app = GraphQLMiddleware(
            Router(routes=routes), engine=engine, graphiql=graphiql
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        await self.app(scope, receive, send)
