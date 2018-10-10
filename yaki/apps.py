from functools import partial
from yaki.http.routes import route_http
from yaki.http.types import HttpConfig
from yaki.utils.types import AsgiInstance, Scope
from yaki.websockets.routes import route_ws
from yaki.websockets.types import WSConfig


def yaki_app(http: HttpConfig, ws: WSConfig):
    route_choices = {
        'http': partial(route_http, http),
        'websocket': partial(route_ws, ws)
    }

    def get_route(scope: Scope) -> AsgiInstance:
        scope_type = scope['type']
        assert isinstance(scope_type, str)

        return route_choices[scope_type](scope)

    return get_route


yaki_app_http_only = partial(yaki_app, ws=WSConfig(routes=[]))
