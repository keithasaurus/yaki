from typing import Any, Dict, List, NamedTuple, Optional, Tuple
from yaki.utils.types import HostPort, Scope


class HttpRequest(NamedTuple):
    body: bytes
    client: Optional[HostPort]
    extensions: Optional[Dict[str, Dict[Any, Any]]]
    headers: List[Tuple[bytes, bytes]]
    http_version: str
    method: str
    path: str
    query_string: bytes
    root_path: str
    scheme: str
    scope_orig: Scope
    server: Optional[HostPort]
