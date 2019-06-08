import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient

from tartiflette_starlette import TartifletteApp


@pytest.mark.parametrize(
    "authorization, expected_user",
    [(None, "a mystery"), ("Bearer 123", "Jane")],
)
def test_access_request_from_graphql_context(
    auth_starlette: Starlette,
    ttftt: TartifletteApp,
    authorization: str,
    expected_user: str,
):
    # See also: `tests/resolvers.py` for the `whoami` resolver.
    auth_starlette.mount("/", ttftt)
    client = TestClient(auth_starlette)
    response = client.post(
        "/",
        json={"query": "{ whoami }"},
        headers={"Authorization": authorization},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": expected_user}}
