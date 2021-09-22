from dataclasses import dataclass
from functools import partial
from typing import Callable, Tuple, Union
from yaki.http.routes import route_http
from yaki.http.types import HttpApp
from yaki.types import AsgiInstance, Scope
from yaki.websockets.routes import route_ws
from yaki.websockets.types import WSApp

AppConfig = Union[HttpApp, WSApp]


@dataclass
class Apps:
    http: Tuple[Callable[[Scope], Tuple[bool, AsgiInstance]], ...]
    websocket: Tuple[Callable[[Scope], Tuple[bool, AsgiInstance]], ...]


def _app_configs_to_routers_dict(apps: Tuple[AppConfig, ...]) -> Apps:
    http_apps = []
    websocket_apps = []

    for app_config in apps:
        if isinstance(app_config, HttpApp):
            http_apps.append(app_config)
        else:
            websocket_apps.append(app_config)

    # at least one empty app of each kind so we can send empty responses
    if len(http_apps) == 0:
        http_apps = [HttpApp(routes=tuple(), middleware=tuple())]

    if len(websocket_apps) == 0:
        websocket_apps = [WSApp(routes=tuple())]

    return Apps(
        http=tuple(partial(route_http, conf) for conf in http_apps),
        websocket=tuple(partial(route_ws, conf) for conf in websocket_apps),
    )


def yaki(*apps: AppConfig) -> Callable[[Scope], AsgiInstance]:
    """
    Typically you shouldn't need more than one or two apps: one for http
    and maybe one for websockets. If, however, you want something like
    different middleware for different parts of your project, you can
    specify that with multiple apps.
    """
    route_choices = _app_configs_to_routers_dict(apps)

    def get_route(scope: Scope) -> AsgiInstance:
        scope_type = scope["type"]
        assert isinstance(scope_type, str)
        if scope_type == "websocket":
            app_routers = route_choices.websocket
        elif scope_type == "http":
            app_routers = route_choices.http
        else:
            raise AssertionError('type must be either "websocket" or "http"')

        for i, app_router in enumerate(app_routers):
            # if not found the app is expected to return
            # some sort of "not found" view
            found, endpoint = app_router(scope)

            if found:
                return endpoint
            else:
                if i == len(app_routers) - 1:
                    return endpoint
        else:
            raise Exception("Should have returned a response")

    return get_route
