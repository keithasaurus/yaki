from typing import (
    Any,
    Awaitable,
    Callable,
    Mapping,
    NamedTuple,
    Union,
)

# Note the Anys here should be recursive AsgiValue, but are not because
# of mypy's current limitations
AsgiValue = Union[bytes, str, int, float, list[Any], dict[str, Any], bool, None]

AsgiEvent = Mapping[str, AsgiValue]

Scope = Mapping[str, AsgiValue]

Receiver = Callable[[], Awaitable[AsgiEvent]]

Sender = Callable[[AsgiEvent], Awaitable[None]]

AsgiInstance = Callable[[Receiver, Sender], Awaitable[None]]

ScopeAsgiInstance = Callable[[Scope], AsgiInstance]

AsgiApp = Callable[[Scope], AsgiInstance]


class HostPort(NamedTuple):
    host: str
    port: int


Headers = list[tuple[bytes, bytes]]


def list_headers_to_tuples(val: AsgiValue) -> Headers:
    """
    Currently this is the same for websockets and http, but that could change
    """
    headers = []

    assert isinstance(val, list)

    for header_pair in val:
        assert isinstance(header_pair, (list, tuple))
        assert len(header_pair) == 2
        k, v = header_pair
        assert isinstance(k, bytes)
        assert isinstance(v, bytes)
        headers.append((k, v))

    return headers


def list_hostport_to_datatype(val: AsgiValue) -> HostPort:
    """
    Currently this is the same for websockets and http, but that could change
    """
    assert isinstance(val, (list, tuple))
    assert len(val) == 2
    host, port = val
    assert isinstance(host, str)
    assert isinstance(port, int)
    return HostPort(host=host, port=port)
