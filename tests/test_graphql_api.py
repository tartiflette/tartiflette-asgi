import pytest
from starlette.testclient import TestClient


def test_get_querystring(client: TestClient):
    response = client.get("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


@pytest.mark.parametrize("path", ("/", "/?foo=bar", "/?q={ hello }"))
def test_get_no_query(client: TestClient, path: str):
    response = client.get(path)
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


def test_post_querystring(client: TestClient):
    response = client.post("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


def test_post_json(client: TestClient):
    response = client.post("/", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


def test_post_graphql(client: TestClient):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "application/graphql"}
    )
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


def test_post_invalid_media_type(client: TestClient):
    response = client.post(
        "/", data="{ hello }", headers={"content-type": "dummy"}
    )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


def test_put(client: TestClient):
    response = client.put("/", json={"query": "{ hello }"})
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


def test_error_handling(client: TestClient):
    response = client.post("/", json={"query": "{ dummy }"})
    assert response.status_code == 400
    json = response.json()
    assert json["data"] is None
    assert len(json["errors"]) == 1
    error = json["errors"][0]
    assert error["locations"] == [{"column": 3, "line": 1}]
    assert "dummy" in error["message"]
    assert error["path"] == ["dummy"]
