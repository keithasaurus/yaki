from yaki import HttpResponse, HttpRequest


async def http_404_view(request: HttpRequest):
    return HttpResponse(status_code=404,
                        body=[b"404: Path Not Found"],
                        headers=[])
