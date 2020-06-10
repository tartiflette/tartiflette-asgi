import pytest
from tartiflette import Engine

from tartiflette_asgi import TartifletteApp

from ._utils import get_client


@pytest.mark.asyncio
async def test_path(engine: Engine) -> None:
    app = TartifletteApp(engine=engine, path="/graphql")

    async with get_client(app) as client:
        response = await client.get("/")
        assert response.status_code == 404
        response = await client.get("/graphql?query={ hello }")
        assert response.status_code == 200
        assert response.json() == {"data": {"hello": "Hello stranger"}}
