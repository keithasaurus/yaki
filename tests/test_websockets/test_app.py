from unittest import TestCase
from yaki.types import Scope
from yaki.websockets.app import ws_app
from yaki.websockets.types import WSAccept, WSReceive, WSReceiveOutput, WSSend


class WSAppTests(TestCase):
    def test_app_with_custom_methods(self):
        async def connect(scope: Scope) -> WSAccept:
            return WSAccept(subprotocol=None)

        async def receive(scope: Scope, event: WSReceive) -> WSReceiveOutput:
            return WSSend(content="hey buddy")

        async def disconnect(scope: Scope) -> None:
            return None

        scoped_app = ws_app(
            connect_handler=connect,
            receive_handler=receive,
            client_disconnect_handler=disconnect
        )()
