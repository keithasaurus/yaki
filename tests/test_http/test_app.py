import asyncio
from unittest import TestCase

from src.http.app import respond, request_response, asgi_to_http_request
from src.http.request.types import HttpRequest
from src.http.response.types import HttpResponse
from src.types import ASGIEvent

from hypothesis import given, settings

from tests.test_http.strategies import asgi_http_scope, asgi_http_request


class RespondTests(TestCase):
    def test_send_gets_multiple_events(self):
        result_list = []

        response = HttpResponse(status_code=200,
                                headers=[(b"header1", b"stuff"),
                                         (b"no2", b"other")],
                                body=[b"something"])

        async def sender(event: ASGIEvent) -> None:
            await asyncio.sleep(0)
            result_list.append(event)

        asyncio.run(respond(response, sender))

        self.assertEqual(result_list,
                         [{'headers': [(b'header1', b'stuff'), (b'no2', b'other')],
                           'status': 200,
                           'type': 'http.response.start'},
                          {'body': b'something',
                           'more_body': False,
                           'type': 'http.response.body'}])


class RequestResponseTest(TestCase):
    @given(asgi_http_scope(), asgi_http_request())
    @settings(max_examples=10)
    def test_works_with_sync_view(self, test_scope, test_request):
        async def receive():
            await asyncio.sleep(0)
            return test_request

        result = []

        async def send(response: HttpResponse) -> None:
            result.append(response)

        def test_view(request: HttpRequest) -> HttpResponse:
            assert request == asgi_to_http_request(test_request["body"],
                                                   test_scope)

            return HttpResponse(status_code=400,
                                headers=[(b"one", b"header")],
                                body=[b"bad request"])

        app = request_response(test_view)

        scoped = app(test_scope)

        asyncio.run(scoped(receive, send))

        self.assertEqual(result,
                         [{'headers': [(b'one', b'header')],
                           'status': 400,
                           'type': 'http.response.start'},
                          {'body': b'bad request', 'more_body': False,
                              'type': 'http.response.body'}])

