from typing import NamedTuple, Optional, Union


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


WSIncomingEvent = Union[WSConnect, WSReceive, WSDisconnect, WSClose]

WSOutgoingEvent = Union[WSAccept, WSSend, WSDisconnect, WSClose]
