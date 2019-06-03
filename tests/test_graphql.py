import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp


def test_graphql_get(client: TestClient):
    response = client.get("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post(client: TestClient):
    response = client.post("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_json(client: TestClient):
    response = client.post("/", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_graphql(client: TestClient):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "application/graphql"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_invalid_media_type(client: TestClient):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "dummy"}
    )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


def test_graphql_put(client: TestClient):
    response = client.put("/", json={"query": "{ hello }"})
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


def test_graphql_no_query(client: TestClient):
    response = client.get("/")
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


def test_graphql_invalid_field(client: TestClient):
    response = client.post("/", json={"query": "{ dummy }"})
    assert response.status_code == 400
    assert response.json() == {
        "data": None,
        "errors": [
            {
                "locations": [{"column": 3, "line": 1}],
                "message": (
                    "field `Query.dummy` was not found in GraphQL schema."
                ),
                "path": ["dummy"],
            }
        ],
    }


def test_graphiql_get(client: TestClient):
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


def test_graphiql_not_found(engine: Engine):
    ttftt = TartifletteApp(engine=engine, graphiql=False)
    client = TestClient(ttftt)
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_path(engine: Engine):
    ttftt = TartifletteApp(engine=engine, path="/graphql")
    client = TestClient(ttftt)
    assert client.get("/").status_code == 404
    response = client.get("/graphql?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


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
