import typing

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from tartiflette import Engine

from .datastructures import GraphiQL


class GraphQLMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, engine: Engine, graphiql: GraphiQL):
        super().__init__(app)
        self.engine = engine
        self.graphiql = graphiql

    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        request.state.engine = self.engine
        request.state.graphiql = self.graphiql
        return await call_next(request)
