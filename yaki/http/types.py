from dataclasses import dataclass
from types import SimpleNamespace
from typing import (
    Any,
    Awaitable,
    Callable,
    NamedTuple,
    Optional,
    Union,
)

from mypy_extensions import Arg

from yaki.routing.types import MatcherOrStr, RouteMatcher
from yaki.types import Headers, HostPort, Scope


class HttpRequest(NamedTuple):
    body: bytes
    client: Optional[HostPort]
    custom: SimpleNamespace
    extensions: Optional[dict[str, dict[Any, Any]]]
    headers: list[tuple[bytes, bytes]]
    http_version: str
    method: str
    path: str
    query_params: dict[str, list[str]]
    root_path: str
    scheme: str
    scope_orig: Scope
    server: HostPort


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
    Callable[[HttpRequest, Arg(str)], Awaitable[HttpResponse]], HttpRequestResponseView
]

# if the route is just a view it accepts all methods.
# If it's a dict, it's the specified method(s)
HttpMethodView = Union[HttpView, dict[str, HttpView]]

HttpRoute = tuple[RouteMatcher, HttpMethodView]

HttpProtoRouteThreeTuple = tuple[MatcherOrStr, set[str], HttpView]
HttpProtoRouteTwoTuple = tuple[MatcherOrStr, HttpMethodView]

HttpProtoRoute = Union[HttpProtoRouteTwoTuple, HttpProtoRouteThreeTuple]


HttpMiddlewareFunc = Callable[
    [HttpRequestResponseView, HttpRequest], Awaitable[HttpResponse]
]


class HttpApp(NamedTuple):
    routes: tuple[HttpRoute, ...]
    middleware: tuple[HttpMiddlewareFunc, ...]
