from functools import partial
from logging import Logger
from typing import Callable, Tuple
from yaki.http.types import (
    HttpMiddlewareFunc,
    HttpRequest,
    HttpRequestResponseView,
    HttpResponse,
)


def default_error_responder(exception: Exception) -> HttpResponse:
    """
    By default we are not communicating any information about the exception to the
    client
    """
    return HttpResponse(status_code=500, headers=[], body=b"Server Error")


def exception_500_middleware(
    logger: Logger, error_responder: Callable[[Exception], HttpResponse]
) -> HttpMiddlewareFunc:
    """
    Catches any exception that has bubbled up and logs it using whatever logger
    the user prefers
    :param logger: determines where and how the message is logged
    :param error_responder: create the HttpResponse to be sent
    """

    async def inner(
        view_func: HttpRequestResponseView, request: HttpRequest
    ) -> HttpResponse:
        try:
            return await view_func(request)
        except Exception as e:
            logger.error(str(e))

            return error_responder(e)

    return inner


exception_500_middleware_default_response = partial(
    exception_500_middleware, error_responder=default_error_responder
)


def combine_middleware(
    middleware: Tuple[HttpMiddlewareFunc, ...], view_func: HttpRequestResponseView
) -> HttpRequestResponseView:
    middleware_and_view_func = view_func
    # Note that the list of the middleware is reversed for it to apply in order
    for middleware_func in middleware[::-1]:
        middleware_and_view_func = partial(middleware_func, middleware_and_view_func)
    return middleware_and_view_func
