from types import MappingProxyType, SimpleNamespace
from typing import Callable, Union
from urllib.parse import parse_qs
from yaki.http.types import (
    HttpDisconnect,
    HttpRequest,
    HttpRequestResponseView,
    HttpResponse
)
from yaki.types import (
    AsgiInstance,
    list_headers_to_tuples,
    list_hostport_to_datatype,
    Receiver,
    Scope,
    Sender
)


async def respond(response: HttpResponse,
                  send: Sender) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": response.status_code,
            "headers": [list(x) for x in response.headers]
        }
    )

    await send({"type": "http.response.body",
                "body": response.body,
                "more_body": False})


def asgi_to_http_request(content: bytes, scope: Scope) -> HttpRequest:
    http_version, method, path, query_string = [
        scope.get(k) for k
        in ['http_version',
            'method',
            'path',
            'query_string']
    ]
    assert isinstance(path, str)
    assert isinstance(http_version, str)
    assert isinstance(method, str)
    assert isinstance(query_string, bytes)

    scheme = scope.get('scheme', 'http')
    root_path = scope.get('root_path', '')

    assert isinstance(scheme, str)
    assert isinstance(root_path, str)

    extensions = scope.get('extensions')
    if extensions is not None:
        assert isinstance(extensions, dict)

        for k, v in extensions.items():
            assert isinstance(k, str)
            assert isinstance(v, dict)

    return HttpRequest(
        body=content,
        client=list_hostport_to_datatype(scope.get("client")),
        custom=SimpleNamespace(),
        extensions=extensions,
        headers=list_headers_to_tuples(scope['headers']),
        http_version=http_version,
        method=method.upper(),  # just in case
        path=path,
        query_params=parse_qs(query_string.decode("utf-8")),
        root_path=root_path,
        scheme=scheme,
        scope_orig=MappingProxyType(scope),
        server=list_hostport_to_datatype(scope.get("server")),
    )


async def wait_for_request(scope: Scope,
                           receive: Receiver) -> Union[HttpRequest, HttpDisconnect]:
    content = b""
    while True:
        event = await receive()

        event_type = event["type"]
        if event_type == "http.request":
            this_content = event.get("body", b"")
            assert isinstance(this_content, bytes)
            content += this_content
            if not event.get("more_body", False):
                return asgi_to_http_request(content, scope)
        elif event_type == "http.disconnect":
            return HttpDisconnect()
        else:
            raise ValueError(f"got unexpected key for type: `{event}`")


def http_endpoint(func: HttpRequestResponseView) -> Callable:
    def app(scope: Scope) -> AsgiInstance:
        async def awaitable(receive: Receiver,
                            send: Sender) -> None:

            request_result = await wait_for_request(scope, receive)

            if isinstance(request_result, HttpRequest):
                response = await func(request_result)
                await respond(response, send)
            else:
                # todo: handle
                raise Exception("client disconnected!")

        return awaitable

    return app
