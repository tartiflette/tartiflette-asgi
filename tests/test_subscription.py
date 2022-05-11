import time
import typing

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect
from tartiflette import Engine

from tartiflette_asgi import Subscriptions, TartifletteApp

from ._utils import Dog, PubSub

MISSING = object()


@pytest.mark.parametrize("subscriptions", [MISSING, None])
def test_if_subscriptions_disabled_then_cannot_connect(
    engine: Engine, subscriptions: typing.Any
) -> None:
    kwargs = {}
    if subscriptions is not MISSING:
        kwargs["subscriptions"] = subscriptions

    app = TartifletteApp(engine=engine, **kwargs)

    with TestClient(app) as client:  # type: TestClient  # type: ignore
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/subscriptions"):
                pass


@pytest.fixture(name="pubsub", scope="session")
def fixture_pubsub() -> PubSub:
    from ._utils import pubsub

    return pubsub


@pytest.fixture(name="subscriptions", params=[True, Subscriptions(path="/subs")])
def fixture_subscriptions(request: typing.Any) -> typing.Union[Subscriptions, bool]:
    return request.param


@pytest.fixture(name="path")
def fixture_path(subscriptions: typing.Any) -> str:
    if subscriptions is True:
        return "/subscriptions"
    return subscriptions.path


def _init(ws: WebSocket) -> None:
    ws.send_json({"type": "connection_init"})  # type: ignore
    assert ws.receive_json() == {"type": "connection_ack"}


def _terminate(ws: WebSocket) -> None:
    ws.send_json({"type": "connection_terminate"})  # type: ignore


def test_protocol_connect_disconnect(
    engine: Engine, subscriptions: typing.Any, pubsub: PubSub, path: str
) -> None:
    app = TartifletteApp(
        engine=engine, subscriptions=subscriptions, context={"pubsub": pubsub}
    )

    with TestClient(app) as client:  # type: typing.Any
        with client.websocket_connect(path) as ws:
            _init(ws)
            _terminate(ws)
            with pytest.raises(WebSocketDisconnect) as ctx:
                ws.receive_json()

    exc: WebSocketDisconnect = ctx.value
    assert exc.code == 1011


def test_subscribe(
    engine: Engine, subscriptions: typing.Any, pubsub: PubSub, path: str
) -> None:
    def _emit(dog: Dog = None) -> None:
        time.sleep(0.1)
        pubsub.emit("dog_added", dog)

    gaspar = Dog(id=1, name="Gaspar", nickname="Rapsag")
    woofy = Dog(id=2, name="Merrygold", nickname="Woofy")

    app = TartifletteApp(
        engine=engine, subscriptions=subscriptions, context={"pubsub": pubsub}
    )

    with TestClient(app) as client:  # type: typing.Any
        with client.websocket_connect(path) as ws:
            _init(ws)

            ws.send_json(
                {
                    "type": "start",
                    "id": "myquery",
                    "payload": {
                        "query": """
                        subscription DogAdded {
                            dogAdded {
                                id
                                name
                                nickname
                            }
                        }
                        """
                    },
                }
            )

            _emit(gaspar)
            assert ws.receive_json() == {
                "id": "myquery",
                "type": "data",
                "payload": {
                    "data": {
                        "dogAdded": {"id": 1, "name": "Gaspar", "nickname": "Rapsag"}
                    }
                },
            }

            _emit(woofy)
            assert ws.receive_json() == {
                "id": "myquery",
                "type": "data",
                "payload": {
                    "data": {
                        "dogAdded": {"id": 2, "name": "Merrygold", "nickname": "Woofy"}
                    }
                },
            }

            _emit(None)
            assert ws.receive_json() == {"id": "myquery", "type": "complete"}

            _terminate(ws)
