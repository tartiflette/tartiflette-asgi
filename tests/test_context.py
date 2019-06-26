import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

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


@pytest.fixture(name="message")
def fixture_message():
    return "Hello, world"


@pytest.fixture(name="client")
def fixture_client(engine, message):
    ttftt = TartifletteApp(engine=engine, context={"message": message})
    return TestClient(ttftt)


def test_custom_context(client, message):
    response = client.post("/", json={"query": "{ message }"})
    assert response.status_code == 200
    assert response.json() == {"data": {"message": message}}


def test_custom_context_is_rebuilt_on_each_request(client, message):
    response = client.post(
        "/",
        json={
            "query": (
                "mutation { "
                'setMessage(input: { message: "Lorem ipsum" }) '
                "}"
            )
        },
    )
    assert response.status_code == 200, response.json()
    assert response.json() == {"data": {"setMessage": "Lorem ipsum"}}

    test_custom_context(client, message)
