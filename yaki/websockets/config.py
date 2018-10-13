from typing import Iterable

from yaki.routing.matchers import bracket_route_matcher
from yaki.websockets.types import WSProtoRoute, WSApp


def ws_app(routes: Iterable[WSProtoRoute]) -> WSApp:
    return WSApp(
        tuple(
            (bracket_route_matcher(matcher), view)
            if isinstance(matcher, str)
            else (matcher, view) for matcher, view in routes))
