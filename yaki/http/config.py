from typing import Iterable

from yaki.http.routes import normalize_routes
from yaki.http.types import HttpConfig, HttpProtoRoute, HttpMiddlewareFunc


def http_config(routes: Iterable[HttpProtoRoute],
                middleware: Iterable[HttpMiddlewareFunc]) -> HttpConfig:
    """
    Just a convenience function that normalizes different kinds of input into
    HttpConfig
    """
    return HttpConfig(
        routes=normalize_routes(routes),
        middleware=tuple(middleware)
    )
