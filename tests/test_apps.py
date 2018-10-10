from hypothesis import given
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_response_named_tuple
)
from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from tests.test_websockets.strategies import asgi_ws_scope
from unittest import TestCase
from yaki.apps import yaki_app_http_only
from yaki.http.types import HttpConfig, HttpRequest, HttpResponse
from yaki.routes import bracket_route_matcher
from yaki.websockets.routes import Asgi404


class YakiAppTests(TestCase):
    @given(asgi_http_scope(),
           asgi_ws_scope(),
           asgi_http_request(),
           http_response_named_tuple())
    def test_uses_http_app(self,
                           test_http_scope,
                           test_asgi_ws_scope,
                           test_asgi_http_request,
                           test_response):
        endpoint_path = '/'
        test_http_scope['path'] = endpoint_path

        async def view(request: HttpRequest) -> HttpResponse:
            return test_response

        app = yaki_app_http_only(
            HttpConfig(
                routes=(
                    (bracket_route_matcher(endpoint_path), view),
                ),
                middleware=tuple()
            )
        )

        endpoint = app(test_http_scope)

        sent_items = call_http_endpoint(endpoint, [test_asgi_http_request])

        self.assertEqual(sent_items,
                         http_response_to_expected_parts(test_response))

        # also show that the websocket doesnt work
        with self.assertRaises(Asgi404):
            app(test_asgi_ws_scope)
