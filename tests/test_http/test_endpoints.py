from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request, http_endpoint, respond
from yaki.http.types import HttpRequest, HttpResponse
from yaki.types import AsgiEvent

import asyncio


class RespondTests(TestCase):
    def test_send_gets_multiple_events(self):
        response = HttpResponse(status_code=200, headers=[], body=b"ok")
        result_list = []

        async def sender(event: AsgiEvent) -> None:
            await asyncio.sleep(0)
            result_list.append(event)

        asyncio.run(respond(response, sender))

        self.assertEqual(result_list, http_response_to_expected_parts(response))


class HttpEndpointTests(TestCase):
    def test_async_view(self):
        test_scope = {
            "type": "http",
            "headers": [],
            "http_version": "1.1",
            "method": "GET",
            "path": "/",
            "query_string": b"",
            "extensions": {},
            "server": ["127.0.0.1", 8000],
            "client": ["127.0.0.1", 5000],
            "scheme": "http",
            "root_path": "",
        }
        test_request = {"type": "http.request", "body": b"hello", "more_body": False}
        test_response = HttpResponse(status_code=201, headers=[[b"a", b"b"]], body=b"resp")

        async def test_view(request: HttpRequest) -> HttpResponse:
            assert request == asgi_to_http_request(test_request["body"], test_scope)

            await asyncio.sleep(0)

            return test_response

        endpoint = http_endpoint(test_view)(test_scope)

        sent_items = call_http_endpoint(endpoint, [test_request])

        self.assertEqual(sent_items, http_response_to_expected_parts(test_response))
