from hypothesis import strategies as st
from tests.utils.strategies import (
    coinflip,
    headers,
    host_and_port,
    query_string,
    scope_extensions
)

import random

from yaki.http.types import HttpResponse


@st.composite
def asgi_http_scope(draw):
    ret = {
        "type": "http",
        "headers": draw(headers()),
        "http_version": random.choice(["1.0", "1.1", "1.2"]),
        "method": random.choice(["CONNECT",
                                 "DELETE",
                                 "GET",
                                 "HEAD",
                                 "OPTIONS",
                                 "PATCH",
                                 "POST",
                                 "PUT",
                                 "TRACE"]),
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
