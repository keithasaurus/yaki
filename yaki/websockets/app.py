from typing import Awaitable, Callable, Dict
from yaki.types import AsgiEvent, AsgiInstance, AsgiValue, Receiver, Scope, Sender
from yaki.websockets.types import (
    WSAccept,
    WSClose,
    WSConnect,
    WSDisconnect,
    WSIncomingEvent,
    WSOutgoingEvent,
    WSReceive,
    WSSend
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


TypedReceiver = Callable[[], Awaitable[WSIncomingEvent]]

TypedSender = Callable[[WSOutgoingEvent], Awaitable[None]]


def ws_app(
        func: Callable[[Scope, TypedReceiver, TypedSender], Awaitable[None]]
) -> Callable[[Scope], AsgiInstance]:
    def app(scope: Scope) -> AsgiInstance:
        async def awaitable(receiver: Receiver,
                            send: Sender) -> None:
            async def wrapped_receiver() -> WSIncomingEvent:
                return ws_incoming_to_datatype(await receiver())

            async def wrapped_send(event: WSOutgoingEvent) -> None:
                await send(ws_outgoing_to_event_dict(event))

            await func(scope, wrapped_receiver, wrapped_send)

        return awaitable

    return app
