import typing

import httpx
from asgi_lifespan import LifespanManager
from pyee import AsyncIOEventEmitter

from ._compat import asynccontextmanager


@asynccontextmanager
async def get_client(app: typing.Callable) -> typing.AsyncIterator:
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app, base_url="http://testserver/") as client:
            yield client


def omit_none(dct: dict) -> dict:
    return {key: value for key, value in dct.items() if value is not None}


PubSub = AsyncIOEventEmitter
pubsub = PubSub()  # pylint: disable=invalid-name


class Dog(typing.NamedTuple):
    id: int
    name: str
    nickname: typing.Optional[str] = None
