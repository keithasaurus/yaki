from pprint import pprint
from typing import Callable, Dict, Union, List, Any, NamedTuple, Optional, Tuple

ASGIValueTypes = Union[bytes, str, int, float, List['ASGIValueTypes'], Dict[str, 'ASGIValueTypes'], bool, None]

ASGIEvent = Dict[str, ASGIValueTypes]


class HTTPScope(NamedTuple):
    """
    proper de-serialized types. original is kept in the orig
    """
    http_version: str
    method: str
    schema: Optional[str]
    path: str
    query_string: bytes
    root_path: Optional[str]
    headers: List[Tuple[bytes, bytes]]
    client: Optional[Tuple[str, int]]
    server: Optional[Tuple[str, int]]
    orig: Dict[str, ASGIValueTypes]


class HTTPRequest(NamedTuple):
    body: Optional[bytes]
    more_body: Optional[bool]
    orig: Dict[str, ASGIValueTypes]


class HTTPResponseStart(NamedTuple):
    status: int
    headers: Optional[List[Tuple[bytes, bytes]]]
    orig: Dict[str, ASGIValueTypes]


class HTTPResponseBody(NamedTuple):
    body: Optional[bytes]
    more_body: Optional[bool]
    orig: Dict[str, ASGIValueTypes]


class HTTPDisconnect(NamedTuple):
    orig: Dict[str, ASGIValueTypes]


def application(scope: Dict[str, Any]) -> Callable:
    async def app_inner(receive,
                        send: Callable[[ASGIEvent], None]):
        event = await receive()

        pprint(event)

        await send({"type": "whatever", "body": "okokok"})
    return app_inner
