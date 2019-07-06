import asyncio
import typing

from starlette.websockets import WebSocket
from tartiflette import Engine

from . import protocol


class _AsyncIOMixin:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tasks: typing.Set[asyncio.Task] = set()

    def schedule(self, coro: typing.Coroutine):
        loop = asyncio.get_event_loop()
        self.tasks.add(loop.create_task(coro))

    async def on_disconnect(self, close_code: int):
        await super().on_disconnect(close_code)
        for task in self.tasks:
            task.cancel()


class _StarletteWebSocketMixin:
    def __init__(self, *, websocket: WebSocket, **kwargs):
        super().__init__(**kwargs)
        self.websocket = websocket

    async def send_json(self, message: typing.Any):
        await self.websocket.send_json(message)

    async def close(self, close_code: int):
        await self.websocket.close(close_code)


class _TartifletteEngineMixin:
    def __init__(self, *, engine: Engine, context: dict, **kwargs):
        super().__init__(**kwargs)
        self.engine = engine
        self.context = context

    def get_stream(self, opid: str, payload: dict) -> typing.AsyncGenerator:
        context = {**payload.get("context", {}), **self.context}
        return self.engine.subscribe(
            query=payload.get("query"),
            variables=payload.get("variables"),
            operation_name=payload.get("operationName"),
            context=context,
        )


class GraphQLWSProtocol(
    _AsyncIOMixin,
    _StarletteWebSocketMixin,
    _TartifletteEngineMixin,
    protocol.GraphQLWSProtocol,
):
    def __init__(self, websocket: WebSocket, engine: Engine, context: dict):
        super().__init__(websocket=websocket, engine=engine, context=context)
