import json
import typing

import pytest
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_starlette import GraphiQL, TartifletteApp


@pytest.fixture(
    name="graphiql",
    params=[False, True, GraphiQL(), GraphiQL(path="/graphql")],
)
def fixture_graphiql(request) -> typing.Union[GraphiQL, bool]:
    return request.param


def build_graphiql_client(ttftt) -> TestClient:
    client = TestClient(ttftt)
    client.headers.update({"accept": "text/html"})
    return client


@pytest.fixture(name="client")
def fixture_client(graphiql, engine: Engine) -> TestClient:
    ttftt = TartifletteApp(engine=engine, graphiql=graphiql)
    return build_graphiql_client(ttftt)


@pytest.fixture(name="path")
def fixture_path(graphiql) -> str:
    if not graphiql or graphiql is True or graphiql.path is None:
        return ""
    return graphiql.path


def test_graphiql(client: TestClient, graphiql, path):
    response = client.get(path)

    assert response.status_code == 200 if graphiql else 404

    if response.status_code == 200:
        assert "<!DOCTYPE html>" in response.text
        assert 'fetch("/",' in response.text
    else:
        assert response.text == "Not Found"


def test_graphiql_not_found(client: TestClient, path):
    response = client.get(path + "foo")
    assert response.status_code == 404
    assert response.text == "Not Found"


def test_default_variables(engine: Engine):
    variables = {"name": "Alice"}
    graphiql = GraphiQL(default_variables=variables)
    client = build_graphiql_client(
        TartifletteApp(engine=engine, graphiql=graphiql)
    )
    response = client.get("/")
    assert response.status_code == 200
    assert json.dumps(variables) in response.text
