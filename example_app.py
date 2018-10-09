from yaki.apps import HttpConfig, WSConfig, yaki_app
from yaki.http.middleware import logging_middleware, timing_middleware
from yaki.http.request.types import HttpRequest
from yaki.http.response.types import HttpResponse
from yaki.routes import bracket_route_matcher

import uvicorn


async def root(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        status_code=200,
        body=[b"hello world"],
        headers=[]
    )

app = yaki_app(
    HttpConfig(
        routes=(
            (bracket_route_matcher("/"), root),
        ),
        middleware=(logging_middleware,
                    timing_middleware)
    ),
    WSConfig(routes=[])
)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
