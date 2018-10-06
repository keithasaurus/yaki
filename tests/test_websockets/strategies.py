from hypothesis import strategies as st
from tests.utils.strategies import coinflip, headers, host_and_port, query_string
from yaki.types import Scope

import random


@st.composite
def ws_scope(draw) -> Scope:
    scope = {
        'type': 'websocket',
        'path': draw(st.text()),
        'query_string': draw(query_string()),
        'headers': draw(headers()),
    }

    if coinflip():
        scope['scheme'] = random.choice(["ws", "wss"])

    if coinflip():
        scope['root_path'] = draw(st.text())

    if coinflip():
        scope['client'] = draw(host_and_port())

    if coinflip():
        scope['server'] = draw(host_and_port())

    if coinflip():
        scope['subprotocols'] = draw(st.lists(st.text(min_size=1)))

    return scope


@st.composite
def ws_connect(draw):
    return {"type": "websocket.connect"}


@st.composite
def ws_receive(draw):
    event = {
        "type": "websocket.receive",
    }

    if coinflip():
        event["bytes"] = draw(st.text().map(lambda x: bytes(x, encoding="utf8")))
        if coinflip():
            event["text"] = None
    else:
        event["text"] = draw(st.text())
        if coinflip():
            event["bytes"] = None

    return event


@st.composite
def ws_close(draw):
    ret = {
        "type": "websocket.close"
    }

    if coinflip():
        ret["code"] = random.randint(1, 20000)

    return ret
