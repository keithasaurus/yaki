from hypothesis import given, settings
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_response_named_tuple
)
from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from typing import Callable
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request
from yaki.http.routes import normalize_routes, route_http
from yaki.http.types import HttpConfig, HttpRequest, HttpResponse, HttpViewFunc
from yaki.http.views import DEFAULT_404_RESPONSE
from yaki.routing.matchers import bracket_route_matcher, regex_route_matcher

import re


class RouteHttpTests(TestCase):
    @given(asgi_http_scope(),
           asgi_http_request(),
           http_response_named_tuple())
    @settings(max_examples=20)
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

        call_http_endpoint(endpoint, [test_asgi_request])

        self.assertEqual(result_target, ['middleware was run', test_response])

    @given(asgi_http_scope(),
           asgi_http_request())
    @settings(max_examples=20)
    def test_404_received_if_route_not_found(self,
                                             test_scope,
                                             test_request):
        endpoint = route_http(HttpConfig(routes=tuple(), middleware=tuple()),
                              test_scope)

        responses = call_http_endpoint(endpoint, [test_request])

        self.assertEqual(responses,
                         http_response_to_expected_parts(DEFAULT_404_RESPONSE))


class NormalizeRoutesTests(TestCase):
    @given(http_response_named_tuple(),
           http_response_named_tuple())
    @settings(max_examples=1)
    def test_two_tuple_routes(self, test_response_1, test_response_2):
        def view_func_1(request: HttpRequest) -> HttpResponse:
            return test_response_1

        def view_func_2(request: HttpRequest) -> HttpResponse:
            return test_response_2

        normalized_routes = normalize_routes([
            ("/path1", {"GET": view_func_1}),
            ("/path2", {"POST": view_func_2,
                        "PUT": view_func_1}),
            (regex_route_matcher(re.compile("^\d+$")), view_func_1),
            (regex_route_matcher("^something(?P<year>\d+)$"), {}),
            ("/name/{name}", view_func_2)
        ])

        route_1, route_2, route_3, route_4, route_5 = normalized_routes

        self.assertEqual(route_1[0]("/path1"), {})
        self.assertEqual(route_1[0]("/path12"), None)
        self.assertEqual(route_2[0]("/path2"), {})
        self.assertEqual(route_3[0]("1293123"), {})
        self.assertEqual(route_4[0]("something3203"), {"year": "3203"})
        self.assertEqual(route_5[0]("/name/keith"), {"name": "keith"})

        for route in normalized_routes:
            assert isinstance(route[1], (dict, Callable))
