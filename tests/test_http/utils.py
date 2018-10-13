from copy import deepcopy
from typing import List
from yaki.http.types import HttpResponse
from yaki.types import AsgiEvent, AsgiInstance

import asyncio


def http_response_to_expected_parts(response: HttpResponse) -> List[AsgiEvent]:
    return [
        {
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': [list(x) for x in response.headers]
        },
        {
            'type': 'http.response.body',
            'body': response.body,
            'more_body': False,
        }
    ]


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
