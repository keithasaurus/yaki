from jinja2 import Template
from os import path
from yaki.http.responses import response_200
from yaki.http.types import HttpRequest, HttpResponse


async def serve_html_page(request: HttpRequest) -> HttpResponse:
    with open(path.join(path.dirname(__file__), "chat.html")) as f:
        template = Template(f.read())

    return response_200(
        template.render({
            "ws_url": f"ws://{request.server.host}:{request.server.port}/chat",
            "page_title": "Chat Bot"
        }))
