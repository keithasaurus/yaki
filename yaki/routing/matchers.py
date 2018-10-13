from typing import Dict, List, Optional, Pattern
from yaki.routing.types import RouteMatcher

import re

BRACKET_REGEX_STR = '{[^ {]*}'

# intentionally left vaguer than desired for error reporting
BRACKET_REGEX_BROAD = re.compile(BRACKET_REGEX_STR)


def regex_match_to_str_dict(pattern: Pattern, url: str) -> Optional[Dict[str, str]]:
    match = re.match(pattern, url)

    if match is None:
        return None
    else:
        return {
            key: str(val) for key, val in match.groupdict().items()
        }


def regex_route_matcher(pattern: Pattern) -> RouteMatcher:
    if isinstance(pattern, str):
        pattern = re.compile(pattern)

    def inner(url: str) -> Optional[Dict[str, str]]:
        return regex_match_to_str_dict(pattern, url)

    return inner


def to_capturing_bracket_param(arg_name: str) -> str:
    return f'(?P<{arg_name}>.+)'


def assert_valid_params(param_names: List[str]) -> None:
    for name in param_names:
        assert name[1:-1].isidentifier(), (
            f"{name} is an invalid name for a url parameter")

    assert len(param_names) == len(set(param_names)), (
        "duplicate parameter names are not allowed")


def bracket_route_matcher(url_pattern: str) -> RouteMatcher:
    param_names = re.findall(BRACKET_REGEX_BROAD, url_pattern)

    assert_valid_params(param_names)

    # replace the brackets with capturing regexes
    split_strs = re.split(f'({BRACKET_REGEX_STR})', url_pattern)

    processed = [
        (to_capturing_bracket_param(s[1:-1]) if s in set(param_names)
         else re.escape(s))  # need to escape literals
        for s in split_strs
    ]

    processed_str = "".join(processed)

    return regex_route_matcher(re.compile(f'^{processed_str}$'))
