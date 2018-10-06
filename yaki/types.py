from typing import Any, Awaitable, Callable, Dict, List, Mapping, Union

# Note the Anys here should be recursive AsgiValue, but are not because
# of mypy's current limitations
AsgiValue = Union[bytes, str, int, float, List[Any], Dict[str, Any], bool, None]

AsgiEvent = Dict[str, AsgiValue]

Scope = Mapping[str, AsgiValue]

Receiver = Callable[[], Awaitable[AsgiEvent]]
Sender = Callable[[AsgiEvent], Awaitable[None]]


AsgiInstance = Callable[[Receiver, Sender], Awaitable[None]]
ScopeAsgiInstance = Callable[[Scope], AsgiInstance]

AsgiApp = Callable[[Scope], AsgiInstance]
