from functools import partial
from typing import Iterable, Tuple, Dict, Callable

from yaki.http.endpoints import http_endpoint
from yaki.http.middleware import combine_middleware
from yaki.http.types import HttpConfig, HttpProtoRoute, HttpRoute, \
    HttpProtoRouteThreeTuple, HttpProtoRouteTwoTuple, HttpViewFunc, HttpMethodView
from yaki.http.views import http_404_view, http_405_view
from yaki.routing.matchers import bracket_route_matcher
from yaki.routing.types import MatcherOrStr, RouteMatcher
from yaki.utils.types import Scope


def method_view_to_view_func(method: str,
                             parsed_params: Dict[str, str],
                             method_view: HttpMethodView) -> HttpViewFunc:
    if isinstance(method_view, dict):
        view_func = method_view.get(method.upper())

        return http_405_view if view_func is None else view_func
    else:  # view func valid for all methods
        view_func = method_view

        if len(parsed_params) == 0:
            view_func = view_func
        else:
            view_func = partial(view_func, **parsed_params)
        return view_func


def route_http(config: HttpConfig, scope: Scope):
    path = scope['path']
    assert isinstance(path, str)

    for route_matcher, method_view in config.routes:
        route_match_result = route_matcher(path)
        if isinstance(route_match_result, dict):
            scope_method = scope['method']
            assert isinstance(scope_method, str)
            view_func = method_view_to_view_func(scope_method,
                                                 route_match_result,
                                                 method_view)
            break

    else:
        view_func = http_404_view

    middleware_and_view_func = combine_middleware(config.middleware,
                                                  view_func)

    return http_endpoint(middleware_and_view_func)(scope)


def normalize_route_matcher(matcher: MatcherOrStr) -> RouteMatcher:
    return (
        bracket_route_matcher(matcher)
        if isinstance(matcher, str) else matcher
    )


def three_tuple_proto_to_route(proto_route: HttpProtoRouteThreeTuple) -> HttpRoute:
    matcher, method_set, view = proto_route

    return (normalize_route_matcher(matcher),
            {method.upper(): view for method in method_set})


def two_tuple_proto_to_route(proto_route: HttpProtoRouteTwoTuple) -> HttpRoute:
    matcher, view = proto_route

    new_view: HttpMethodView = {}
    if isinstance(view, dict):
        new_view = {
            k.upper(): v for k, v in view.items()
        }
    else:
        new_view = view

    new_matcher = normalize_route_matcher(matcher)

    return new_matcher, new_view


def normalize_routes(
        proto_routes: Iterable[HttpProtoRoute]
) -> Tuple[HttpRoute, ...]:
    routes = []
    for proto_route in proto_routes:
        # note that mypy isn't able to determine that we're essentially
        # pattern matching on tuple length, so ignoring type below.
        if len(proto_route) == 3:
            routes.append(three_tuple_proto_to_route(proto_route))  # type: ignore
        elif len(proto_route) == 2:
            routes.append(two_tuple_proto_to_route(proto_route))  # type: ignore
        else:
            raise ValueError("Bad Route! Wrong sized tuple")

    return tuple(routes)
