import typing

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from tartiflette import Engine

from .datastructures import GraphiQL


class GraphQLMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        engine: Engine,
        context: dict,
        graphiql: GraphiQL,
        graphql_path: str,
    ):
        super().__init__(app)
        self.kwargs = {
            "engine": engine,
            "context": context,
            "graphiql": graphiql,
            "graphql_path": graphql_path,
        }

    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        for key, value in self.kwargs.items():
            setattr(request.state, key, value)
        return await call_next(request)
