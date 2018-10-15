from jinja2 import Template
from os import path
from yaki.http.responses import response
from yaki.http.types import HttpRequest, HttpResponse


async def serve_html_page(request: HttpRequest) -> HttpResponse:
    with open(path.join(path.dirname(__file__), "chat_page.html")) as f:
        template = Template(f.read())

    return response(
        template.render({
            "ws_url": f"ws://{request.server.host}:{request.server.port}/chat"
        }))
