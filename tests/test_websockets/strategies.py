from hypothesis import strategies as st
from tests.utils.strategies import (
    headers,
    host_and_port,
    query_string,
    scope_extensions
)
from yaki.utils.types import Scope


@st.composite
def ws_scope(draw) -> Scope:
    return {
        'type': 'websocket',
        'path': draw(st.text(max_size=100)),
        'headers': draw(headers()),
        # todo: next keys are optional
        'query_string': draw(query_string()),
        'root_path': draw(st.text(max_size=100)),
        'client': draw(host_and_port()),
        'server': draw(host_and_port()),
        'subprotocols': draw(st.lists(st.text(min_size=1))),
        'extensions': draw(scope_extensions()),
        'scheme': draw(st.sampled_from(['ws', 'wss']))
    }


@st.composite
def ws_connect(draw):
    return {"type": "websocket.connect"}


@st.composite
def ws_receive(draw):
    return {
        "type": "websocket.receive",
        # todo: bytes and text should alternate in which is None and which isn't
        "bytes": draw(st.text().map(lambda x: bytes(x, encoding="utf8"))),
        "text": None
    }


@st.composite
def ws_close(draw):
    return {
        "type": "websocket.close",
        # todo: optional kwarg
        'code': draw(st.integers())
    }


@st.composite
def ws_disconnect(draw):
    return {
        "type": "websocket.close",
        # todo: optional kwarg
        'code': draw(st.integers())
    }
