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


def ws_incoming_to_datatype(event: ASGIEvent) -> WSIncomingEvent:
    event_type = event['type']
    assert isinstance(event_type, str)
    if event_type == "connect":
        return WSConnect()

    elif event_type == "receive":
        str_content = event.get("text")
        content = str_content if str_content is not None else event['bytes']
        assert isinstance(content, (str, bytes))
        return WSReceive(content)

    elif event_type == "disconnect":
        code = event["code"]
        assert isinstance(code, int)
        return WSDisconnect(code=code)
    else:
        raise ValueError(f"Bad received dict. type was `{event['type']}`")


async def should_close(client_state: WSState,
                       event: WSOutgoingEvent) -> bool:
    if client_state == WSState.CONNECTING:
        if isinstance(event, WSClose):
            return True
        elif isinstance(event, WSAccept):
            return False
        else:
            raise TypeError("Bad type for connecting")

    elif client_state == WSState.CONNECTED:
        if isinstance(event, WSSend):
            return False
        elif isinstance(event, WSClose):
            return True
        else:
            raise TypeError("Bad type for connected")
    else:
        raise Exception("Something is wrong!")


def websocket_endpoint(func: Callable[[WSIncomingEvent], Awaitable[WSOutgoingEvent]]):
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

                client_state = state["client_state"]

                if client_state == WSState.CONNECTING:
                    assert isinstance(event, WSConnect)
                    state['client_state'] = WSState.CONNECTED
                elif client_state == WSState.CONNECTED:
                    if isinstance(event, WSDisconnect):
                        state[client_state] = WSState.DISCONNECTED
                    else:
                        assert isinstance(event, WSReceive)
                        outgoing = await func(event)

                        if should_close(state["client_state"], outgoing):
                            state["client_state"] = WSState.DISCONNECTED

                        await send(ws_outgoing_to_event_dict(outgoing))

                else:
                    raise RuntimeError('Cannot call "receive" once a disconnect '
                                       'message has been received.')

                if state["client_state"] == WSState.DISCONNECTED:
                    break

        return awaitable

    return app
