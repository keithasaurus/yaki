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
    ret = {
        "type": "http",
        "headers": draw(headers()),
        "http_version": gen_http_version(),
        "method": gen_http_method(),
        "path": "/" + draw(st.text()),
        "query_string": draw(query_string()),
    }

    if coinflip():
        ret['client'] = draw(host_and_port())

    if coinflip():
        ret['server'] = draw(host_and_port())

    if coinflip():
        ret["scheme"] = draw(st.text(min_size=1))

    if coinflip():
        ret["root_path"] = draw(st.text())

    if coinflip():
        ret['extensions'] = draw(scope_extensions())

    return ret


@st.composite
def asgi_http_request(draw):
    ret = {"type": "http.request",
           "body": bytes(draw(st.text()), encoding="utf8"),
           "more_body": False}

    # todo: return multiple requests with only the
    # last with more_body=False
    if coinflip():
        ret["more_body"] = False

    return ret


@st.composite
def http_response(draw):
    http_response = draw(st.from_type(HttpResponse))
    # make the iterable a list for the sake of testing... some
    # iterables can only be consumed once, meaning testing make not
    # behave the same as the code under test and vice versa

    return http_response._replace(body=list(http_response.body))


@st.composite
def http_request_named_tuple(draw):
    return HttpRequest(
        body=draw(st.binary()),
        client=draw(st.from_type(HostPort)) if coinflip() else None,
        extensions=draw(scope_extensions()) if coinflip() else None,
        headers=draw(st.lists(st.tuples(header_string(), header_string()))),
        http_version=gen_http_version(),
        method=gen_http_method(),
        path=draw(st.text()),
        query_string=draw(query_string()),
        root_path=draw(st.text()),
        scheme=draw(st.text(min_size=1)),
        scope_orig=draw(asgi_http_scope()),
        server=draw(st.from_type(HostPort)) if coinflip() else None
    )
