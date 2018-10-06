from hypothesis import strategies as st
from tests.utils.strategies import coinflip, headers, host_and_port, query_string

import random


@st.composite
def asgi_scope(draw):
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
