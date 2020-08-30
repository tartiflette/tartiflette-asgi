import typing

import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp

from ._utils import get_client


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "authorization, expected_user", [("", "a mystery"), ("Bearer 123", "Jane")]
)
async def test_access_request_from_graphql_context(
    engine: Engine,
    authorization: str,
    expected_user: str,
) -> None:
    class FakeAuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(
            self, request: Request, call_next: typing.Callable
        ) -> Response:
            request.state.user = (
                "Jane" if request.headers["authorization"] == "Bearer 123" else None
            )
            return await call_next(request)

    graphql = TartifletteApp(engine=engine)
    app = Starlette(
        routes=[Mount("/", graphql)],
        middleware=[Middleware(FakeAuthMiddleware)],
        on_startup=[graphql.startup],
    )

    async with get_client(app) as client:
        # See `tests/resolvers.py` for the `whoami` resolver.
        response = await client.post(
            "/",
            json={"query": "{ whoami }"},
            headers={"Authorization": authorization},
        )

    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": expected_user}}


@pytest.mark.asyncio
@pytest.mark.parametrize("context", (None, {"get_foo": lambda: "bar"}))
async def test_extra_context(engine: Engine, context: typing.Optional[dict]) -> None:
    app = TartifletteApp(engine=engine, context=context)

    async with get_client(app) as client:
        response = await client.post("/", json={"query": "{ foo }"})

    assert response.status_code == 200
    expected_foo = "bar" if context else "default"
    assert response.json() == {"data": {"foo": expected_foo}}
