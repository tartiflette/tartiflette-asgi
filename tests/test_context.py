from starlette.applications import Starlette
from starlette.testclient import TestClient

from tartiflette_starlette import TartifletteApp


def test_graphql_context(auth_starlette: Starlette, ttftt: TartifletteApp):
    # Test the access to `context["request"]`
    # See: `whoami` resolver in `tests/resolvers.py`.
    auth_starlette.mount("/", ttftt)
    client = TestClient(auth_starlette)
    response = client.post(
        "/",
        json={"query": "{ whoami }"},
        headers={"Authorization": "Bearer 123"},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": "Jane"}, "errors": None}
