from typing import Callable, Optional, Union

RouteMatcher = Callable[[str], Optional[dict[str, str]]]

MatcherOrStr = Union[str, RouteMatcher]
