from functools import partial
from typing import Union
from yaki.http.routes import route_http
from yaki.http.types import HttpApp
from yaki.utils.types import AsgiInstance, Scope
from yaki.websockets.routes import route_ws
from yaki.websockets.types import WSApp

AppConfig = Union[HttpApp, WSApp]


def yaki(*apps: AppConfig):
    """
    Typically you shouldn't need more than one or two apps: one for http
    and one for websockets. If, however, you want something like
    different middleware for different parts of your project, you can
    specify that with multiple apps.
    """
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

    route_choices = {
        'http': tuple(partial(route_http, conf) for conf in http_apps),
        'websocket': tuple(partial(route_ws, conf) for conf in websocket_apps)
    }

    def get_route(scope: Scope) -> AsgiInstance:
        scope_type = scope['type']
        assert isinstance(scope_type, str)

        app_routers = route_choices[scope_type]

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
            raise Exception('Should have returned a response')

    return get_route
