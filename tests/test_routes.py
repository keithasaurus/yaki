from unittest import TestCase
from yaki.routing.matchers import bracket_route_matcher, regex_match_to_str_dict

import re


class RegexMatchTest(TestCase):
    def test_returns_dict_of_parameterized_strings(self):
        result = regex_match_to_str_dict(
            re.compile(
                "a(?P<b>.+)c",
            ),
            "a-stuff!-c",
        )

        self.assertEqual(result, {"b": "-stuff!-"})

    def test_no_match_returns_none(self):
        result = regex_match_to_str_dict(re.compile("abc"), "")

        self.assertIsNone(result)


class BracketRouteMatcherTests(TestCase):
    def test_works_without_brackets(self):
        test_str = "/something"
        matcher = bracket_route_matcher(test_str)

        self.assertEqual({}, matcher(test_str))

    def test_works_with_brackets(self):
        url_pattern = "/some/{name}/and/{city}/and{_state_thing}"
        matcher = bracket_route_matcher(url_pattern)

        self.assertEqual(
            matcher("/some/keith/and/jackson/andMI1.chag---an"),
            {"name": "keith", "city": "jackson", "_state_thing": "MI1.chag---an"},
        )

    def test_does_not_allow_duplicate_names(self):
        with self.assertRaises(AssertionError):
            bracket_route_matcher("/{name}/{name}")

    def test_param_must_have_valid_name(self):
        for invalid_pattern in [
            "{}",  # no arg_length
            "{.}",  # no period arg name
        ]:
            with self.assertRaises(AssertionError):
                bracket_route_matcher(invalid_pattern)

    def test_end_must_match(self):
        matcher = bracket_route_matcher("/")

        self.assertIsInstance(matcher("/"), dict)
        self.assertIsNone(matcher("/a"))
