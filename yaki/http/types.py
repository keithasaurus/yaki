from dataclasses import dataclass
from mypy_extensions import Arg
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Union
)
from yaki.routing.matchers import RouteMatcher
from yaki.routing.types import MatcherOrStr
from yaki.types import Headers, HostPort, Scope


class HttpRequest(NamedTuple):
    body: bytes
    client: Optional[HostPort]
    custom: SimpleNamespace
    extensions: Optional[Dict[str, Dict[Any, Any]]]
    headers: List[Tuple[bytes, bytes]]
    http_version: str
    method: str
    path: str
    query_params: Dict[str, List[str]]
    root_path: str
    scheme: str
    scope_orig: Scope
    server: Optional[HostPort]


# friendlier types
ResponseTypes = Union[str, bytes]


@dataclass
class HttpResponse:
    """
    using dataclass instead of named tuple for mutability... if
    responses are large, it may be problematic to create whole
    new objects in middleware
    """
    status_code: int
    headers: Headers
    body: bytes


class HttpDisconnect(NamedTuple):
    pass


# Just the request and response
HttpRequestResponseView = Callable[[HttpRequest], Awaitable[HttpResponse]]

HttpView = Union[
    Callable[[HttpRequest, Arg(str)], Awaitable[HttpResponse]],
    HttpRequestResponseView
]

# if the route is just a view it accepts all methods.
# If it's a dict, it's the specified method(s)
HttpMethodView = Union[HttpView, Dict[str, HttpView]]

HttpRoute = Tuple[RouteMatcher, HttpMethodView]

HttpProtoRouteThreeTuple = Tuple[MatcherOrStr, Set[str], HttpView]
HttpProtoRouteTwoTuple = Tuple[MatcherOrStr, HttpMethodView]

HttpProtoRoute = Union[
    HttpProtoRouteTwoTuple,
    HttpProtoRouteThreeTuple
]


HttpMiddlewareFunc = Callable[[HttpRequestResponseView, HttpRequest],
                              Awaitable[HttpResponse]]


class HttpApp(NamedTuple):
    routes: Tuple[HttpRoute, ...]
    middleware: Tuple[HttpMiddlewareFunc, ...]
