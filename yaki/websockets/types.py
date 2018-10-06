from typing import NamedTuple, Optional, Union

import enum


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

WSReceiveOutput = Union[WSSend, WSDisconnect, WSClose, None]


class WSState(enum.Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2


INCOMING_CLIENT_STATES = {
    WSState.CONNECTING: {"connect"},
}
