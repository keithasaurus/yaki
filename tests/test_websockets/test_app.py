from hypothesis import given
from hypothesis import strategies as st
from tests.test_websockets.strategies import (
    ws_close,
    ws_connect,
    ws_receive,
    ws_scope
)
from unittest import TestCase
from yaki.types import AsgiEvent, Scope
from yaki.websockets.app import ws_app_receiver_only, ws_incoming_to_datatype
from yaki.websockets.types import WSReceive, WSReceiveOutput, WSSend

import asyncio


class WSAppReceiverOnlyTests(TestCase):
    @given(ws_scope(), ws_connect(), st.lists(ws_receive()), ws_close())
    def test_receive_works(self,
                           test_scope,
                           test_connect_event,
                           test_receive_events,
                           test_close_event):
        events = iter(
            [test_connect_event] + test_receive_events + [test_close_event]
        )

        receive_events_iter = iter(test_receive_events)

        async def receive_handler(scope: Scope, event: WSReceive) -> WSReceiveOutput:
            assert scope == test_scope
            assert event == ws_incoming_to_datatype(next(receive_events_iter))
            return WSSend(content="hey buddy")

        async def receive() -> AsgiEvent:
            return next(events)

        # send events here so we can check them
        send_destination = []

        async def send(event: AsgiEvent) -> None:
            send_destination.append(event)

        scoped_app = ws_app_receiver_only(
            receive_handler=receive_handler)(test_scope)

        asyncio.run(scoped_app(receive, send))

        self.assertEqual(send_destination,
                         [{'subprotocol': None, 'type': 'websocket.accept'}] +
                         [{'text': 'hey buddy', 'type': 'websocket.send'}
                          for _ in range(len(test_receive_events))])
