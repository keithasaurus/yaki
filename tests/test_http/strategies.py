import random

from hypothesis import strategies as st

def coinflip():
    return random.random() > .5


@st.composite
def query_string(draw):
    strs = []
    for _ in range(random.randint(0, 10)):
        key = draw(st.text(min_size=1,
                           max_size=30)
                   .map(lambda x: x.strip())
                   .filter(lambda x: len(x) > 0))
        val = draw(st.text(max_size=40))
        strs.append(f"{key}={val}")

    joined = "&".join(strs)
    return bytes(joined, encoding="utf8")


@st.composite
def host_and_port(draw):
    return [st.text(min_size=1), random.randint(1, 10000)]


@st.composite
def asgi_http_scope(draw):
    ret = {
        "type": "http",
        "headers": draw(
            st.lists(
                st.lists(
                    st.text().map(lambda x: bytes(x.lower(), encoding="utf8")),
                    min_size=2,
                    max_size=2),
                min_size=0,
                max_size=40)),
        "http_version": random.choice(["1.0", "1.1", "1.2"]),
        "method": random.choice(["CONNECT",
                                 "DELETE",
                                 "GET",
                                 "HEAD",
                                 "OPTIONS",
                                 "PATCH",
                                 "POST",
                                 "PUT",
                                 "TRACE"]),
        "path": "/" + draw(st.text()),
        "query_string": draw(query_string()),
    }

    if coinflip():
        ret['client'] = draw(host_and_port())

    if coinflip():
        ret['server'] = draw(host_and_port())

    if coinflip():
        ret["scheme"] = draw(st.text(min_size=1))

    if coinflip():
        ret["root_path"] = draw(st.text())

    return ret


@st.composite
def asgi_http_request(draw):
    ret = {"type": "http.request",
           "body": bytes(draw(st.text()), encoding="utf8"),
           "more_body": False}

    # todo: return multiple requests with only the
    # last with more_body=False
    if coinflip():
        ret["more_body"] = False

    return ret