from dataclasses import dataclass
from types import SimpleNamespace
from typing import (
    Awaitable,
    Callable,
    List,
    Mapping,
    NamedTuple,
    Optional,
    Tuple,
    Union
)
from yaki.routing.matchers import RouteMatcher
from yaki.routing.types import MatcherOrStr
from yaki.types import AsgiEvent, HostPort


class WSConnect(NamedTuple):
    pass


@dataclass
class WSAccept:
    subprotocol: Optional[str]


@dataclass
class WSSend:
    content: Union[str, bytes]


@dataclass
class WSClose:
    code: int


@dataclass
class WSDisconnect:
    code: int


class WSReceive(NamedTuple):
    content: Union[str, bytes]


class WSScope(NamedTuple):
    path: str
    query_string: bytes
    headers: List[Tuple[bytes, bytes]]
    scheme: Optional[str]
    root_path: Optional[str]
    client: Optional[HostPort]
    server: Optional[HostPort]
    subprotocols: Optional[List[str]]
    orig: AsgiEvent


WSIncomingEvent = Union[WSConnect, WSReceive, WSDisconnect, WSClose]


class WSInbound(NamedTuple):
    custom: SimpleNamespace
    event: WSIncomingEvent
    orig: Mapping


WSOutbound = Union[WSAccept, WSSend, WSDisconnect, WSClose]


WSReceiver = Callable[[], Awaitable[WSInbound]]

WSSender = Callable[[WSOutbound], Awaitable[None]]


WSView = Callable[[WSScope, WSReceiver, WSSender], Awaitable[None]]


WSProtoRoute = Tuple[MatcherOrStr, WSView]

WSRoute = Tuple[RouteMatcher, WSView]


class WSApp(NamedTuple):
    routes: Tuple[WSRoute, ...]
