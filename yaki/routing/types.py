from typing import Callable, Dict, Optional, Union

RouteMatcher = Callable[[str], Optional[Dict[str, str]]]

MatcherOrStr = Union[str, RouteMatcher]
