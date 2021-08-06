import asyncio
import typing

from starlette.websockets import WebSocket
from tartiflette import Engine

from . import protocol


class GraphQLWSProtocol(protocol.GraphQLWSProtocol):
    def __init__(self, websocket: WebSocket, engine: Engine, context: dict):
        super().__init__()
        self.websocket = websocket
        self.engine = engine
        self.context = context
        self.tasks: typing.Set[asyncio.Task] = set()

    # Concurrency implementation.

    def schedule(self, coro: typing.Coroutine) -> None:
        loop = asyncio.get_event_loop()
        self.tasks.add(loop.create_task(coro))

    async def on_disconnect(self, close_code: int) -> None:
        await super().on_disconnect(close_code)
        for task in self.tasks:
            task.cancel()

    # WebSocket implementation.

    async def send_json(self, message: typing.Any) -> None:
        await self.websocket.send_json(message)

    async def close(self, close_code: int) -> None:
        await self.websocket.close(close_code)

    # GraphQL engine implementation.

    def get_subscription(
        self, opid: str, payload: protocol.Payload
    ) -> protocol.Subscription:
        context = {**payload.get("context", {}), **self.context}
        aiterator = self.engine.subscribe(
            query=payload["query"],
            variables=payload.get("variables"),
            operation_name=payload.get("operationName"),
            context=context,
        )

        # `tartiflette` type hints say it returns an `AsyncIterable` (doesn't
        # include `aclose`), but it is actually a full-fledged `AsyncGenerator`
        # which we want to be closing at some point.
        agen = typing.cast(
            typing.AsyncGenerator[typing.Dict[str, typing.Any], None], aiterator
        )

        return protocol.Subscription(agen)
