import asyncio
from typing import Callable, Awaitable, Union

from src.http.response.types import HttpResponse, HttpRequest
from src.types import Sender, Scope, ASGIInstance, Receiver


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


def request_response(func: HttpViewFunc):
    is_coroutine = asyncio.iscoroutinefunction(func)

    def app(scope: Scope) -> ASGIInstance:
        async def awaitable(receive: Receiver,
                            send: Sender) -> None:
            request = await receive()

            if is_coroutine:
                # ignoring because cannot signify to mypy that this is safe
                response = await func(request)  # type: ignore
            else:
                response = func(request)
            await respond(response, send)

        return awaitable

    return app
