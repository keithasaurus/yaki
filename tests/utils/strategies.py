from hypothesis import strategies as st

import random


def coinflip() -> bool:
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
def headers(draw):
    return draw(st.lists(
        st.lists(
            st.text().map(lambda x: bytes(x.lower(), encoding="utf8")),
            min_size=2,
            max_size=2),
        min_size=0,
        max_size=40))


@st.composite
def host_and_port(draw):
    return [st.text(min_size=1), random.randint(1, 10000)]
