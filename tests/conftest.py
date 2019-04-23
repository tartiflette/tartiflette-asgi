import os

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp


# NOTE: must be session-scoped to prevent redefining GraphQL types.
@pytest.fixture(name="engine", scope="session")
def fixture_engine():
    sdl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdl")
    return Engine(sdl, modules=["tests.resolvers"])


@pytest.fixture(name="app")
def fixture_app(engine):
    return TartifletteApp(engine=engine)


@pytest.fixture(name="client")
def fixture_client(app):
    return TestClient(app)


@pytest.fixture(name="starlette")
def fixture_starlette():
    return Starlette()


@pytest.fixture
def auth_starlette(starlette):
    @starlette.middleware("http")
    async def fake_auth(request, call_next):
        request.state.user = (
            "Jane"
            if request.headers.get("Authorization") == "Bearer 123"
            else None
        )
        return await call_next(request)

    return starlette
