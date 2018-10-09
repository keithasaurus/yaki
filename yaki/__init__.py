from functools import partial
from typing import Tuple, List, NamedTuple, Callable, Awaitable

from yaki.http.app import HttpViewFunc, http_app
from yaki.http.request.types import HttpRequest
from yaki.http.response.types import HttpResponse
from yaki.http.views import http_404_view
from yaki.routes import RouteMatcher
from yaki.utils.types import Scope, AsgiInstance
from yaki.websockets.app import WSViewFunc, ws_app


HttpRoutePair = Tuple[RouteMatcher, HttpViewFunc]
HttpMiddlewareFunc = Callable[[HttpViewFunc, HttpRequest], Awaitable[HttpResponse]]


class HttpConfig(NamedTuple):
    routes: Tuple[HttpRoutePair, ...]
    middleware: Tuple[HttpMiddlewareFunc, ...]


class WSConfig(NamedTuple):
    routes: List[Tuple[RouteMatcher, WSViewFunc]]


def yaki_app(http: HttpConfig, ws: WSConfig):
    def get_route(scope: Scope) -> AsgiInstance:
        type = scope['type']
        path = scope['path']
        assert isinstance(type, str)
        assert isinstance(path, str)

        if type == 'http':
            for route_matcher, view_func in http.routes:
                route_match_result = route_matcher(path)
                if isinstance(route_match_result, dict):
                    if len(route_match_result) == 0:
                        view_func = view_func
                    else:
                        view_func = partial(view_func, route_match_result)
                    break
            else:
                view_func = http_404_view

            middleware_and_view_func = view_func
            for middleware_func in http.middleware[::-1]:
                middleware_and_view_func = partial(middleware_func,
                                                   middleware_and_view_func)

            return http_app(middleware_and_view_func)(scope)
        elif type == 'websocket':
            for route_matcher, ws_view_func in ws.routes:
                if isinstance(route_matcher(path), dict):
                    return ws_app(ws_view_func)(scope)

        raise ValueError(f"Invalid scope type. Got: '{type}'")
    return get_route


__all__ = ['yaki_app']