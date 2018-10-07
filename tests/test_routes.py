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

    def test_does_not_allow_duplicate_names(self):
        with self.assertRaises(AssertionError):
            bracket_route_parser("/{name}/{name}")

    def test_param_must_have_valid_name(self):
        for invalid_pattern in [
            "{}",  # no arg_length
            "{.}",  # no period arg name
        ]:
            with self.assertRaises(AssertionError):
                bracket_route_parser(invalid_pattern)
