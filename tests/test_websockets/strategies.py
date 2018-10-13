from hypothesis import strategies as st
from tests.utils.strategies import (
    headers,
    host_and_port,
    query_string,
    scope_extensions
)
from yaki.types import Scope


@st.composite
def asgi_ws_scope(draw) -> Scope:
    return {
        'type': 'websocket',
        'path': draw(st.text(max_size=100)),
        'headers': draw(headers()),
        # todo: next keys # todo: if it's text it should beare optional
        'query_string': draw(query_string()),
        'root_path': draw(st.text(max_size=100)),
        'client': draw(host_and_port()),
        'server': draw(host_and_port()),
        'subprotocols': draw(st.lists(st.text(min_size=1))),
        'extensions': draw(scope_extensions()),
        'scheme': draw(st.sampled_from(['ws', 'wss']))
    }


def asgi_ws_connect():
    return {"type": "websocket.connect"}


@st.composite
def _asgi_receive_bytes(draw):
    return {
        "type": "websocket.receive",
        "bytes": draw(st.text().map(lambda x: x.encode("utf8"))),
        "text": None
    }


@st.composite
def _asgi_receive_text(draw):
    return {
        "type": "websocket.receive",
        "bytes": None,
        "text": draw(st.text(max_size=100))
    }


@st.composite
def asgi_ws_receive(draw):
    return draw(st.one_of(_asgi_receive_bytes(), _asgi_receive_text()))


@st.composite
def asgi_ws_close(draw):
    return {
        "type": "websocket.close",
        # todo: optional kwarg
        'code': draw(st.integers())
    }


@st.composite
def asgi_ws_disconnect(draw):
    return {
        "type": "websocket.disconnect",
        # todo: optional kwarg
        'code': draw(st.integers())
    }
