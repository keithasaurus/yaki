from hypothesis import given, settings
from hypothesis import strategies as st
from unittest import TestCase
from yaki.http import responses
from yaki.http.responses import (
    default_headers_from_content,
    response,
    response_types_to_bytes,
)
from yaki.http.types import HttpResponse


class ResponseTests(TestCase):
    @given(st.text(max_size=100))
    @settings(max_examples=5)
    def test_returns_200_with_default_headers_by_default(self, test_content):
        self.assertEqual(
            HttpResponse(
                body=test_content.encode("utf8"),
                status_code=200,
                headers=default_headers_from_content(
                    response_types_to_bytes(test_content)
                ),
            ),
            response(test_content),
        )

    @given(st.text(max_size=100))
    @settings(max_examples=5)
    def test_convenience_status_code_responders_have_correct_status(self, test_content):
        for num in [200, 201, 400, 401, 403, 404, 405, 500, 502, 503, 504]:
            func = getattr(responses, f"response_{num}")

            result = func(test_content, [])

            self.assertEqual(
                result,
                HttpResponse(
                    body=test_content.encode("utf8"),
                    status_code=num,
                    headers=default_headers_from_content(
                        response_types_to_bytes(test_content)
                    ),
                ),
            )
