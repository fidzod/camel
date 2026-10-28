from __future__ import annotations

from typing import cast

import pytest

from camel.dsl import Elem
from camel.ir import ElemIR, TextIR, to_ir


def test_text():
    assert to_ir("hello") == {"type": "Text", "contents": "hello"}


def test_elem():
    elem = Elem("div", classes=("card",)) > "hi"
    assert to_ir(elem) == {
        "type": "Elem",
        "tag": "div",
        "classes": ("card",),
        "children": ({"type": "Text", "contents": "hi"},),
    }


def test_fragment():
    fragment = Elem("p") + Elem("span")
    assert to_ir(fragment) == {
        "type": "Fragment",
        "children": (
            {"type": "Elem", "tag": "p", "classes": (), "children": ()},
            {"type": "Elem", "tag": "span", "classes": (), "children": ()},
        ),
    }


def test_unregistered_type_raises():
    with pytest.raises(TypeError):
        to_ir(42)


def test_realistic_tree_compiles_flat():
    site = (Elem("h1").brand_color > "Camel.py") + (
        Elem("div").card.featured
        > (
            (Elem("h2") > "What's new?")
            + (Elem("ul") > ((Elem("li") > "a") + (Elem("li") > "b")))
        )
    )

    ir = to_ir(site)
    assert ir["type"] == "Fragment"

    div_ir = cast(ElemIR, ir["children"][1])
    assert div_ir["type"] == "Elem"
    assert div_ir["tag"] == "div"

    h2_ir, ul_ir = (cast(ElemIR, child) for child in div_ir["children"])
    assert h2_ir["tag"] == "h2"
    assert ul_ir["tag"] == "ul"

    li_a_ir, li_b_ir = (cast(ElemIR, child) for child in ul_ir["children"])

    (text_a,) = (cast(TextIR, child) for child in li_a_ir["children"])
    (text_b,) = (cast(TextIR, child) for child in li_b_ir["children"])
    assert text_a["contents"] == "a"
    assert text_b["contents"] == "b"
