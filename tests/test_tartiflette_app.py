from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp


def test_path(engine: Engine) -> None:
    app = TartifletteApp(engine=engine, path="/graphql")

    with TestClient(app) as client:
        assert client.get("/").status_code == 404
        response = client.get("/graphql?query={ hello }")

    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}
