from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union
)
from yaki.routes import RouteMatcher
from yaki.utils.types import HostPort, Scope


class HttpRequest(NamedTuple):
    body: bytes
    client: Optional[HostPort]
    extensions: Optional[Dict[str, Dict[Any, Any]]]
    headers: List[Tuple[bytes, bytes]]
    http_version: str
    method: str
    path: str
    query_string: bytes
    root_path: str
    scheme: str
    scope_orig: Scope
    server: Optional[HostPort]


class HttpResponse(NamedTuple):
    status_code: int
    headers: List[Tuple[bytes, bytes]]
    body: Iterable[bytes]


class HttpDisconnect(NamedTuple):
    pass


HttpViewFunc = Union[Callable[[HttpRequest], Awaitable[HttpResponse]]]

HttpRoutePair = Tuple[RouteMatcher, HttpViewFunc]

HttpMiddlewareFunc = Callable[[HttpViewFunc, HttpRequest], Awaitable[HttpResponse]]


class HttpConfig(NamedTuple):
    routes: Tuple[HttpRoutePair, ...]
    middleware: Tuple[HttpMiddlewareFunc, ...]
