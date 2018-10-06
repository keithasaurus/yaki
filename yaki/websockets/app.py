from functools import partial
from typing import Awaitable, Callable, Dict, Union
from yaki.types import (
    AsgiEvent,
    AsgiInstance,
    AsgiValue,
    Receiver,
    Scope,
    ScopeAsgiInstance,
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
    WSReceiveOutput,
    WSSend
)


def event_to_dict(event_type: str,
                  event_details: Dict[str, AsgiValue]) -> AsgiEvent:
    event_details["type"] = f"websocket.{event_type}"
    return event_details


def _ws_send_to_asgi_dict(event: WSSend) -> AsgiEvent:
    content_key = "text" if isinstance(event.content, str) else "bytes"
    return event_to_dict("send", {content_key: event.content})


def ws_outgoing_to_event_dict(event: WSOutgoingEvent) -> AsgiEvent:
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


ReceiveHandler = Callable[[Scope, WSReceive], Awaitable[WSReceiveOutput]]


def ws_app(
        # todo: are these the right output types?
        connect_handler: Callable[[Scope], Awaitable[Union[WSAccept,
                                                           WSDisconnect,
                                                           WSClose]]],
        receive_handler: ReceiveHandler,
        client_disconnect_handler: Callable[[Scope, Union[WSDisconnect, WSClose]],
                                            Awaitable[None]]
) -> Callable[[Scope], AsgiInstance]:
    def app(scope: Scope) -> AsgiInstance:
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

            connect_response = await connect_handler(scope)

            if not isinstance(connect_response, WSAccept):
                state["app_disconnected"] = True

            await send(ws_outgoing_to_event_dict(connect_response))

            if app_disconnected():
                return None
            else:
                while not client_disconnected() and not app_disconnected():
                    incoming_event: WSIncomingEvent = ws_incoming_to_datatype(
                        await receive())

                    if isinstance(incoming_event, (WSClose, WSDisconnect)):
                        state['client_disconnected'] = True
                        await client_disconnect_handler(scope, incoming_event)
                        return None

                    elif isinstance(incoming_event, WSReceive):
                        outgoing = await receive_handler(scope, incoming_event)

                        if isinstance(outgoing, (WSClose, WSDisconnect)):
                            state['app_disconnected'] = True

                        if outgoing is not None:
                            await send(ws_outgoing_to_event_dict(outgoing))

        return awaitable

    return app


async def basic_connect(scope: Scope) -> WSAccept:
    return WSAccept(subprotocol=None)


async def basic_disconnect(scope: Scope, event) -> None:
    return None


ws_app_receiver_only: Callable[[ReceiveHandler], ScopeAsgiInstance] = (
    partial(ws_app,
            connect_handler=basic_connect,
            client_disconnect_handler=basic_disconnect))
