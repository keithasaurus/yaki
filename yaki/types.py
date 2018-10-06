from typing import Any, Awaitable, Callable, Dict, List, Mapping, Union

# Note the Anys here should be recursive ASGIValue, but are not because
# of mypy's current limitations
ASGIValue = Union[bytes, str, int, float, List[Any], Dict[str, Any], bool, None]

ASGIEvent = Dict[str, ASGIValue]

Scope = Mapping[str, ASGIValue]

Receiver = Callable[[], Awaitable[ASGIEvent]]
Sender = Callable[[ASGIEvent], Awaitable[None]]

ASGIInstance = Callable[[Receiver, Sender], Awaitable[None]]

ASGIApp = Callable[[Scope], ASGIInstance]
