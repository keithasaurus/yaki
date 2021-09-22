from yaki.apps import yaki
from yaki.http.config import http_app
from yaki.http.responses import response_200
from yaki.http.types import HttpRequest, HttpResponse


async def view(request: HttpRequest) -> HttpResponse:
    return response_200("Hello, world!", [])


app = yaki(http_app(routes=[("/", view)], middleware=[]))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
