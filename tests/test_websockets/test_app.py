from hypothesis import given
from hypothesis import strategies as st
from tests.test_websockets.strategies import (
    ws_close,
    ws_connect,
    ws_receive,
    ws_scope
)
from typing import List
from unittest import TestCase
from yaki.types import AsgiEvent, AsgiInstance, Scope
from yaki.websockets.app import (
    disconnect_noop,
    ws_app,
    ws_app_receiver_only,
    ws_close_to_dict,
    ws_disconnect_to_dict,
    ws_incoming_to_datatype
)
from yaki.websockets.types import (
    WSClose,
    WSDisconnect,
    WSReceive,
    WSReceiveOutput,
    WSSend
)

import asyncio


def _test_ws_event_sequence(scope: Scope,
                            incoming_events: List[AsgiEvent],
                            app: AsgiInstance) -> List[AsgiEvent]:
    incoming_events_iter = iter(incoming_events)

    async def receive() -> AsgiEvent:
        return next(incoming_events_iter)

    # send events here so we can check them
    send_destination = []

    async def send(event: AsgiEvent) -> None:
        send_destination.append(event)

    app_with_scope = app(scope)

    asyncio.run(app_with_scope(receive, send))

    return send_destination


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

    @given(ws_scope(),
           ws_connect(),
           st.from_type(WSDisconnect),
           ws_receive())
    def test_early_disconnect_stops_everything(self,
                                               test_scope,
                                               test_connect,
                                               test_disconnect,
                                               test_late_receive_message):
        async def receive_handler(scope: Scope, event: WSReceive) -> WSReceiveOutput:
            return WSSend(content="SHOULD NOT BE RECEIVED!!")

        async def connect_handler(scope: Scope):
            return test_disconnect

        sent_events = _test_ws_event_sequence(
            test_scope,
            [test_connect, test_disconnect, test_late_receive_message],
            ws_app(receive_handler=receive_handler,
                   connect_handler=connect_handler,
                   client_disconnect_handler=disconnect_noop))

        self.assertEqual(sent_events, [ws_disconnect_to_dict(test_disconnect)])

    @given(ws_scope(),
           ws_connect(),
           st.from_type(WSClose),
           ws_receive())
    def test_early_close_stops_everything(self,
                                          test_scope,
                                          test_connect,
                                          test_close,
                                          test_late_receive_message):
        async def receive_handler(scope: Scope, event: WSReceive) -> WSReceiveOutput:
            return WSSend(content="SHOULD NOT BE RECEIVED!!")

        async def connect_handler(scope: Scope):
            return test_close

        sent_events = _test_ws_event_sequence(
            test_scope,
            [test_connect, test_close, test_late_receive_message],
            ws_app(receive_handler=receive_handler,
                   connect_handler=connect_handler,
                   client_disconnect_handler=disconnect_noop))

        self.assertEqual(sent_events, [ws_close_to_dict(test_close)])
