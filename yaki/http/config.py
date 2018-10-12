from typing import Iterable
from yaki.http.routes import normalize_routes
from yaki.http.types import HttpApp, HttpMiddlewareFunc, HttpProtoRoute


def http_app(routes: Iterable[HttpProtoRoute],
             middleware: Iterable[HttpMiddlewareFunc]) -> HttpApp:
    """
    Just a convenience function that normalizes different kinds of input into
    HttpApp
    """
    return HttpApp(
        routes=normalize_routes(routes),
        middleware=tuple(middleware)
    )
