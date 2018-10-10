from hypothesis import given, settings
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_response_named_tuple
)
from tests.test_http.utils import http_response_to_expected_parts
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request
from yaki.http.routes import route_http
from yaki.http.types import HttpConfig, HttpRequest, HttpResponse, HttpViewFunc
from yaki.http.views import DEFAULT_404_RESPONSE
from yaki.routes import bracket_route_matcher
from yaki.utils.types import AsgiEvent

import asyncio


class RouteHttpTests(TestCase):
    @given(asgi_http_scope(),
           asgi_http_request(),
           http_response_named_tuple())
    @settings(max_examples=30)
    def test_response_is_correct(self,
                                 test_scope,
                                 test_asgi_request,
                                 test_response):
        endpoint_path = '/'
        test_scope['path'] = endpoint_path  # have to make sure the view is hit

        request_named_tuple = asgi_to_http_request(
            test_asgi_request['body'],
            test_scope
        )

        result_target = []

        async def middleware_func(view_func: HttpViewFunc,
                                  request: HttpRequest) -> HttpResponse:
            self.assertEqual(request, request_named_tuple)
            result_target.append('middleware was run')
            response = await view_func(request)

            result_target.append(test_response)
            return response

        async def view(request: HttpRequest) -> HttpResponse:
            self.assertEqual(request, request_named_tuple)
            return test_response

        async def sender(response: HttpResponse) -> None:
            # not important
            pass

        async def receiver() -> AsgiEvent:
            await asyncio.sleep(0)
            return test_asgi_request

        endpoint = route_http(
            HttpConfig(
                routes=(
                    (bracket_route_matcher(endpoint_path), view),
                ),
                middleware=(
                    middleware_func,
                )),
            test_scope
        )

        asyncio.run(endpoint(receiver, sender))

        self.assertEqual(
            result_target,
            ['middleware was run', test_response])

    @given(asgi_http_scope(),
           asgi_http_request())
    @settings(max_examples=30)
    def test_404_received_if_route_not_found(self,
                                             test_scope,
                                             test_request):
        responses = []

        async def sender(event: AsgiEvent) -> None:
            responses.append(event)

        async def receiver() -> AsgiEvent:
            return test_request

        endpoint = route_http(HttpConfig(routes=tuple(), middleware=tuple()),
                              test_scope)

        asyncio.run(endpoint(receiver, sender))

        self.assertEqual(responses,
                         http_response_to_expected_parts(DEFAULT_404_RESPONSE))
