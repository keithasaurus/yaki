from typing import Iterable, List, NamedTuple, Tuple


class HttpResponse(NamedTuple):
    status_code: int
    headers: List[Tuple[bytes, bytes]]
    body: Iterable[bytes]


class HttpDisconnect(NamedTuple):
    pass
