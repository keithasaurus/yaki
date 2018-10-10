from yaki.http.types import HttpRequest, HttpResponse

DEFAULT_404_RESPONSE = HttpResponse(status_code=404,
                                    body=[b"404: Path Not Found"],
                                    headers=[])


async def http_404_view(request: HttpRequest):
    return DEFAULT_404_RESPONSE
