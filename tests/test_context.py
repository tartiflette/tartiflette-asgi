import typing

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp, mount


@pytest.mark.parametrize(
    "authorization, expected_user", [(None, "a mystery"), ("Bearer 123", "Jane")]
)
def test_access_request_from_graphql_context(
    auth_starlette: Starlette,
    ttftt: TartifletteApp,
    authorization: str,
    expected_user: str,
) -> None:
    # See also: `tests/resolvers.py` for the `whoami` resolver.
    mount.starlette(auth_starlette, "/", ttftt)
    with TestClient(auth_starlette) as client:
        response = client.post(
            "/", json={"query": "{ whoami }"}, headers={"Authorization": authorization}
        )
    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": expected_user}}


@pytest.mark.parametrize("context", (None, {"get_foo": lambda: "bar"}))
def test_extra_context(engine: Engine, context: typing.Optional[dict]) -> None:
    ttftt = TartifletteApp(engine=engine, context=context)

    with TestClient(ttftt) as client:
        response = client.post("/", json={"query": "{ foo }"})

    assert response.status_code == 200
    expected_foo = "bar" if context else "default"
    assert response.json() == {"data": {"foo": expected_foo}}
