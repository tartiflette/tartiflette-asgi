import pytest
from starlette.testclient import TestClient

from tartiflette_starlette import TartifletteApp


def test_graphql_get(client):
    response = client.get("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post(client):
    response = client.post("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_json(client):
    response = client.post("/", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_graphql(client):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "application/graphql"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_post_invalid_media_type(client):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "dummy"}
    )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


def test_graphql_put(client):
    response = client.put("/", json={"query": "{ hello }"})
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


def test_graphql_no_query(client):
    response = client.get("/")
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


def test_graphql_invalid_field(client):
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


def test_graphiql_get(client):
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text


def test_graphiql_not_found(engine):
    app = TartifletteApp(engine=engine, graphiql=False)
    client = TestClient(app)
    response = client.get("/", headers={"accept": "text/html"})
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_path(engine):
    app = TartifletteApp(engine=engine, path="/graphql")
    client = TestClient(app)
    assert client.get("/").status_code == 404
    response = client.get("/graphql?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


@pytest.mark.parametrize("path", [None, "/graphql"])
def test_starlette_mount(starlette, engine, path):
    kwargs = {"engine": engine}
    if path is not None:
        kwargs["path"] = path
    app = TartifletteApp(**kwargs)
    starlette.mount("/foo", app)
    client = TestClient(starlette)
    endpoint = "/" if path is None else path
    query = "{ hello }"
    response = client.get(f"/foo{endpoint}?query={query}")
    assert response.status_code == 200
    assert response.json() == {
        "data": {"hello": "Hello stranger"},
        "errors": None,
    }


def test_graphql_context(auth_starlette, app):
    # Test the access to `context["request"]`
    # See: `whoami` resolver in `tests/resolvers.py`.
    auth_starlette.mount("/", app)
    client = TestClient(auth_starlette)
    response = client.post(
        "/",
        json={"query": "{ whoami }"},
        headers={"Authorization": "Bearer 123"},
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"whoami": "Jane"}, "errors": None}
