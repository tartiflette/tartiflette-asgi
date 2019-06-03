import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp


@pytest.mark.parametrize("path", [None, "/graphql"])
def test_starlette_mount(starlette: Starlette, engine: Engine, path: str):
    kwargs = {"engine": engine}

    if path is not None:
        kwargs["path"] = path

    ttftt = TartifletteApp(**kwargs)
    starlette.mount("/foo", ttftt)

    client = TestClient(starlette)

    endpoint = "/" if path is None else path
    query = "{ hello }"
    response = client.get(f"/foo{endpoint}?query={query}")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }
