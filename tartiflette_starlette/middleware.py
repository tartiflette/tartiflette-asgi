import typing

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from .datastructures import GraphQLRequestState
from .helpers import StateHelper


class GraphQLMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, state: GraphQLRequestState):
        super().__init__(app)
        self.state = state

    async def dispatch(
        self,
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        StateHelper.set(request, self.state)
        return await call_next(request)
