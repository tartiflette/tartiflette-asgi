import typing

from starlette.applications import Starlette
from starlette.types import ASGIApp

from tartiflette_starlette import TartifletteApp

MountHelper = typing.Callable[[ASGIApp, str, TartifletteApp], None]


def starlette(parent: Starlette, path: str, app: TartifletteApp, **kwargs):
    parent.mount(path, app, **kwargs)
    parent.add_event_handler("startup", app.startup)
