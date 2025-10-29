from tests.utils.logging import SelfLogger
from unittest import TestCase
from yaki.http.middleware import (
    combine_middleware,
    exception_500_middleware_default_response,
)
from yaki.http.types import HttpRequest, HttpRequestResponseView, HttpResponse

import asyncio
import logging
from types import SimpleNamespace


def make_request(method: str = "GET") -> HttpRequest:
    return HttpRequest(
        body=b"",
        client=["127.0.0.1", 5000],
        custom=SimpleNamespace(),
        extensions={},
        headers=[],
        http_version="1.1",
        method=method,
        path="/",
        query_params={},
        root_path="",
        scheme="http",
        scope_orig={
            "type": "http",
            "headers": [],
            "http_version": "1.1",
            "method": method,
            "path": "/",
            "query_string": b"",
            "extensions": {},
            "server": ["127.0.0.1", 8000],
            "client": ["127.0.0.1", 5000],
            "scheme": "http",
            "root_path": "",
        },
        server=["127.0.0.1", 8000],
    )


class CombineMiddlewareTests(TestCase):
    def test_executes_in_filo_order(self):
        events = []
        test_request = make_request()
        test_response = HttpResponse(status_code=200, headers=[], body=b"ok")

        async def middleware_1(
            view_func: HttpRequestResponseView, request: HttpRequest
        ) -> HttpResponse:
            events.append(1)

            response = await view_func(request)

            events.append(4)

            return response

        async def middleware_2(
            view_func: HttpRequestResponseView, request: HttpRequest
        ) -> HttpResponse:
            events.append("b")
            response = await view_func(request)

            events.append("c")
            return response

        async def view(request: HttpRequest):
            events.append("the view happened")

            return test_response

        combined_func = combine_middleware((middleware_1, middleware_2), view)

        result = asyncio.run(combined_func(test_request))

        self.assertEqual(result, test_response)

        self.assertEqual(events, [1, "b", "the view happened", "c", 4])

    def test_middleware_can_edit_custom_obj(self):
        test_val = "bob"
        test_request = make_request()
        test_response = HttpResponse(status_code=200, headers=[], body=b"ok")

        async def name_middleware(
            view_func: HttpRequestResponseView, request: HttpRequest
        ) -> HttpResponse:
            request.custom.name = test_val

            return await view_func(request)

        async def view(request: HttpRequest):
            assert request.custom.name == test_val

            return test_response

        combined_func = combine_middleware((name_middleware,), view)

        result = asyncio.run(combined_func(test_request))

        self.assertEqual(result, test_response)


class Exception500Tests(TestCase):
    def test_default_responder_returns_proper_result_when_exception_raised(self):
        test_request = make_request()
        exception_message = "uh oh"
        test_exception = Exception(exception_message)

        async def view(request: HttpRequest) -> HttpResponse:
            raise test_exception

        logger = SelfLogger(__file__)

        combined_func = combine_middleware(
            (exception_500_middleware_default_response(logger),), view
        )

        asyncio.run(combined_func(test_request))

        self.assertEqual(logger.logged_messages, {logging.ERROR: [str(test_exception)]})
