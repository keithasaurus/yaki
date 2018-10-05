import asyncio
from typing import Callable, Awaitable, Union, Optional, Tuple, List

from src.http.request.types import HttpRequest, HostPort
from src.http.response.types import HttpResponse, HttpDisconnect
from src.types import Sender, Scope, ASGIInstance, Receiver, ASGIValue


async def respond(response: HttpResponse, send: Sender) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": response.status_code,
            "headers": response.headers
        }
    )

    prev_item = None

    for body_item in response.body:
        # send previous because we need to know if there's a future event to send
        if prev_item is not None:
            await send({"type": "http.response.body",
                        "body": prev_item,
                        "more_body": True})

        prev_item = body_item

    await send({"type": "http.response.body",
                "body": prev_item,
                "more_body": False})


HttpViewFunc = Union[
    Callable[[HttpRequest], Awaitable[HttpResponse]],
    Callable[[HttpRequest], HttpResponse],
]


def _get_hostport(val: Optional[ASGIValue]) -> Optional[HostPort]:
    if isinstance(val, list) and len(val) == 2:
        host, port = val
        if isinstance(host, str) and isinstance(port, int):
            return HostPort(host=host, port=port)
    return None


def _get_tuple_headers(val: ASGIValue) -> List[Tuple[bytes, bytes]]:
    headers = []

    if isinstance(val, list):
        for header_pair in val:
            if (isinstance(header_pair, list)
                    and len(header_pair) == 2):
                k, v = header_pair
                if isinstance(k, bytes) and isinstance(v, bytes):
                    headers.append((k, v))

    return headers


def asgi_to_http_request(content: bytes, scope: Scope) -> HttpRequest:
    http_version, method, path, query_string = [
        scope.get(k) for k
        in ['http_version',
            'method',
            'path',
            'query_string', ]
    ]
    assert isinstance(path, str)
    assert isinstance(http_version, str)
    assert isinstance(method, str)
    assert isinstance(query_string, bytes)

    scheme = scope.get('scheme', 'http')
    root_path = scope.get('root_path', '')

    assert isinstance(scheme, str)
    assert isinstance(root_path, str)

    return HttpRequest(
        body=content,
        client=_get_hostport(scope.get("client")),
        headers=_get_tuple_headers(scope['headers']),
        http_version=http_version,
        method=method,
        path=path,
        query_string=query_string,
        root_path=root_path,
        scheme=scheme,
        server=_get_hostport(scope.get("server"))
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


def request_response(func: HttpViewFunc):
    is_coroutine = asyncio.iscoroutinefunction(func)

    def app(scope: Scope) -> ASGIInstance:
        async def awaitable(receive: Receiver,
                            send: Sender) -> None:

            request_result = await wait_for_request(scope, receive)

            if isinstance(request_result, HttpRequest):
                if is_coroutine:
                    # ignoring because cannot signify to mypy that this is safe
                    response = await func(request_result)  # type: ignore
                else:
                    response = func(request_result)
                await respond(response, send)
            else:
                # todo: handle
                raise Exception("client disconnected!")

        return awaitable

    return app
