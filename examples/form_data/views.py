from os import path
from typing import Any

from jinja2 import Template
from multipart.multipart import parse_options_header, FormParser

from yaki.http.methods import GET
from yaki.http.responses import response_200
from yaki.http.types import HttpRequest, HttpResponse


def parse_form(request: HttpRequest) -> Any:
    breakpoint()
    content_type_header = request.headers.get("Content-Type")
    content_type, options = parse_options_header(content_type_header)
    if content_type == b"multipart/form-data":
        multipart_parser = MultiPartParser(request.headers, request.body)
        self._form = multipart_parser.parse()
    elif content_type == b"application/x-www-form-urlencoded":
        form_parser = FormParser(headers, self.stream())
        self._form = await form_parser.parse()
    else:
        return = {}


def get_form_template() -> Template:
    with open(path.join(path.dirname(__file__), "form.html")) as f:
        return Template(f.read())


async def form_view(request: HttpRequest) -> HttpResponse:
    if request.method == GET:
        return response_200(get_form_template().render())
    else:
        parse_form(request)
