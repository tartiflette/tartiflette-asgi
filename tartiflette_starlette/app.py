import typing

from starlette.requests import Request
from tartiflette import Engine

from .graphql import handle_graphql


class Tartiflette:
    """ASGI3 application to execute GraphQL queries using Tartiflette.

    Ships with a GraphiQL client.

    Parameters
    ----------
    engine : Engine, optional
        A Tartiflette engine.
    sdl : str, optional
        A Tartiflette engine SDL string, which must be passed if `engine`
        is not given.
        See: https://tartiflette.io/docs/api/engine
    graphiql : bool, optional
        Whether to serve the GraphiQL client to web browsers. Defauts to `True`.
    schema_name : str, optional
        Which GraphQL schema from the Tartiflette schema registry to use.
        Defaults to `"default"`.
        See: https://tartiflette.io/docs/api/schema-registry/
    """

    def __init__(
        self,
        *,
        engine: Engine = None,
        sdl: str = None,
        graphiql: bool = True,
        schema_name: str = "default",
    ):
        if engine is None:
            assert sdl, "`sdl` expected if `engine` not given"
            engine = Engine(sdl, schema_name)

        assert engine, "`engine` expected if `sdl` not given"

        self.engine = engine
        self.graphiql = graphiql

    async def __call__(
        self, scope: dict, receive: typing.Callable, send: typing.Callable
    ):
        request = Request(scope, receive=receive)
        response = await handle_graphql(
            request, engine=self.engine, enable_graphiql=self.graphiql
        )
        await response(scope, receive, send)
