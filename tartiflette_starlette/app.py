import typing

from tartiflette import Engine

from .graphql import GraphQLHandler


class TartifletteApp:
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

        self.handler = GraphQLHandler(engine, graphiql=graphiql)

    async def __call__(
        self, scope: dict, receive: typing.Callable, send: typing.Callable
    ):
        response = await self.handler(scope, receive)
        await response(scope, receive, send)
