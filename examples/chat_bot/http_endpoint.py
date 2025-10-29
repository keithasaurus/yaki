from jinja2 import Template
from os import path
from yaki.http.responses import response
from yaki.http.types import HttpRequest, HttpResponse


async def serve_html_page(request: HttpRequest) -> HttpResponse:
    with open(path.join(path.dirname(__file__), "chat_page.html")) as f:
        template = Template(f.read())

    # Handle optional server info gracefully for examples
    host = "127.0.0.1"
    port = 5000
    if request.server is not None:
        host = request.server.host
        port = request.server.port

    return response(
        template.render({"ws_url": f"ws://{host}:{port}/chat"})
    )
