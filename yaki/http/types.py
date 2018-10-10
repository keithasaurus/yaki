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
    Union,
    Set)
from yaki.routing.matchers import RouteMatcher
from yaki.routing.types import MatcherOrStr
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
    body: Union[bytes, Iterable[bytes]]


class HttpDisconnect(NamedTuple):
    pass


HttpViewFunc = Union[Callable[[HttpRequest], Awaitable[HttpResponse]]]


# if the route is just a view it accepts all methods.
# If it's a dict, it's the specified method(s)
HttpMethodView = Union[HttpViewFunc, Dict[str, HttpViewFunc]]

HttpRoute = Tuple[RouteMatcher, HttpMethodView]

HttpProtoRouteThreeTuple = Tuple[MatcherOrStr, Set[str], HttpViewFunc]
HttpProtoRouteTwoTuple = Tuple[MatcherOrStr, HttpMethodView]

HttpProtoRoute = Union[
    HttpProtoRouteTwoTuple,
    HttpProtoRouteThreeTuple
]


HttpMiddlewareFunc = Callable[[HttpViewFunc, HttpRequest], Awaitable[HttpResponse]]


class HttpConfig(NamedTuple):
    routes: Tuple[HttpRoute, ...]
    middleware: Tuple[HttpMiddlewareFunc, ...]
