import os

import pytest
from starlette.applications import Starlette
from starlette.datastructures import Headers
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import Tartiflette


class FakeAuthMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        headers = Headers(scope=scope)
        scope["user"] = (
            "Jane" if headers.get("Authorization") == "Bearer 123" else None
        )
        await self.app(scope, receive, send)


# NOTE: must be session-scoped to prevent redefining GraphQL types.
@pytest.fixture(name="engine", scope="session")
def fixture_engine():
    sdl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdl")
    return Engine(sdl, modules=["tests.resolvers"])


@pytest.fixture(name="ttftt")
def fixture_ttftt(engine):
    return Tartiflette(engine=engine)


@pytest.fixture(name="client")
def fixture_client(ttftt):
    return TestClient(ttftt)


@pytest.fixture(name="app")
def fixture_app():
    return Starlette()


@pytest.fixture
def auth_app(app):
    app.add_middleware(FakeAuthMiddleware)
    return app
