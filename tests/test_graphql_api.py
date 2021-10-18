import pytest
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp

from ._utils import get_client


@pytest.mark.asyncio
async def test_get_querystring(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.get("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ("/", "/?foo=bar", "/?q={ hello }"))
async def test_get_no_query(engine: Engine, path: str) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.get(path)
    assert response.status_code == 400
    assert response.text == "No GraphQL query found in the request"


@pytest.mark.asyncio
async def test_post_querystring(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post("/?query={ hello }")
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


@pytest.mark.asyncio
async def test_post_json(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post("/", json={"query": "{ hello }"})
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


@pytest.mark.asyncio
async def test_post_invalid_json(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post(
            "/", content="{test", headers={"content-type": "application/json"}
        )
    assert response.status_code == 400
    assert response.json() == {"error": "Invalid JSON."}


@pytest.mark.asyncio
async def test_post_graphql(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post(
            "/", content="{ hello }", headers={"content-type": "application/graphql"}
        )
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "Hello stranger"}}


@pytest.mark.asyncio
async def test_post_invalid_media_type(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post(
            "/", content="{ hello }", headers={"content-type": "dummy"}
        )
    assert response.status_code == 415
    assert response.text == "Unsupported Media Type"


@pytest.mark.asyncio
async def test_put(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.put("/", json={"query": "{ hello }"})
    assert response.status_code == 405
    assert response.text == "Method Not Allowed"


@pytest.mark.asyncio
async def test_error_handling(engine: Engine) -> None:
    app = TartifletteApp(engine=engine)
    async with get_client(app) as client:
        response = await client.post("/", json={"query": "{ dummy }"})
    assert response.status_code == 400
    json = response.json()
    assert json["data"] is None
    assert len(json["errors"]) == 1
    error = json["errors"][0]
    assert error["locations"] == [{"column": 3, "line": 1}]
    assert "dummy" in error["message"]
    assert error["path"] == ["dummy"]
