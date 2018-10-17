from .views import form_view
from yaki.apps import yaki
from yaki.http.config import http_app

app = yaki(
    # serve the html via yaki
    http_app(
        routes=[
            ("/", form_view)],
        middleware=[]
    ),
)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
