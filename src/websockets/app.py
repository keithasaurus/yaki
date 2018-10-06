from src.types import ASGIEvent, ASGIInstance, ASGIValue, Receiver, Scope, Sender
from src.websockets.types import (
    WSAccept,
    WSClose,
    WSConnect,
    WSDisconnect,
    WSIncomingEvent,
    WSOutgoingEvent,
    WSReceive,
    WSSend
)
from typing import Awaitable, Callable, Dict, Union


async def some_websocket_endpoint(event: WSIncomingEvent) -> WSOutgoingEvent:
    print("got event:", event)

    return WSSend("Some string")


def event_to_dict(event_type: str,
                  event_details: Dict[str, ASGIValue]) -> ASGIEvent:
    event_details["type"] = f"websocket.{event_type}"
    return event_details


def _ws_send_to_asgi_dict(event: WSSend) -> ASGIEvent:
    content_key = "text" if isinstance(event.content, str) else "bytes"
    return event_to_dict("send", {content_key: event.content})


def ws_outgoing_to_event_dict(event: WSOutgoingEvent) -> ASGIEvent:
    if isinstance(event, WSAccept):
        return event_to_dict("accept", {"subprotocol": event.subprotocol})
    elif isinstance(event, WSSend):
        content_key = "text" if isinstance(event.content, str) else "bytes"
        return event_to_dict("send", {content_key: event.content})
    elif isinstance(event, WSClose):
        return event_to_dict("close", {"code": event.code})
    elif isinstance(event, WSDisconnect):
        return event_to_dict("disconnect", {"code": event.code})

    raise TypeError(f"type `{type(event)}` is not a valid WSOutgoingEvent")


def _event_to_receive(event: ASGIEvent) -> WSReceive:
    str_content = event.get("text")
    content = str_content if str_content is not None else event['bytes']
    assert isinstance(content, (str, bytes))
    return WSReceive(content)


def _event_to_disconnect(event: ASGIEvent) -> WSDisconnect:
    code = event["code"]
    assert isinstance(code, int)
    return WSDisconnect(code=code)


def ws_incoming_to_datatype(event: ASGIEvent) -> WSIncomingEvent:
    convert_funcs: Dict[str, Callable[[ASGIEvent], WSIncomingEvent]] = {
        "connect": lambda x: WSConnect(),
        "receive": _event_to_receive,
        "disconnect": _event_to_disconnect
    }

    event_type = event['type']
    assert isinstance(event_type, str)
    event_type = event_type.replace('websocket.', '')

    return convert_funcs[event_type](event)


def websocket_endpoint(
        # todo: are these the right output types?
        connect_handler: Callable[[Scope, WSConnect], Awaitable[Union[WSAccept,
                                                                      WSDisconnect,
                                                                      WSClose]]],
        receive_handler: Callable[[Scope, WSReceive], Awaitable[Union[WSSend,
                                                                      WSDisconnect,
                                                                      WSClose,
                                                                      None]]],
        client_disconnect_handler: Callable[[Scope, WSDisconnect], Awaitable[None]]
) -> Callable[[Scope], ASGIInstance]:
    def app(scope: Scope) -> ASGIInstance:
        state: Dict[str, bool] = {
            "client_disconnected": False,
            "app_disconnected": False
        }

        def app_disconnected() -> bool:
            return state['app_disconnected']

        def client_disconnected() -> bool:
            return state['client_disconnected']

        async def awaitable(receive: Receiver,
                            send: Sender) -> None:
            connect_event = ws_incoming_to_datatype(await receive())
            assert isinstance(connect_event, WSConnect)

            connect_response = await connect_handler(scope, connect_event)

            if not isinstance(connect_response, WSAccept):
                state["app_disconnected"] = True

            await send(ws_outgoing_to_event_dict(connect_response))

            if app_disconnected():
                return None
            else:
                while not client_disconnected() and not app_disconnected():
                    incoming_event: WSIncomingEvent = ws_incoming_to_datatype(
                        await receive())

                    if isinstance(incoming_event, WSDisconnect):
                        state['client_disconnected'] = True
                        await client_disconnect_handler(scope, incoming_event)
                        return None

                    elif isinstance(incoming_event, WSReceive):
                        outgoing = await receive_handler(scope, incoming_event)

                        if isinstance(outgoing, (WSClose, WSDisconnect)):
                            state['app_disconnected'] = True

                        if outgoing is not None:
                            await send(ws_outgoing_to_event_dict(outgoing))

                        return None

        return awaitable

    return app
