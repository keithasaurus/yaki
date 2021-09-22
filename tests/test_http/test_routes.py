from hypothesis import given, settings
from hypothesis import strategies as st
from tests.test_http.strategies import (
    asgi_http_request,
    asgi_http_scope,
    http_request_named_tuple,
    http_response_named_tuple,
)
from tests.test_http.utils import call_http_endpoint, http_response_to_expected_parts
from typing import Callable
from unittest import TestCase
from yaki.http.endpoints import asgi_to_http_request
from yaki.http.methods import DELETE, GET, POST, PUT
from yaki.http.routes import method_view_to_view_func, normalize_routes, route_http
from yaki.http.types import HttpApp, HttpRequest, HttpRequestResponseView, HttpResponse
from yaki.http.views import DEFAULT_404_RESPONSE, DEFAULT_405_RESPONSE
from yaki.routing.matchers import bracket_route_matcher, regex_route_matcher

import asyncio
import re


class RouteHttpTests(TestCase):
    @given(asgi_http_scope(), asgi_http_request(), http_response_named_tuple())
    @settings(max_examples=20)
    def test_response_is_correct(self, test_scope, test_asgi_request, test_response):
        endpoint_path = "/"
        test_scope["path"] = endpoint_path  # have to make sure the view is hit

        request_named_tuple = asgi_to_http_request(
            test_asgi_request["body"], test_scope
        )

        result_target = []

        async def middleware_func(
            view_func: HttpRequestResponseView, request: HttpRequest
        ) -> HttpResponse:
            self.assertEqual(request, request_named_tuple)
            result_target.append("middleware was run")
            response = await view_func(request)

            result_target.append(test_response)
            return response

        async def view(request: HttpRequest) -> HttpResponse:
            self.assertEqual(request, request_named_tuple)
            return test_response

        _, endpoint = route_http(
            HttpApp(
                routes=((bracket_route_matcher(endpoint_path), view),),
                middleware=(middleware_func,),
            ),
            test_scope,
        )

        call_http_endpoint(endpoint, [test_asgi_request])

        self.assertEqual(result_target, ["middleware was run", test_response])

    @given(asgi_http_scope(), asgi_http_request())
    @settings(max_examples=20)
    def test_404_received_if_route_not_found(self, test_scope, test_request):
        _, endpoint = route_http(
            HttpApp(routes=tuple(), middleware=tuple()), test_scope
        )

        responses = call_http_endpoint(endpoint, [test_request])

        self.assertEqual(
            responses, http_response_to_expected_parts(DEFAULT_404_RESPONSE)
        )


class NormalizeRoutesTests(TestCase):
    @given(http_response_named_tuple(), http_response_named_tuple())
    @settings(max_examples=1)
    def test_two_and_three_tuple_routes(self, test_response_1, test_response_2):
        def view_func_1(request: HttpRequest) -> HttpResponse:
            return test_response_1

        def view_func_2(request: HttpRequest) -> HttpResponse:
            return test_response_2

        normalized_routes = normalize_routes(
            [
                ("/path1", {"GET": view_func_1}),
                ("/path2", {"POST": view_func_2, "PUT": view_func_1}),
                (regex_route_matcher(re.compile(r"^\d+$")), view_func_1),
                (regex_route_matcher(r"^something(?P<year>\d+)$"), {}),
                ("/name/{name}", view_func_2),
                (bracket_route_matcher("/other/{month}"), {"GET", "POST"}, view_func_1),
            ]
        )

        for route in normalized_routes:
            assert len(route) == 2
            assert isinstance(route[0], Callable)
            assert isinstance(route[1], (dict, Callable))

        route_1, route_2, route_3, route_4, route_5, route_6 = normalized_routes

        self.assertEqual(route_1[0]("/path1"), {})
        self.assertEqual(route_1[0]("/path12"), None)
        self.assertEqual(route_2[0]("/path2"), {})
        self.assertEqual(route_3[0]("1293123"), {})
        self.assertEqual(route_4[0]("something3203"), {"year": "3203"})
        self.assertEqual(route_5[0]("/name/alice"), {"name": "alice"})
        self.assertEqual(route_6[0]("/other/march"), {"month": "march"})

    def test_raises_error_for_wrong_sized_tuple(self):
        for test_tuple in [
            tuple(),
            (1,),
            (1, 2, 3, 4),
        ]:
            with self.assertRaises(ValueError):
                normalize_routes([test_tuple])


class MethodViewToViewFuncTests(TestCase):
    @given(
        http_request_named_tuple(),
        http_response_named_tuple(),
        st.text(max_size=10),
        st.text(max_size=10),
    )
    @settings(max_examples=5)
    def test_converts_dicts_to_kwargs(
        self, test_request, test_response, test_name, test_age
    ):
        def assert_correct(request: HttpRequest, name: str, age: str):
            assert request == test_request
            assert name == test_name
            assert age == test_age
            return test_response

        async def view_request_first(
            request: HttpRequest, name: str, age: str
        ) -> HttpResponse:
            return assert_correct(request, name, age)

        async def view_kwargs(request: HttpRequest, **kwargs) -> HttpResponse:
            return assert_correct(request, kwargs["name"], kwargs["age"])

        for view in [view_request_first, view_kwargs]:
            new_func = method_view_to_view_func(
                GET,
                {"name": test_name, "age": test_age},
                # todo: remove when kwargs are part of type signature
                view,
            )

            self.assertEqual(asyncio.run(new_func(test_request)), test_response)

    @given(http_request_named_tuple(), http_response_named_tuple())
    def test_dict_method_view_returns_405_for_invalid(
        self, test_request, test_response
    ):

        test_request = test_request._replace(method=POST)

        async def view(request: HttpRequest) -> HttpResponse:
            return test_response

        view_func = method_view_to_view_func(
            POST, parsed_params={}, method_view={GET: view, PUT: view, DELETE: view}
        )

        self.assertEqual(asyncio.run(view_func(test_request)), DEFAULT_405_RESPONSE)
