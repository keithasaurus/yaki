from typing import Callable, Awaitable, Dict, Any

from src.types import ASGIEvent, Scope, ASGIInstance, Receiver, Sender, ASGIValue
from src.websockets.types import WSDisconnect, WSClose, WSSend, WSState, \
    WSOutgoingEvent, WSAccept, WSIncomingEvent, WSConnect, WSReceive


async def some_websocket_endpoint(event: WSIncomingEvent) -> WSOutgoingEvent:
    print("got event:", event)

    return WSSend("Some string")


def event_to_dict(event_type: str,
                  event_details: Dict[str, ASGIValue]) -> ASGIEvent:
    event_details["type"] = f"websocket.{event_type}"
    return event_details


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


def get_incoming_new_client_state(
        client_state: WSState,
        event: WSIncomingEvent
) -> WSState:
    if client_state == WSState.CONNECTING:
        assert isinstance(event, WSConnect)
        return WSState.CONNECTED
    elif client_state == WSState.CONNECTED:
        if isinstance(event, WSDisconnect):
            return WSState.DISCONNECTED
        else:
            assert isinstance(event, WSReceive)
            return WSState.CONNECTED
    else:
        raise RuntimeError('Cannot call "receive" once a disconnect '
                           'message has been received.')


def get_outgoing_new_client_state(
        client_state: WSState,
        event: WSOutgoingEvent) -> WSState:
    if client_state == WSState.CONNECTING:
        if isinstance(event, WSClose):
            return WSState.DISCONNECTED
        elif isinstance(event, WSAccept):
            return WSState.CONNECTING
        else:
            raise TypeError("Bad type for connecting")

    elif client_state == WSState.CONNECTED:
        if isinstance(event, WSSend):
            return WSState.CONNECTED
        elif isinstance(event, WSClose):
            return WSState.DISCONNECTED
        else:
            raise TypeError("Bad type for connected")
    else:
        raise Exception("Something is wrong!")


def websocket_endpoint(
        func: Callable[[WSIncomingEvent], Awaitable[WSOutgoingEvent]]):
    def app(scope: Scope) -> ASGIInstance:
        state: Dict[str, Any] = {
            "client_state": WSState.CONNECTING
        }

        async def awaitable(receive: Receiver,
                            send: Sender) -> None:

            # todo: handle subprotocol
            await send(ws_outgoing_to_event_dict(WSAccept(None)))

            while True:
                event_dict: ASGIEvent = await receive()

                event: WSIncomingEvent = ws_incoming_to_datatype(event_dict)

                state["client_state"] = get_incoming_new_client_state(
                    state["client_state"],
                    event)

                if isinstance(event, WSReceive):
                    outgoing = await func(event)

                    state["client_state"] = get_outgoing_new_client_state(
                        state["client_state"], outgoing)

                    await send(ws_outgoing_to_event_dict(outgoing))

                if state["client_state"] == WSState.DISCONNECTED:
                    break

        return awaitable

    return app
