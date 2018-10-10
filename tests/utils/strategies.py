from hypothesis import strategies as st

import random


@st.composite
def query_string(draw):
    strs = []
    for _ in range(random.randint(0, 10)):
        key = draw(st.text(min_size=1,
                           max_size=20)
                   .map(lambda x: x.strip())
                   .filter(lambda x: len(x) > 0))
        val = draw(st.text(max_size=40))
        strs.append(f"{key}={val}")

    joined = "&".join(strs)
    return bytes(joined, encoding="utf8")


@st.composite
def header_string(draw):
    return draw(
        st.text(max_size=100).map(lambda x: bytes(x.lower(), encoding="utf8"))
    )


@st.composite
def headers(draw):
    return draw(st.lists(
        st.lists(
            header_string(),
            min_size=2,
            max_size=2),
        min_size=0,
        max_size=15))


@st.composite
def host_and_port(draw):
    return [draw(st.text(min_size=1)), random.randint(1, 10000)]


@st.composite
def scope_extensions(draw):
    return draw(st.dictionaries(st.text(),
                                st.dictionaries(st.text(),
                                                st.text(),
                                                max_size=5),
                                max_size=5))
