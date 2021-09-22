from .http_endpoint import serve_html_page
from .ws_endpoint import ws_chat_bot
from yaki.apps import yaki
from yaki.http.config import http_app
from yaki.websockets.config import ws_app

app = yaki(
    # serve the html via yaki
    http_app(routes=[("/", serve_html_page)], middleware=[]),
    # provide a chatbot websocket
    ws_app(routes=[("/chat", ws_chat_bot)]),
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=5000)
