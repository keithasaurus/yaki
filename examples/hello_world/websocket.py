from yaki.apps import yaki
from yaki.websockets.config import ws_app
from yaki.websockets.types import (
    TypedReceiver,
    TypedSender,
    WSAccept,
    WSClose,
    WSConnect,
    WSScope,
    WSSend
)

import asyncio


async def ws_hello(scope: WSScope,
                   receive: TypedReceiver,
                   send: TypedSender) -> None:
    connect = await receive()
    assert isinstance(connect, WSConnect)
    await send(WSAccept(subprotocol=None))
    await send(WSSend("Hello"))
    await asyncio.sleep(1)
    await send(WSSend("world"))
    await asyncio.sleep(1)
    await send(WSClose(1000))


app = yaki(
    ws_app(
        routes=[
            ("/", ws_hello)
        ]
    )
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=5000)
