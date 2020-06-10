import inspect
import json
import re
import typing

import pytest
from tartiflette import Engine

from tartiflette_asgi import GraphiQL, TartifletteApp

from ._utils import get_client


@pytest.fixture(
    name="graphiql", params=[False, True, GraphiQL(), GraphiQL(path="/graphql")]
)
def fixture_graphiql(request: typing.Any) -> typing.Union[GraphiQL, bool]:
    return request.param


@pytest.fixture(name="path")
def fixture_path(graphiql: typing.Any) -> str:
    if not graphiql or graphiql is True or graphiql.path is None:
        return ""
    return graphiql.path


@pytest.mark.asyncio
async def test_graphiql(engine: Engine, graphiql: typing.Any, path: str) -> None:
    app = TartifletteApp(engine=engine, graphiql=graphiql)
    async with get_client(app) as client:
        response = await client.get(path, headers={"accept": "text/html"})

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


@pytest.mark.asyncio
async def test_graphiql_not_found(engine: Engine, path: str) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.get(path + "foo")
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


@pytest.mark.asyncio
async def test_defaults(
    engine: Engine, variables: dict, query: str, headers: dict
) -> None:
    graphiql = GraphiQL(
        default_variables=variables, default_query=query, default_headers=headers
    )
    app = TartifletteApp(engine=engine, graphiql=graphiql)

    async with get_client(app) as client:
        response = await client.get("/", headers={"accept": "text/html"})

    assert response.status_code == 200
    assert json.dumps(variables) in response.text
    assert inspect.cleandoc(query) in response.text
    assert json.dumps(headers) in response.text
