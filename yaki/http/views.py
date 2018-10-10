from yaki.http.types import HttpRequest, HttpResponse

DEFAULT_404_RESPONSE = HttpResponse(status_code=404,
                                    body=[b"404: Path Not Found"],
                                    headers=[])

DEFAULT_405_RESPONSE = HttpResponse(status_code=405,
                                    body=[b"405: Method Not Allowed"],
                                    headers=[])


async def http_404_view(request: HttpRequest) -> HttpResponse:
    return DEFAULT_404_RESPONSE


async def http_405_view(request: HttpRequest) -> HttpResponse:
    return DEFAULT_405_RESPONSE
