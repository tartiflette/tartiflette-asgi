import typing

from pyee import AsyncIOEventEmitter


def omit_none(dct: dict) -> dict:
    return {key: value for key, value in dct.items() if value is not None}


PubSub = AsyncIOEventEmitter
pubsub = PubSub()  # pylint: disable=invalid-name


class Dog(typing.NamedTuple):
    id: int
    name: str
    nickname: typing.Optional[str] = None
