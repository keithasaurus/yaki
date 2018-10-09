from typing import List
from yaki.http.types import HttpResponse
from yaki.utils.types import AsgiEvent


def http_response_to_expected_parts(response: HttpResponse) -> List[AsgiEvent]:
    expected_body = []

    for body_bytes in response.body:
        expected_body.append({
            'type': 'http.response.body',
            'body': body_bytes,
            'more_body': True,
        })

    if len(expected_body) > 0:
        expected_body[-1]['more_body'] = False

    return [{
        'type': 'http.response.start',
        'status': response.status_code,
        'headers': [list(x) for x in response.headers]}] + expected_body
