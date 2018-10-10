from hypothesis import given, settings
from hypothesis import strategies as st
from tests.test_http.strategies import (
    http_request_named_tuple,
    http_response_named_tuple
)
from tests.utils.logging import SelfLogger
from unittest import TestCase
from yaki.http.middleware import (
    combine_middleware,
    exception_500_middleware_default_response
)
from yaki.http.types import HttpRequest, HttpResponse, HttpViewFunc

import asyncio
import logging


class CombineMiddlewareTests(TestCase):
    @given(http_request_named_tuple(),
           http_response_named_tuple())
    @settings(max_examples=20)
    def test_executes_in_filo_order(self, test_request, test_response):
        events = []

        async def middleware_1(view_func: HttpViewFunc,
                               request: HttpRequest) -> HttpResponse:
            events.append(1)

            response = await view_func(request)

            events.append(4)

            return response

        async def middleware_2(view_func: HttpViewFunc,
                               request: HttpRequest) -> HttpResponse:
            events.append('b')
            response = await view_func(request)

            events.append('c')
            return response

        async def view_func(request: HttpRequest):
            events.append('the view happened')

            return test_response

        combined_func = combine_middleware(
            (middleware_1, middleware_2),
            view_func
        )

        result = asyncio.run(combined_func(test_request))

        self.assertEqual(result, test_response)

        self.assertEqual(events,
                         [1, 'b', 'the view happened', 'c', 4])


class Exception500Tests(TestCase):
    @given(http_request_named_tuple(),
           st.text(max_size=200))
    @settings(max_examples=20)
    def test_default_responder_returns_proper_result_when_exception_raised(
            self,
            test_request,
            exception_message):
        test_exception = Exception(exception_message)

        async def view(request: HttpRequest) -> HttpResponse:
            raise test_exception

        logger = SelfLogger(__file__)

        combined_func = combine_middleware(
            (exception_500_middleware_default_response(logger),),
            view)

        asyncio.run(combined_func(test_request))

        self.assertEqual(logger.logged_messages,
                         {logging.ERROR: [str(test_exception)]})
