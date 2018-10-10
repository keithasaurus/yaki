from hypothesis import strategies as st
from tests.utils.strategies import (
    coinflip,
    header_string,
    headers,
    host_and_port,
    query_string,
    scope_extensions
)
from yaki.http.types import HttpRequest, HttpResponse
from yaki.utils.types import HostPort

import random


def gen_http_version():
    return random.choice(["1.0", "1.1", "1.2"])


def gen_http_method():
    return random.choice(["CONNECT",
                          "DELETE",
                          "GET",
                          "HEAD",
                          "OPTIONS",
                          "PATCH",
                          "POST",
                          "PUT",
                          "TRACE"])


@st.composite
def asgi_http_scope(draw):
    # some of these keys are optional but can't reason about
    # how hypothesis is handling at the moment
    return {
        "type": "http",
        "headers": draw(headers()),
        "http_version": gen_http_version(),
        "method": gen_http_method(),
        "path": "/" + draw(st.text(max_size=1000)),
        "query_string": draw(query_string()),
        'extensions': draw(scope_extensions()),
        'server': draw(host_and_port()),
        'client': draw(host_and_port()),
        'scheme': draw(st.text(min_size=1)),
        'root_path': draw(st.text(max_size=100))
    }


@st.composite
def asgi_http_request(draw):
    # todo: allow multiple results to return and set "more_body" appropriately
    return {"type": "http.request",
            "body": bytes(draw(st.text(max_size=10000)), encoding="utf8"),
            "more_body": False}


@st.composite
def http_response_named_tuple(draw):
    return HttpResponse(
        status_code=draw(st.integers()),
        # make the iterable a list for the sake of testing... some
        # iterables can only be consumed once, meaning testing make not
        # behave the same as the code under test and vice versa
        body=draw(
            st.lists(
                st.text(max_size=1000).map(lambda x: bytes(x.lower(),
                                                           encoding="utf8")),
                max_size=40
            )
        ),
        headers=draw(headers())
    )


@st.composite
def http_request_named_tuple(draw):
    return HttpRequest(
        body=draw(st.binary()),
        client=draw(st.from_type(HostPort)) if coinflip() else None,
        extensions=draw(scope_extensions()) if coinflip() else None,
        headers=draw(st.lists(st.tuples(header_string(), header_string()),
                              max_size=60)),
        http_version=gen_http_version(),
        method=gen_http_method(),
        path=draw(st.text(max_size=1000)),
        query_string=draw(query_string()),
        root_path=draw(st.text(max_size=1000)),
        scheme=draw(st.text(min_size=1, max_size=5)),
        scope_orig=draw(asgi_http_scope()),
        server=draw(st.from_type(HostPort)) if coinflip() else None
    )
