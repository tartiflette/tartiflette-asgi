import typing

from starlette.routing import BaseRoute, Route, Router, WebSocketRoute
from starlette.types import Receive, Scope, Send
from tartiflette import Engine

from ._datastructures import GraphiQL, GraphQLConfig, Subscriptions
from ._endpoints import GraphiQLEndpoint, GraphQLEndpoint, SubscriptionEndpoint
from ._middleware import GraphQLMiddleware


class TartifletteApp:
    def __init__(
        self,
        *,
        engine: Engine = None,
        sdl: str = None,
        graphiql: typing.Union[None, bool, GraphiQL] = True,
        path: str = "/",
        subscriptions: typing.Union[bool, Subscriptions] = None,
        context: dict = None,
        schema_name: str = "default",
    ) -> None:
        if engine is None:
            assert sdl, "`sdl` expected if `engine` not given"
            engine = Engine(sdl=sdl, schema_name=schema_name)

        assert engine, "`engine` expected if `sdl` not given"

        self.engine = engine

        if context is None:
            context = {}

        if graphiql is True:
            graphiql = GraphiQL()
        elif not graphiql:
            graphiql = None

        assert graphiql is None or isinstance(graphiql, GraphiQL)

        if subscriptions is True:
            subscriptions = Subscriptions(path="/subscriptions")
        elif not subscriptions:
            subscriptions = None

        assert subscriptions is None or isinstance(subscriptions, Subscriptions)

        routes: typing.List[BaseRoute] = []

        if graphiql and graphiql.path is not None:
            routes.append(Route(graphiql.path, GraphiQLEndpoint))

        routes.append(Route(path, GraphQLEndpoint))

        if subscriptions is not None:
            routes.append(WebSocketRoute(subscriptions.path, SubscriptionEndpoint))

        self.router = Router(routes=routes, on_startup=[self.startup])

        config = GraphQLConfig(
            engine=self.engine,
            context=context,
            graphiql=graphiql,
            path=path,
            subscriptions=subscriptions,
        )

        self.app = GraphQLMiddleware(self.router, config=config)

        self._started_up = False

    async def startup(self) -> None:
        await self.engine.cook()
        self._started_up = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "lifespan":
            await self.router.lifespan(scope, receive, send)
        else:
            if not self._started_up:
                raise RuntimeError(
                    "GraphQL engine is not ready.\n\n"
                    "HINT: you must register the startup event handler on the "
                    "parent ASGI application.\n"
                    "Starlette example:\n\n"
                    "   app.mount('/graphql', graphql)\n"
                    "   app.add_event_handler('startup', graphql.startup)"
                )
            await self.app(scope, receive, send)
