import typing

from starlette.routing import Lifespan, Route, Router, WebSocketRoute
from starlette.types import Receive, Scope, Send
from tartiflette import Engine

from .datastructures import GraphiQL, GraphQLConfig, Subscriptions
from .endpoints import GraphiQLEndpoint, GraphQLEndpoint, SubscriptionEndpoint
from .middleware import GraphQLMiddleware


class TartifletteApp:
    def __init__(
        self,
        *,
        engine: Engine = None,
        sdl: str = None,
        graphiql: typing.Union[bool, GraphiQL] = True,
        path: str = "/",
        subscriptions: typing.Union[bool, Subscriptions] = None,
        context: dict = None,
        schema_name: str = "default",
    ):
        if engine is None:
            assert sdl, "`sdl` expected if `engine` not given"
            engine = Engine(sdl=sdl, schema_name=schema_name)

        assert engine, "`engine` expected if `sdl` not given"

        self.engine = engine

        if context is None:
            context = {}

        if graphiql is True:
            graphiql = GraphiQL()

        if subscriptions is True:
            subscriptions = Subscriptions(path="/subscriptions")

        routes = []

        if graphiql and graphiql.path is not None:
            routes.append(Route(path=graphiql.path, endpoint=GraphiQLEndpoint))

        graphql_route = Route(path=path, endpoint=GraphQLEndpoint)
        routes.append(graphql_route)

        if subscriptions is not None:
            subscription_route = WebSocketRoute(
                path=subscriptions.path, endpoint=SubscriptionEndpoint
            )
            routes.append(subscription_route)

        config = GraphQLConfig(
            engine=self.engine,
            context=context,
            graphiql=graphiql,
            path=graphql_route.path,
            subscriptions=subscriptions,
        )

        router = Router(routes=routes)
        self.app = GraphQLMiddleware(router, config=config)
        self.lifespan = Lifespan(on_startup=self.startup)

        self._started_up = False

    async def startup(self):
        await self.engine.cook()
        self._started_up = True

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "lifespan":
            await self.lifespan(scope, receive, send)
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
