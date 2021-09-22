from dataclasses import dataclass
from datetime import datetime, timedelta
from yaki.websockets.types import (
    WSAccept,
    WSClose,
    WSConnect,
    WSDisconnect,
    WSInbound,
    WSOutbound,
    WSReceive,
    WSReceiver,
    WSScope,
    WSSend,
    WSSender,
)

import asyncio
import random


@dataclass
class ChatState:
    disconnected: bool
    last_client_message: datetime
    no_response_count: int


async def check_bored(state: ChatState, send: WSSender):
    acceptable_wait = timedelta(seconds=10)
    while True:
        await asyncio.sleep(10)
        time_since_last_message = datetime.now() - state.last_client_message
        if time_since_last_message > acceptable_wait:
            if time_since_last_message > acceptable_wait * 5:
                await send(WSSend("This is boring. I'm leaving"))
                state.disconnected = True
                await send(WSClose(1000))
                break
            else:
                await send(WSSend("Hey, say something!"))


async def ws_chat_bot(scope: WSScope, receive: WSReceiver, send: WSSender) -> None:
    state = ChatState(
        disconnected=False, last_client_message=datetime.now(), no_response_count=0
    )

    async def protected_send(event: WSOutbound):
        if not state.disconnected:
            await send(event)

    connect = await receive()

    assert isinstance(connect.event, WSConnect)

    await protected_send(WSAccept(subprotocol=None))

    await protected_send(WSSend("So, tell me something!"))

    # our bot will periodically say something if it gets bored
    asyncio.get_event_loop().create_task(check_bored(state, protected_send))

    while not state.disconnected:

        message: WSInbound = await receive()

        if isinstance(message.event, (WSClose, WSDisconnect)):
            state.disconnected = True
            break

        elif isinstance(message.event, WSReceive):
            state.last_client_message = datetime.now()

            if len(message.event.content) == 0:
                resp: str = "That's, like, zero information."
            else:
                resp = random.choice(
                    [
                        "That's nice. Tell me something else.",
                        "Sorry, I don't care about that. Be more entertaining, please.",
                        "...",
                        "...SMH",
                        "I like the way you think.",
                    ]
                )

            await protected_send(WSSend(resp))

        elif isinstance(message.event, WSConnect):
            # already received a connect request
            state.disconnected = True
            await protected_send(WSClose(1000))
            break
        else:
            raise TypeError("Bad event type!")

    await protected_send(WSClose(1000))
