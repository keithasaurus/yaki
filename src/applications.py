import asyncio
from typing import Callable, Awaitable

from src.http.response.types import HttpResponse, HttpRequest
from src.types import ASGIInstance, Scope, Sender, Receiver


async def some_http_view(scope: Scope,
                         request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        status_code=200,
        headers=[(b"some-header", b"hooray")],
        body=[
            b"hello world", b"world stuff"
        ]
    )


def kn() -> ASGIInstance:
    return request_response(some_http_view)



def websocket_session(func):
    """
    Takes a coroutine `func(session, **kwargs)`, and returns an ASGI application.
    """

    def app(scope: Scope) -> ASGIInstance:
        async def awaitable(receive: Receiver,
                            send: Sender) -> None:
            session = WebSocket(scope, receive=receive, send=send)
            kwargs = scope.get("kwargs", {})
            await func(session, **kwargs)

        return awaitable

    return app