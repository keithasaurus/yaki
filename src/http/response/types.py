from typing import NamedTuple, Iterable, List, Tuple

from src.types import ASGIEvent

# todo: make named tuple or convert HttpResponse to NamedTuple
HttpRequest = ASGIEvent


class HttpResponse(NamedTuple):
    status_code: int
    headers: List[Tuple[bytes, bytes]]
    body: Iterable[bytes]
