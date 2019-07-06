import os
import typing

import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp

from ._utils import PubSub, pubsub

# NOTE: must be session-scoped to prevent redefining GraphQL types.
@pytest.fixture(name="engine", scope="session")
def fixture_engine() -> Engine:
    sdl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdl")
    return Engine(sdl, modules=["tests.resolvers"])


@pytest.fixture(name="pubsub", scope="session")
def fixture_pubsub() -> PubSub:
    return pubsub


@pytest.fixture(name="ttftt")
def fixture_ttftt(engine: Engine, pubsub: PubSub) -> TartifletteApp:
    return TartifletteApp(
        engine=engine,
        subscription_path="/subscriptions",
        context={"pubsub": pubsub},
    )


@pytest.fixture(name="client")
def fixture_client(ttftt: TartifletteApp) -> TestClient:
    with TestClient(ttftt) as client:
        yield client


@pytest.fixture(name="starlette")
def fixture_starlette() -> Starlette:
    return Starlette()


@pytest.fixture
def auth_starlette(starlette: Starlette) -> Starlette:
    @starlette.middleware("http")
    async def fake_auth(
        request: Request,
        call_next: typing.Callable[[Request], typing.Awaitable[Response]],
    ) -> Response:
        request.state.user = (
            "Jane"
            if request.headers.get("Authorization") == "Bearer 123"
            else None
        )
        return await call_next(request)

    return starlette
