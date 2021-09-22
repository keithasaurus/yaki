from yaki.apps import yaki
from yaki.websockets.config import ws_app
from yaki.websockets.types import (
    WSAccept,
    WSClose,
    WSReceiver,
    WSScope,
    WSSend,
    WSSender,
)


async def ws_hello(scope: WSScope, receive: WSReceiver, send: WSSender) -> None:
    await receive()  # this is the connect message

    await send(WSAccept(subprotocol=None))

    await send(WSSend("Hello"))

    await send(WSSend("world"))

    await send(WSClose(1000))


app = yaki(ws_app(routes=[("/", ws_hello)]))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
