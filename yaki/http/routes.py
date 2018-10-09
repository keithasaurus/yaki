from functools import partial
from yaki.http.endpoints import http_endpoint
from yaki.http.types import HttpConfig
from yaki.http.views import http_404_view
from yaki.utils.types import Scope


def route_http(config: HttpConfig, scope: Scope):
    path = scope['path']
    assert isinstance(path, str)

    for route_matcher, view_func in config.routes:
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
    for middleware_func in config.middleware[::-1]:
        middleware_and_view_func = partial(middleware_func,
                                           middleware_and_view_func)

    return http_endpoint(middleware_and_view_func)(scope)
