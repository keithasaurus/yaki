from hypothesis import given, settings
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_response_named_tuple,
)
from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request, http_endpoint, respond
from yaki.http.types import HttpRequest, HttpResponse
from yaki.types import AsgiEvent

import asyncio


class RespondTests(TestCase):
    @given(http_response_named_tuple())
    @settings(max_examples=30)
    def test_send_gets_multiple_events(self, response):
        result_list = []

        async def sender(event: AsgiEvent) -> None:
            await asyncio.sleep(0)
            result_list.append(event)

        asyncio.run(respond(response, sender))

        self.assertEqual(result_list, http_response_to_expected_parts(response))


class HttpEndpointTests(TestCase):
    @given(asgi_http_scope(), asgi_http_request(), http_response_named_tuple())
    @settings(max_examples=30)
    def test_async_view(self, test_scope, test_request, test_response):
        async def test_view(request: HttpRequest) -> HttpResponse:
            assert request == asgi_to_http_request(test_request["body"], test_scope)

            await asyncio.sleep(0)

            return test_response

        endpoint = http_endpoint(test_view)(test_scope)

        sent_items = call_http_endpoint(endpoint, [test_request])

        self.assertEqual(sent_items, http_response_to_expected_parts(test_response))
