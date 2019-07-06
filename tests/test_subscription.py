import time

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from ._utils import Dog, PubSub


def _init(ws: WebSocket):
    ws.send_json({"type": "connection_init"})
    assert ws.receive_json() == {"type": "connection_ack"}


def _terminate(ws: WebSocket):
    ws.send_json({"type": "connection_terminate"})


def test_protocol_connect_disconnect(client: TestClient):
    with client.websocket_connect("/subscriptions") as ws:
        _init(ws)
        _terminate(ws)
        with pytest.raises(WebSocketDisconnect) as ctx:
            ws.receive_json()

    exc: WebSocketDisconnect = ctx.value
    assert exc.code == 1011


def test_subscribe(client: TestClient, pubsub: PubSub):
    def _emit(dog: Dog):
        time.sleep(0.1)
        pubsub.emit("dog_added", dog)

    gaspar = Dog(id=1, name="Gaspar", nickname="Rapsag")
    woofy = Dog(id=2, name="Merrygold", nickname="Woofy")

    with client.websocket_connect("/subscriptions") as ws:
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
                    "dogAdded": {
                        "id": 1,
                        "name": "Gaspar",
                        "nickname": "Rapsag",
                    }
                }
            },
        }

        _emit(woofy)
        assert ws.receive_json() == {
            "id": "myquery",
            "type": "data",
            "payload": {
                "data": {
                    "dogAdded": {
                        "id": 2,
                        "name": "Merrygold",
                        "nickname": "Woofy",
                    }
                }
            },
        }

        _emit(None)
        assert ws.receive_json() == {"id": "myquery", "type": "complete"}

        _terminate(ws)
