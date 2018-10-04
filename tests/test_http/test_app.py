import asyncio
from unittest import TestCase

from src.http.app import respond
from src.http.response.types import HttpResponse
from src.types import ASGIEvent


class RespondTests(TestCase):
    def test_send_gets_multiple_events(self):
        result_list = []

        response = HttpResponse(status_code=200,
                                headers=[(b"header1", b"stuff"),
                                         (b"no2", b"other")],
                                body=[b"something"])

        async def sender(event: ASGIEvent) -> None:
            await asyncio.sleep(0)
            result_list.append(event)

        asyncio.run(respond(response, sender))

        self.assertEqual(result_list,
                         [{'headers': [(b'header1', b'stuff'), (b'no2', b'other')],
                           'status': 200,
                           'type': 'http.response.start'},
                          {'body': b'something',
                           'more_body': False,
                           'type': 'http.response.body'}])
