import typing

from starlette.applications import Starlette
from starlette.types import ASGIApp

from tartiflette_asgi import TartifletteApp

MountHelper = typing.Callable[[ASGIApp, str, TartifletteApp], None]


def starlette(parent: Starlette, path: str, app: TartifletteApp) -> None:
    parent.mount(path, app)
    parent.add_event_handler("startup", app.startup)
