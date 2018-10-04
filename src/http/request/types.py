from typing import NamedTuple, Optional, Tuple, List


class HostPort(NamedTuple):
    host: str
    port: int


class HttpRequest(NamedTuple):
    body: bytes
    client: Optional[HostPort]
    headers: List[Tuple[bytes, bytes]]
    http_version: str
    method: str
    path: str
    query_string: bytes
    root_path: str
    scheme: str
    server: Optional[HostPort]




