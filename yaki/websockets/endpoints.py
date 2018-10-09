from typing import Awaitable, Callable, Dict
from yaki.utils.types import (
    AsgiEvent,
    AsgiInstance,
    AsgiValue,
    list_headers_to_tuples,
    list_hostport_to_datatype,
    Receiver,
    Scope,
    Sender
)
from yaki.websockets.types import (
    WSAccept,
    WSClose,
    WSConnect,
    WSDisconnect,
    WSIncomingEvent,
    WSOutgoingEvent,
    WSReceive,
    WSScope,
    WSSend,
    WSViewFunc
)


def event_to_dict(event_type: str,
                  event_details: Dict[str, AsgiValue]) -> AsgiEvent:
    event_details["type"] = f"websocket.{event_type}"
    return event_details


def _ws_send_to_asgi_dict(event: WSSend) -> AsgiEvent:
    content_key = "text" if isinstance(event.content, str) else "bytes"
    return event_to_dict("send", {content_key: event.content})


def ws_disconnect_to_dict(event: WSDisconnect) -> AsgiEvent:
    return event_to_dict("disconnect", {"code": event.code})


def ws_close_to_dict(event: WSClose) -> AsgiEvent:
    return event_to_dict("close", {"code": event.code})


def ws_outgoing_to_event_dict(event: WSOutgoingEvent) -> AsgiEvent:
    if isinstance(event, WSAccept):
        return event_to_dict("accept", {"subprotocol": event.subprotocol})
    elif isinstance(event, WSSend):
        content_key = "text" if isinstance(event.content, str) else "bytes"
        return event_to_dict("send", {content_key: event.content})
    elif isinstance(event, WSClose):
        return ws_close_to_dict(event)
    elif isinstance(event, WSDisconnect):
        return ws_disconnect_to_dict(event)

    raise TypeError(f"type `{type(event)}` is not a valid WSOutgoingEvent")


def _event_to_receive(event: AsgiEvent) -> WSReceive:
    str_content = event.get("text")
    content = str_content if str_content is not None else event['bytes']
    assert isinstance(content, (str, bytes))
    return WSReceive(content)


def _event_to_disconnect(event: AsgiEvent) -> WSDisconnect:
    code = event["code"]
    assert isinstance(code, int)
    return WSDisconnect(code=code)


def _event_to_close(event: AsgiEvent) -> WSClose:
    code = event["code"]
    assert isinstance(code, int)
    return WSClose(code=code)


def ws_incoming_to_datatype(event: AsgiEvent) -> WSIncomingEvent:
    convert_funcs: Dict[str, Callable[[AsgiEvent], WSIncomingEvent]] = {
        "connect": lambda x: WSConnect(),
        "receive": _event_to_receive,
        "disconnect": _event_to_disconnect,
        "close": _event_to_close
    }

    event_type = event['type']
    assert isinstance(event_type, str)
    event_type = event_type.replace('websocket.', '')

    return convert_funcs[event_type](event)


def asgi_ws_scope_to_datatype(scope: AsgiEvent) -> WSScope:
    path = scope['path']
    query_string = scope.get('query_string', b"")
    scheme = scope.get('scheme')
    root_path = scope.get('root_path')
    subprotocols = scope.get('subprotocols')
    extensions = scope.get('extensions')

    assert isinstance(path, str)
    assert isinstance(query_string, bytes)
    assert isinstance(scheme, str) or scheme is None
    assert isinstance(root_path, str) or root_path is None

    if subprotocols is not None:
        assert isinstance(subprotocols, list)
        for s in subprotocols:
            assert isinstance(s, str)

    if extensions is not None:
        assert isinstance(extensions, dict)

        for k, v in extensions.items():
            assert isinstance(k, str)
            assert isinstance(v, dict)

    return WSScope(
        client=list_hostport_to_datatype(scope.get("client")),
        headers=list_headers_to_tuples(scope['headers']),
        orig=scope,
        path=path,
        query_string=query_string,
        root_path=root_path,
        scheme=scheme,
        server=list_hostport_to_datatype(scope.get("client")),
        subprotocols=subprotocols
    )


def ws_endpoint(func: WSViewFunc) -> Callable[[Scope], AsgiInstance]:
    def app(scope: Scope) -> AsgiInstance:
        async def awaitable(receiver: Receiver,
                            send: Sender) -> None:
            async def wrapped_receiver() -> WSIncomingEvent:
                return ws_incoming_to_datatype(await receiver())

            async def wrapped_send(event: WSOutgoingEvent) -> None:
                await send(ws_outgoing_to_event_dict(event))

            await func(asgi_ws_scope_to_datatype(scope),
                       wrapped_receiver,
                       wrapped_send)

        return awaitable

    return app
