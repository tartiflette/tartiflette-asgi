from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import TartifletteApp


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
