from hypothesis import given, settings
from hypothesis import strategies as st
from tests.test_websockets.strategies import ws_connect, ws_receive, ws_scope
from unittest import TestCase
from yaki.types import AsgiEvent, Scope
from yaki.websockets.app import (
    ws_app,
    ws_incoming_to_datatype,
    ws_outgoing_to_event_dict
)
from yaki.websockets.types import WSAccept, WSClose, WSDisconnect, WSSend

import asyncio


class WSAppTests(TestCase):
    @given(ws_scope(),
           ws_connect(),
           st.lists(ws_receive()),
           st.from_type(WSAccept),
           st.lists(st.from_type(WSSend)),
           st.from_type(WSClose),
           st.from_type(WSDisconnect))
    @settings(max_examples=20)
    def test_receive_works(self,
                           test_scope,
                           test_connect_event,
                           test_receive_events,
                           test_accept_event,
                           test_send_events,
                           test_close_event,
                           test_disconnect):
        incoming_events = [test_connect_event] + test_receive_events

        iter_incoming = iter(incoming_events)

        outgoing_events = [test_accept_event,
                           test_close_event,
                           test_disconnect] + test_send_events

        async def ws_func(scope: Scope, receive, send) -> None:
            assert scope == test_scope

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

        scoped_app = ws_app(ws_func)(test_scope)

        asyncio.run(scoped_app(receive, send))

        self.assertEqual(
            send_destination,
            [ws_outgoing_to_event_dict(evt) for evt in outgoing_events]
        )
