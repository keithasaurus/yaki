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
    TRACE,
)
from yaki.http.types import HttpRequest, HttpResponse


# Deterministic helpers replacing Hypothesis strategies for explicit tests

def gen_http_version() -> str:
    return "1.1"


def gen_http_method() -> str:
    return GET


def asgi_http_scope(path: str = "/") -> dict:
    return {
        "type": "http",
        "headers": [],
        "http_version": gen_http_version(),
        "method": gen_http_method(),
        "path": path,
        "query_string": b"",
        "extensions": {},
        "server": ["127.0.0.1", 8000],
        "client": ["127.0.0.1", 5000],
        "scheme": "http",
        "root_path": "",
    }


def asgi_http_request(body: bytes = b"hello") -> dict:
    return {"type": "http.request", "body": body, "more_body": False}


def http_response_named_tuple(status_code: int = 200, body: bytes = b"ok") -> HttpResponse:
    return HttpResponse(status_code=status_code, headers=[], body=body)


def http_request_named_tuple(method: str = GET, path: str = "/") -> HttpRequest:
    return HttpRequest(
        body=b"",
        client=["127.0.0.1", 5000],
        custom=SimpleNamespace(),
        extensions={},
        headers=[],
        http_version="1.1",
        method=method,
        path=path,
        query_params={},
        root_path="",
        scheme="http",
        scope_orig=asgi_http_scope(path),
        server=["127.0.0.1", 8000],
    )
