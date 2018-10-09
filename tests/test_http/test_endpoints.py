from hypothesis import given, settings
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_response_named_tuple
)
from typing import List
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request, http_endpoint, respond
from yaki.http.types import HttpRequest, HttpResponse
from yaki.utils.types import AsgiEvent

import asyncio


def http_response_to_expected_parts(response: HttpResponse) -> List[AsgiEvent]:
    expected_body = []

    for body_bytes in response.body:
        expected_body.append({
            'type': 'http.response.body',
            'body': body_bytes,
            'more_body': True,
        })

    if len(expected_body) > 0:
        expected_body[-1]['more_body'] = False

    return [{
        'type': 'http.response.start',
        'status': response.status_code,
        'headers': [list(x) for x in response.headers]}] + expected_body


class RespondTests(TestCase):
    @given(http_response_named_tuple())
    @settings(max_examples=30)
    def test_send_gets_multiple_events(self, response):
        result_list = []

        async def sender(event: AsgiEvent) -> None:
            await asyncio.sleep(0)
            result_list.append(event)

        asyncio.run(respond(response, sender))

        self.assertEqual(result_list,
                         http_response_to_expected_parts(response))


class HttpEndpointTests(TestCase):
    @given(asgi_http_scope(), asgi_http_request(), http_response_named_tuple())
    @settings(max_examples=30)
    def test_async_view(self, test_scope, test_request, test_response):
        async def receive():
            await asyncio.sleep(0)
            return test_request

        result = []

        async def send(response: HttpResponse) -> None:
            await asyncio.sleep(0)
            result.append(response)

        async def test_view(request: HttpRequest) -> HttpResponse:
            assert request == asgi_to_http_request(test_request["body"],
                                                   test_scope)

            await asyncio.sleep(0)

            return test_response

        scoped_app = http_endpoint(test_view)(test_scope)

        asyncio.run(scoped_app(receive, send))

        self.assertEqual(result,
                         http_response_to_expected_parts(test_response))
