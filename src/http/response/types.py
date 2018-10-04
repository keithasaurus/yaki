from typing import NamedTuple, Iterable, List, Tuple


class HttpResponse(NamedTuple):
    status_code: int
    headers: List[Tuple[bytes, bytes]]
    body: Iterable[bytes]


class HttpDisconnect(NamedTuple):
    pass
