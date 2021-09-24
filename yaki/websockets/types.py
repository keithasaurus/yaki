from dataclasses import dataclass
from types import SimpleNamespace
from typing import (
    Awaitable,
    Callable,
    Mapping,
    Optional,
    Tuple,
    Union,
)

from yaki.routing.types import MatcherOrStr, RouteMatcher
from yaki.types import AsgiEvent, HostPort, AsgiValue


class _WSConnectType:
    pass


ws_connect = _WSConnectType()


@dataclass(frozen=True)
class WSAccept:
    subprotocol: Optional[str]


@dataclass(frozen=True)
class WSSend:
    content: Union[str, bytes]


@dataclass(frozen=True)
class WSClose:
    code: int


@dataclass(frozen=True)
class WSDisconnect:
    code: int


@dataclass(frozen=True)
class WSReceive:
    content: Union[str, bytes]


@dataclass(frozen=True)
class WSScope:
    path: str
    query_string: bytes
    headers: list[tuple[bytes, bytes]]
    scheme: Optional[str]
    root_path: Optional[str]
    client: Optional[HostPort]
    server: Optional[HostPort]
    subprotocols: Optional[list[str]]
    orig: AsgiEvent


WSIncomingEvent = Union[_WSConnectType, WSReceive, WSDisconnect, WSClose]


@dataclass(frozen=True)
class WSInbound:
    custom: SimpleNamespace
    event: WSIncomingEvent
    orig: Mapping[str, AsgiValue]


WSOutbound = Union[WSAccept, WSSend, WSDisconnect, WSClose]

WSReceiver = Callable[[], Awaitable[WSInbound]]

WSSender = Callable[[WSOutbound], Awaitable[None]]

WSView = Callable[[WSScope, WSReceiver, WSSender], Awaitable[None]]

WSProtoRoute = tuple[MatcherOrStr, WSView]

WSRoute = tuple[RouteMatcher, WSView]

WSApp = Tuple[WSRoute, ...]
