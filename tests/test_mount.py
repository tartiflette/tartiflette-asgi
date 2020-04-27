import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp, mount

from ._utils import omit_none


@pytest.mark.parametrize("mount_path", ("/", "/graphql"))
@pytest.mark.parametrize("path", [None, "/", "/graphql", "/graphql/"])
def test_starlette_mount(
    starlette: Starlette, engine: Engine, mount_path: str, path: str
) -> None:
    kwargs = omit_none({"engine": engine, "path": path})

    app = TartifletteApp(**kwargs)
    mount.starlette(starlette, mount_path, app)

    query = "{ hello }"
    full_path = mount_path.rstrip("/") + ("/" if path is None else path)
    assert "//" not in full_path

    url = f"{full_path}?query={query}"
    with TestClient(starlette) as client:
        response = client.get(url)
        graphiql_response = client.get(url, headers={"accept": "text/html"})

    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}

    assert graphiql_response.status_code == 200
    assert full_path in graphiql_response.text


def test_must_register_startup_handler(
    starlette: Starlette, ttftt: TartifletteApp
) -> None:
    starlette.mount("/graphql", ttftt)

    with TestClient(starlette) as client:
        with pytest.raises(RuntimeError) as ctx:
            client.get("/graphql")

    error = str(ctx.value).lower()
    assert "hint" in error
    assert "starlette example" in error
    assert ".add_event_handler" in error
    assert "'startup'" in error
    assert ".startup" in error
