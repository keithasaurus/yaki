from hypothesis import strategies as st
from tests.utils.strategies import (
    header_string,
    headers,
    host_and_port,
    query_string,
    scope_extensions
)
from types import SimpleNamespace
from yaki.http.methods import (
    CONNECT,
    DELETE,
    GET,
    HEAD,
    OPTIONS,
    PATCH,
    POST,
    PUT,
    TRACE
)
from yaki.http.types import HttpRequest, HttpResponse
from yaki.types import HostPort


@st.composite
def gen_http_version(draw):
    return draw(st.sampled_from(["1.0", "1.1", "1.2"]))


@st.composite
def gen_http_method(draw):
    return draw(st.sampled_from([CONNECT,
                                 DELETE,
                                 GET,
                                 HEAD,
                                 OPTIONS,
                                 PATCH,
                                 POST,
                                 PUT,
                                 TRACE]))


@st.composite
def asgi_http_scope(draw):
    # some of these keys are optional but can't reason about
    # how hypothesis is handling at the moment
    return {
        "type": "http",
        "headers": draw(headers()),
        "http_version": draw(gen_http_version()),
        "method": draw(gen_http_method()),
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
            "body": bytes(draw(st.text(max_size=1000)), encoding="utf8"),
            "more_body": False}


@st.composite
def http_response_named_tuple(draw):
    return HttpResponse(
        status_code=draw(st.integers()),
        # make the iterable a list for the sake of testing... some
        # iterables can only be consumed once, meaning testing make not
        # behave the same as the code under test and vice versa
        body=draw(st.text(max_size=100).map(lambda x: x.encode("utf8"))),
        headers=draw(headers())
    )


@st.composite
def http_request_named_tuple(draw):
    return HttpRequest(
        body=draw(st.binary(max_size=50)),
        client=draw(st.one_of(st.from_type(HostPort), st.none())),
        custom=SimpleNamespace(),
        extensions=draw(st.one_of(scope_extensions(), st.none())),
        headers=draw(st.lists(st.tuples(header_string(), header_string()),
                              max_size=10)),
        http_version=draw(gen_http_version()),
        method=draw(gen_http_method()),
        path=draw(st.text(max_size=200)),
        query_string=draw(query_string()),
        root_path=draw(st.text(max_size=200)),
        scheme=draw(st.text(min_size=1, max_size=5)),
        scope_orig=draw(asgi_http_scope()),
        server=draw(st.one_of(st.from_type(HostPort), st.none())))
