from typing import Dict, Optional, Callable, Union

RouteMatcher = Callable[[str], Optional[Dict[str, str]]]

MatcherOrStr = Union[str, RouteMatcher]