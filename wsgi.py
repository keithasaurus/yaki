#! /usr/bin/env python


def application(environ, start_response):
    import pdb; pdb.set_trace()
    data = bytes("Hello, World!\n", encoding="utf8")
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
