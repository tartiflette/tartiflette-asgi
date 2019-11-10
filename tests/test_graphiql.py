import inspect
import json
import re
import typing

import pytest
from starlette.applications import Starlette
from starlette.testclient import TestClient
from tartiflette import Engine

from tartiflette_asgi import GraphiQL, TartifletteApp, mount


@pytest.fixture(
    name="graphiql", params=[False, True, GraphiQL(), GraphiQL(path="/graphql")]
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
    with build_graphiql_client(ttftt) as client:
        yield client


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
        m = re.search(r"var (\w+) = `/`;", response.text)
        assert m is not None, response.text
        endpoint_variable_name = m.group(1)
        assert f"fetch({endpoint_variable_name}," in response.text
        assert "None" not in response.text
    else:
        assert response.text == "Not Found"


def test_graphiql_not_found(client: TestClient, path):
    response = client.get(path + "foo")
    assert response.status_code == 404
    assert response.text == "Not Found"


@pytest.fixture(name="variables")
def fixture_variables() -> dict:
    return {"name": "Alice"}


@pytest.fixture(name="query")
def fixture_query() -> str:
    return """
        query Hello($name: String) {
            hello(name: $name)
        }
    """


@pytest.fixture(name="headers")
def fixture_headers() -> dict:
    return {"Authorization": "Bearer 123"}


def test_defaults(engine: Engine, variables: dict, query: str, headers: dict):
    graphiql = GraphiQL(
        default_variables=variables, default_query=query, default_headers=headers
    )
    ttftt = TartifletteApp(engine=engine, graphiql=graphiql)

    with build_graphiql_client(ttftt) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert json.dumps(variables) in response.text
    assert inspect.cleandoc(query) in response.text
    assert json.dumps(headers) in response.text


@pytest.mark.parametrize("mount_path", ("", "/graphql"))
def test_endpoint_paths_when_mounted(
    starlette: Starlette, engine: Engine, mount_path: str
):
    ttftt = TartifletteApp(engine=engine, graphiql=True, subscriptions=True)
    mount.starlette(starlette, mount_path, ttftt)

    with TestClient(starlette) as client:
        response = client.get(mount_path, headers={"accept": "text/html"})

    assert response.status_code == 200

    graphql_endpoint = mount_path + "/"
    assert fr"var graphQLEndpoint = `{graphql_endpoint}`;" in response.text

    subscriptions_endpoint = mount_path + "/subscriptions"
    assert fr"var subscriptionsEndpoint = `{subscriptions_endpoint}`;" in response.text
