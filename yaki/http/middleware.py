from functools import partial
from typing import Tuple
from yaki.http.types import HttpMiddlewareFunc, HttpViewFunc


def combine_middleware(middleware: Tuple[HttpMiddlewareFunc, ...],
                       view_func: HttpViewFunc) -> HttpViewFunc:
    middleware_and_view_func = view_func
    # Note that the list of the middleware is reversed for it to apply in order
    for middleware_func in middleware[::-1]:
        middleware_and_view_func = partial(middleware_func,
                                           middleware_and_view_func)
    return middleware_and_view_func
