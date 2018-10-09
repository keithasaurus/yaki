from typing import Callable, Dict, Optional, Pattern

import re

RouteMatcher = Callable[[str], Optional[Dict[str, str]]]


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
    def inner(url: str):
        return regex_match_to_str_dict(pattern, url)

    return inner


def to_capturing_bracket_param(arg_name: str) -> str:
    return f'(?P<{arg_name}>.+)'


def bracket_route_matcher(url_pattern: str) -> RouteMatcher:
    param_names = re.findall(BRACKET_REGEX_BROAD, url_pattern)

    param_names_set = set(param_names)

    for name in param_names:
        assert name[1:-1].isidentifier(), (
            f"{name} is an invalid name for a url parameter")

    assert len(param_names) == len(param_names_set), (
        "duplicate parameter names are not allowed")

    # replace the brackets with capturing regexes
    split_strs = re.split(f'({BRACKET_REGEX_STR})', url_pattern)

    processed = [
        (to_capturing_bracket_param(s[1:-1]) if s in param_names_set
         else re.escape(s))  # need to escape literals
        for s in split_strs
    ]

    processed_str = "".join(processed)

    return regex_route_matcher(re.compile(f'^{processed_str}$'))
