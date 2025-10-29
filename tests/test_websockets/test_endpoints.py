import asyncio
from unittest import TestCase

from yaki.types import AsgiEvent, Scope
from yaki.websockets.endpoints import (
    asgi_ws_scope_to_datatype,
    ws_endpoint,
    ws_incoming_to_datatype,
    ws_outgoing_to_event_dict,
)
from yaki.websockets.types import WSAccept, WSSend, WSClose, WSDisconnect


def asgi_ws_connect():
    return {"type": "websocket.connect"}


class WSEndpointTests(TestCase):
    def test_receive_works(self):
        # Build a minimal, deterministic scope and events
        test_scope: Scope = {
            "type": "websocket",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "root_path": "",
            "client": ["127.0.0.1", 5000],
            "server": ["127.0.0.1", 5000],
            "subprotocols": ["chat"],
            "extensions": {},
            "scheme": "ws",
        }

        test_receive_events = [
            {"type": "websocket.receive", "bytes": b"hi", "text": None},
            {"type": "websocket.receive", "bytes": None, "text": "hello"},
        ]

        test_accept_event = WSAccept(subprotocol=None)
        test_send_events = [WSSend("Hello"), WSSend(b"bytes")] 
        test_close_event = WSClose(1000)
        test_disconnect = WSDisconnect(1001)

        incoming_events = [asgi_ws_connect()] + test_receive_events

        iter_incoming = iter(incoming_events)

        outgoing_events = [
            test_accept_event,
            test_close_event,
            test_disconnect,
        ] + test_send_events

        async def ws_func(scope: Scope, receive, send) -> None:
            assert scope == asgi_ws_scope_to_datatype(test_scope)

            # wait for all incoming events
            for asgi_event in incoming_events:
                received_event = await receive()
                assert received_event == ws_incoming_to_datatype(asgi_event)

            # send all outgoing events
            for event in outgoing_events:
                await send(event)

        async def receive() -> AsgiEvent:
            return next(iter_incoming)

        # send events here so we can check them
        send_destination = []

        async def send(event: AsgiEvent) -> None:
            send_destination.append(event)

        scoped_app = ws_endpoint(ws_func)(test_scope)

        asyncio.run(scoped_app(receive, send))

        self.assertEqual(
            send_destination,
            [ws_outgoing_to_event_dict(evt) for evt in outgoing_events],
        )
