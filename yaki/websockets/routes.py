from typing import Tuple
from yaki.utils.types import AsgiInstance, Scope
from yaki.websockets.endpoints import ws_endpoint
from yaki.websockets.types import WSApp


class Asgi404(Exception):
    pass


def route_ws(config: WSApp, scope: Scope) -> Tuple[bool, AsgiInstance]:
    path = scope['path']

    assert isinstance(path, str)

    for route_matcher, ws_view_func in config.routes:
        if isinstance(route_matcher(path), dict):
            return True, ws_endpoint(ws_view_func)(scope)
    else:
        raise Asgi404('todo: handle not found websocket!')
