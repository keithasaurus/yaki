from src.http.app import request_response
from src.http.request.types import HttpRequest
from src.http.response.types import HttpResponse
from src.types import ASGIInstance


async def some_http_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        status_code=200,
        headers=[(b"some-header", b"hooray")],
        body=[
            b"hello world", b"world stuff"
        ]
    )


def kn() -> ASGIInstance:
    return request_response(some_http_view)
