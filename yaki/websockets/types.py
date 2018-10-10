from typing import Awaitable, Callable, List, NamedTuple, Optional, Tuple, Union
from yaki.routing.matchers import RouteMatcher
from yaki.utils.types import AsgiEvent, HostPort


class WSConnect(NamedTuple):
    pass


class WSAccept(NamedTuple):
    subprotocol: Optional[str]


class WSSend(NamedTuple):
    content: Union[str, bytes]


class WSClose(NamedTuple):
    code: int


class WSDisconnect(NamedTuple):
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

WSOutgoingEvent = Union[WSAccept, WSSend, WSDisconnect, WSClose]


TypedReceiver = Callable[[], Awaitable[WSIncomingEvent]]

TypedSender = Callable[[WSOutgoingEvent], Awaitable[None]]


WSViewFunc = Callable[[WSScope, TypedReceiver, TypedSender], Awaitable[None]]


class WSConfig(NamedTuple):
    routes: List[Tuple[RouteMatcher, WSViewFunc]]
