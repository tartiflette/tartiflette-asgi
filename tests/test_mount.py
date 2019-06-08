import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp

from ._utils import omit_none


@pytest.mark.parametrize("mount_path", ("/", "/graphql"))
@pytest.mark.parametrize("path", [None, "", "/", "/graphql", "/graphql/"])
def test_starlette_mount(
    starlette: Starlette, engine: Engine, mount_path: str, path: str
):
    kwargs = omit_none({"engine": engine, "path": path})

    app = TartifletteApp(**kwargs)
    starlette.mount(mount_path, app)

    client = TestClient(starlette)

    query = "{ hello }"
    full_path = mount_path.rstrip("/") + ("/" if path is None else path)
    assert "//" not in full_path

    response = client.get(f"{full_path}?query={query}")
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}
