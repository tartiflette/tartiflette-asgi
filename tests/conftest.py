import os

import pytest
from tartiflette import Engine


# NOTE: must be session-scoped to prevent redefining GraphQL types.
@pytest.fixture(scope="session")
def engine() -> Engine:
    sdl = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdl")
    return Engine(sdl, modules=["tests.resolvers"])
