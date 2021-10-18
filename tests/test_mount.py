import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse
from starlette.routing import Mount, Route
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp

from ._utils import get_client, omit_none

app = Starlette()


@pytest.mark.asyncio
@pytest.mark.parametrize("mount_path", ("/", "/graphql"))
@pytest.mark.parametrize("path", [None, "/", "/graphql", "/graphql/"])
async def test_starlette_mount(engine: Engine, mount_path: str, path: str) -> None:
    kwargs = omit_none({"engine": engine, "path": path})

    graphql = TartifletteApp(**kwargs)
    routes = [Mount(mount_path, graphql)]
    app = Starlette(routes=routes, on_startup=[graphql.startup])

    query = "{ hello }"
    full_path = mount_path.rstrip("/") + ("/" if path is None else path)
    assert "//" not in full_path

    url = f"{full_path}?query={query}"
    async with get_client(app) as client:
        response = await client.get(url)
        graphiql_response = await client.get(url, headers={"accept": "text/html"})

    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}

    assert graphiql_response.status_code == 200
    assert full_path in graphiql_response.text


@pytest.mark.asyncio
async def test_must_register_startup_handler(engine: Engine) -> None:
    graphql = TartifletteApp(engine=engine)
    app = Starlette(routes=[Mount("/graphql", graphql)], on_startup=[])

    async with get_client(app) as client:
        with pytest.raises(RuntimeError) as ctx:
            await client.get("/graphql/")

    error = str(ctx.value).lower()
    assert "hint" in error
    assert "starlette example" in error
    assert ".add_event_handler" in error
    assert "'startup'" in error
    assert ".startup" in error


@pytest.mark.asyncio
@pytest.mark.parametrize("mount_path, url", [("", "/"), ("/graphql", "/graphql/")])
async def test_graphiql_endpoint_paths_when_mounted(
    engine: Engine, mount_path: str, url: str
) -> None:
    graphql = TartifletteApp(engine=engine, graphiql=True, subscriptions=True)
    app = Starlette(routes=[Mount(mount_path, graphql)], on_startup=[graphql.startup])

    async with get_client(app) as client:
        response = await client.get(url, headers={"accept": "text/html"})

    assert response.status_code == 200

    graphql_endpoint = mount_path + "/"
    assert f"var graphQLEndpoint = `{graphql_endpoint}`;" in response.text

    subscriptions_endpoint = mount_path + "/subscriptions"
    assert f"var subscriptionsEndpoint = `{subscriptions_endpoint}`;" in response.text


@pytest.mark.asyncio
async def test_tartiflette_app_as_sub_starlette_app(engine: Engine) -> None:
    async def home(_request: Request) -> PlainTextResponse:
        return PlainTextResponse("Hello, world!")

    graphql = TartifletteApp(engine=engine)
    routes = [
        Route("/", endpoint=home),
        Mount("/graphql", app=graphql, name="tartiflette-asgi"),
    ]
    app = Starlette(routes=routes, on_startup=[graphql.startup])

    async with get_client(app) as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, world!"
        response = await client.get("/graphql/?query={ hello }")
        assert response.status_code == 200
        assert response.json() == {"data": {"hello": "Hello stranger"}}
