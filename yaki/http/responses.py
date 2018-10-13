from typing import Callable, Optional
from yaki.http.types import HttpResponse, ResponseTypes
from yaki.types import Headers


def response_types_to_bytes(content: ResponseTypes) -> bytes:
    if isinstance(content, str):
        # for string we assume utf8
        return bytes(content, encoding='utf8')
    elif isinstance(content, bytes):
        return content
    else:
        raise TypeError(f'invalid type. Got {type(content)}')


def default_headers_from_content(content: bytes) -> Headers:
    content_length = str(len(content))
    return [
        (b'content-type', b'text/html; charset=utf-8'),
        (b'content-length', content_length.encode('utf8'))
    ]


def _simple_response(content: ResponseTypes,
                     status_code: int,
                     headers: Optional[Headers]) -> HttpResponse:
    content_bytes = response_types_to_bytes(content)

    return HttpResponse(
        body=content_bytes,
        status_code=status_code,
        headers=(
            headers if headers is not None
            else default_headers_from_content(response_types_to_bytes(content))))


def _status_response(status_code: int) -> Callable:
    def inner(content: ResponseTypes,
              headers: Optional[Headers]=None) -> HttpResponse:
        return _simple_response(content,
                                status_code,
                                headers)

    return inner


def response(content: ResponseTypes,
             status_code: int = 200,
             headers: Optional[Headers] = None) -> HttpResponse:
    return _simple_response(content,
                            status_code,
                            headers)


response_200 = _status_response(200)
response_201 = _status_response(201)
response_400 = _status_response(400)
response_401 = _status_response(401)
response_403 = _status_response(403)
response_404 = _status_response(404)
response_405 = _status_response(405)
response_500 = _status_response(500)
response_502 = _status_response(502)
response_503 = _status_response(503)
response_504 = _status_response(504)
