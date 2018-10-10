from copy import deepcopy
from typing import List
from yaki.http.types import HttpResponse
from yaki.utils.types import AsgiEvent, AsgiInstance

import asyncio


def http_response_to_expected_parts(response: HttpResponse) -> List[AsgiEvent]:
    expected_body: List[AsgiEvent] = [
        {
            'type': 'http.response.body',
            'body': body_bytes,
            'more_body': True,
        } for body_bytes in response.body
    ]

    if len(expected_body) > 0:
        expected_body[-1]['more_body'] = False

    ret: List[AsgiEvent] = [{
        'type': 'http.response.start',
        'status': response.status_code,
        'headers': [list(x) for x in response.headers]
    }]

    ret.extend(expected_body)

    return ret


def call_http_endpoint(endpoint: AsgiInstance,
                       events: List[AsgiEvent]) -> List[AsgiEvent]:
    """
    given the events to receive, process and return the sent events in a list
    """
    responses = []

    async def sender(event: AsgiEvent) -> None:
        responses.append(event)

    events_iter = deepcopy(events)

    async def receiver() -> AsgiEvent:
        return events_iter.pop(0)

    asyncio.run(endpoint(receiver, sender))

    return responses
