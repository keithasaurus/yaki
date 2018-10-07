from unittest import TestCase
from yaki.routes import bracket_route_parser, regex_match_to_str_dict

import re


class RegexMatchTest(TestCase):
    def test_returns_dict_of_parameterized_strings(self):
        result = regex_match_to_str_dict(
            re.compile("a(?P<b>.+)c", ),
            "a-stuff!-c"
        )

        self.assertEqual(
            result,
            {'b': '-stuff!-'}
        )

    def test_no_match_returns_none(self):
        result = regex_match_to_str_dict(
            re.compile("abc"),
            ""
        )

        self.assertIsNone(result)


class BracketRouteParserTests(TestCase):
    def test_works_without_brackets(self):
        test_str = "/something"
        parser = bracket_route_parser(test_str)

        self.assertEqual({}, parser(test_str))

    def test_works_with_brackets(self):
        url_pattern = "/some/{name}/and/{city}/and{_state_thing}"
        parser = bracket_route_parser(url_pattern)

        self.assertEqual(
            parser("/some/keith/and/jackson/andMI1.chag---an"),
            {"name": "keith",
             "city": "jackson",
             "_state_thing": "MI1.chag---an"})
