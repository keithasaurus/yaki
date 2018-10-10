from hypothesis import strategies as st
from tests.utils.strategies import (
    headers,
    host_and_port,
    query_string,
    scope_extensions
)
from yaki.utils.types import Scope


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


@st.composite
def asgi_ws_connect(draw):
    return {"type": "websocket.connect"}


@st.composite
def asgi_ws_receive(draw):
    bytes_, text = draw(st.one_of(
        st.tuples(st.none(), st.text(max_size=100)),
        st.tuples(st.text().map(lambda x: bytes(x, encoding="utf8")), st.none())
    ))

    return {
        "type": "websocket.receive",
        # todo: bytes and text should alternate in which is None and which isn't
        "bytes": bytes_,
        "text": text
    }


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
        "type": "websocket.close",
        # todo: optional kwarg
        'code': draw(st.integers())
    }
