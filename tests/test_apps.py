from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from unittest import TestCase
from yaki.apps import yaki
from yaki.http.config import http_app
from yaki.http.types import HttpRequest, HttpResponse
from yaki.websockets.routes import Asgi404


class YakiAppTests(TestCase):
    def test_uses_http_app(self):
        endpoint_path = "/"
        test_http_scope = {
            "type": "http",
            "headers": [],
            "http_version": "1.1",
            "method": "GET",
            "path": endpoint_path,
            "query_string": b"",
            "extensions": {},
            "server": ["127.0.0.1", 8000],
            "client": ["127.0.0.1", 5000],
            "scheme": "http",
            "root_path": "",
        }
        test_asgi_http_request = {"type": "http.request", "body": b"hi", "more_body": False}
        test_response = HttpResponse(status_code=200, headers=[], body=b"ok")

        async def view(request: HttpRequest) -> HttpResponse:
            return test_response

        app = yaki(
            http_app(
                routes=[
                    (endpoint_path, view),
                ],
                middleware=[],
            )
        )

        endpoint = app(test_http_scope)

        sent_items = call_http_endpoint(endpoint, [test_asgi_http_request])

        self.assertEqual(sent_items, http_response_to_expected_parts(test_response))

        # also show that the websocket doesnt work
        test_asgi_ws_scope = {
            "type": "websocket",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "root_path": "",
            "client": ["127.0.0.1", 5000],
            "server": ["127.0.0.1", 8000],
            "subprotocols": ["chat"],
            "extensions": {},
            "scheme": "ws",
        }
        with self.assertRaises(Asgi404):
            app(test_asgi_ws_scope)
