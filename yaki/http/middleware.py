from datetime import datetime
from functools import partial
from typing import Tuple
from yaki.http.types import (
    HttpMiddlewareFunc,
    HttpRequest,
    HttpResponse,
    HttpViewFunc
)


async def logging_middleware(view_func: HttpViewFunc,
                             request: HttpRequest) -> HttpResponse:
    print(request.path)

    return await view_func(request)


async def timing_middleware(view_func: HttpViewFunc,
                            request: HttpRequest) -> HttpResponse:
    start = datetime.now()

    result = await view_func(request)

    end = datetime.now()

    print(f"took {end - start}")

    return result


def combine_middleware(middleware: Tuple[HttpMiddlewareFunc, ...],
                       view_func: HttpViewFunc) -> HttpViewFunc:
    middleware_and_view_func = view_func
    # Note that the list of the middleware is reversed for it to apply in order
    for middleware_func in middleware[::-1]:
        middleware_and_view_func = partial(middleware_func,
                                           middleware_and_view_func)
    return middleware_and_view_func
