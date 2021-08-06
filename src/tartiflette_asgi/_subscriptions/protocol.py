"""Sans-IO base implementation of the GraphQL over WebSocket protocol.

See: https://github.com/apollographql/subscriptions-transport-ws
"""
import json
import sys
import typing

from .constants import GQL

if sys.version_info >= (3, 8):  # pragma: no cover
    from typing import TypedDict
else:  # pragma: no cover
    from typing_extensions import TypedDict


class Payload(TypedDict):
    context: dict
    query: typing.Union[str, bytes]
    variables: typing.Optional[typing.Dict[str, typing.Any]]
    operationName: typing.Optional[str]


class Subscription:
    def __init__(
        self,
        agen: typing.AsyncGenerator[typing.Dict[str, typing.Any], None],
    ) -> None:
        self._agen = agen

    async def __aiter__(self) -> typing.AsyncIterator[typing.Dict[str, typing.Any]]:
        async for item in self._agen:
            yield item

    async def aclose(self) -> None:
        await self._agen.aclose()


class GraphQLWSProtocol:
    name = "graphql-ws"

    def __init__(self) -> None:
        self._subscriptions: typing.Dict[str, Subscription] = {}

    # Methods whose implementation is left to the implementer.

    def schedule(self, coro: typing.Coroutine) -> None:
        raise NotImplementedError

    async def send_json(self, message: dict) -> None:
        raise NotImplementedError

    async def close(self, close_code: int) -> None:
        raise NotImplementedError

    def get_subscription(self, opid: str, payload: Payload) -> Subscription:
        raise NotImplementedError

    # Helpers.

    async def _send_message(
        self,
        opid: typing.Optional[str] = None,
        optype: typing.Optional[str] = None,
        payload: typing.Optional[typing.Any] = None,
    ) -> None:
        items = (("id", opid), ("type", optype), ("payload", payload))
        message = {k: v for k, v in items if v is not None}
        await self.send_json(message)

    async def _send_error(
        self,
        message: str,
        opid: typing.Optional[str] = None,
        error_type: typing.Optional[str] = None,
    ) -> None:
        if error_type not in {GQL.ERROR, GQL.CONNECTION_ERROR}:
            error_type = GQL.ERROR
        await self._send_message(opid, error_type, {"message": message})

    async def _subscribe(self, opid: str, payload: Payload) -> None:
        subscription = self.get_subscription(opid, payload)
        self._subscriptions[opid] = subscription

        try:
            async for item in subscription:
                if opid not in self._subscriptions:
                    break
                await self._send_message(opid, optype="data", payload=item)
        except Exception as exc:
            await self._send_error("Internal error", opid=opid)
            raise exc

        await self._send_message(opid, "complete")
        await self._unsubscribe(opid)

    async def _unsubscribe(self, opid: str) -> None:
        subscription = self._subscriptions.pop(opid, None)
        if subscription is None:
            return
        await subscription.aclose()

    # Client message handlers.

    async def _on_connection_init(self, opid: str, payload: Payload) -> None:
        try:
            await self._send_message(optype=GQL.CONNECTION_ACK)
        except Exception as exc:
            await self._send_error(str(exc), opid=opid, error_type=GQL.CONNECTION_ERROR)
            await self.close(1011)

    async def _on_start(self, opid: str, payload: Payload) -> None:
        if opid in self._subscriptions:
            await self._unsubscribe(opid)
        await self._subscribe(opid, payload)

    async def _on_stop(self, opid: str, payload: Payload) -> None:
        await self._unsubscribe(opid)

    async def _on_connection_terminate(self, opid: str, payload: Payload) -> None:
        await self.close(1011)

    # Main task.

    async def _main(self, message: typing.Any) -> None:
        if not isinstance(message, dict):
            try:
                message = json.loads(message)
                if not isinstance(message, dict):
                    raise TypeError("payload must be a JSON object")
            except TypeError as exc:
                await self._send_error(str(exc))

        optype: str = message.get("type")
        opid: str = message.get("id")
        payload: Payload = message.get("payload", {})

        handler: typing.Callable[[str, Payload], typing.Awaitable[None]]

        if optype == "connection_init":
            handler = self._on_connection_init
        elif optype == "start":
            handler = self._on_start
        elif optype == "stop":
            handler = self._on_stop
        elif optype == "connection_terminate":
            handler = self._on_connection_terminate
        else:
            await self._send_error(f"Unsupported message type: {optype}", opid=opid)
            return

        await handler(opid=opid, payload=payload)

    # Public API.

    async def on_receive(self, message: typing.Any) -> None:
        # Subscription execution is a long-lived `async for` operation,
        # so we must schedule it in a separate task on the event loop.
        self.schedule(self._main(message))

    async def on_disconnect(self, close_code: int) -> None:
        # NOTE: load keys in list to prevent "size changed during iteration".
        for opid in list(self._subscriptions):
            await self._unsubscribe(opid)
