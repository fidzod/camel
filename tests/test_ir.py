from __future__ import annotations

from typing import cast

import pytest

from camel.dsl import Elem, Empty, Let, PartialIf, StateRef
from camel.ir import AddActionIR, AppendActionIR, ElemIR, TextIR, to_ir


def test_text():
    assert to_ir("hello") == {"type": "Text", "contents": "hello"}


def test_elem():
    elem = Elem("div", classes=("card",)) > "hi"
    assert to_ir(elem) == {
        "type": "Elem",
        "tag": "div",
        "classes": ("card",),
        "children": ({"type": "Text", "contents": "hi"},),
        "events": (),
        "bind": {"type": "Empty"},
    }


def test_fragment():
    fragment = Elem("p") + Elem("span")
    assert to_ir(fragment) == {
        "type": "Fragment",
        "children": (
            {
                "type": "Elem", "tag": "p", "classes": (), "children": (),
                "events": (), "bind": {"type": "Empty"},
            },
            {
                "type": "Elem", "tag": "span", "classes": (), "children": (),
                "events": (), "bind": {"type": "Empty"},
            },
        ),
    }


def test_unregistered_type_raises():
    with pytest.raises(TypeError):
        to_ir(42)


def test_state_ref():
    assert to_ir(StateRef("clicks")) == {"type": "StateRef", "name": "clicks"}


def test_state():
    state = Let((("clicks", 0),)).in_(Elem("h3") > StateRef("clicks"))
    assert to_ir(state) == {
        "type": "State",
        "initial": {"clicks": 0},
        "child": {
            "type": "Elem",
            "tag": "h3",
            "classes": (),
            "children": ({"type": "StateRef", "name": "clicks"},),
            "events": (),
            "bind": {"type": "Empty"},
        },
    }


def test_empty():
    assert to_ir(Empty()) == {"type": "Empty"}


def test_if_with_literal_and_explicit_otherwise():
    built = PartialIf(StateRef("clicks") == 1).then("click").otherwise("clicks")
    assert to_ir(built) == {
        "type": "If",
        "condition": {
            "type": "Condition",
            "op": "Eq",
            "left": {"type": "StateRef", "name": "clicks"},
            "right": {"type": "Literal", "value": 1},
        },
        "then": {"type": "Text", "contents": "click"},
        "otherwise": {"type": "Text", "contents": "clicks"},
    }


def test_if_otherwise_defaults_to_empty():
    built = PartialIf(StateRef("clicks") == 1).then("click")
    ir = to_ir(built)
    assert ir["type"] == "If"
    assert ir["otherwise"] == {"type": "Empty"}


def test_on_click_add_action():
    elem = Elem("button").on_click(StateRef("clicks").add(1))
    assert to_ir(elem) == {
        "type": "Elem",
        "tag": "button",
        "classes": (),
        "children": (),
        "events": (
            {
                "name": "click",
                "actions": (
                    {
                        "type": "Action",
                        "name": "Add",
                        "target": {"type": "StateRef", "name": "clicks"},
                        "amount": {"type": "Literal", "value": 1},
                    },
                ),
            },
        ),
        "bind": {"type": "Empty"},
    }


def test_add_action_amount_may_be_a_state_ref():
    elem = Elem("button").on_click(StateRef("clicks").add(StateRef("step")))
    ir = to_ir(elem)
    assert ir["type"] == "Elem"
    (event,) = ir["events"]
    (action,) = (cast(AddActionIR, a) for a in event["actions"])
    assert action["amount"] == {"type": "StateRef", "name": "step"}


def test_on_click_append_action():
    elem = Elem("button").on_click(StateRef("tasks").append("milk"))
    assert to_ir(elem) == {
        "type": "Elem",
        "tag": "button",
        "classes": (),
        "children": (),
        "events": (
            {
                "name": "click",
                "actions": (
                    {
                        "type": "Action",
                        "name": "Append",
                        "target": {"type": "StateRef", "name": "tasks"},
                        "value": {"type": "Literal", "value": "milk"},
                    },
                ),
            },
        ),
        "bind": {"type": "Empty"},
    }


def test_append_action_value_may_be_a_state_ref():
    elem = Elem("button").on_click(StateRef("tasks").append(StateRef("new")))
    ir = to_ir(elem)
    assert ir["type"] == "Elem"
    (event,) = ir["events"]
    (action,) = (cast(AppendActionIR, a) for a in event["actions"])
    assert action["value"] == {"type": "StateRef", "name": "new"}


def test_on_click_restore_action():
    elem = Elem("button").on_click(StateRef("new").restore())
    assert to_ir(elem) == {
        "type": "Elem",
        "tag": "button",
        "classes": (),
        "children": (),
        "events": (
            {
                "name": "click",
                "actions": (
                    {
                        "type": "Action",
                        "name": "Restore",
                        "target": {"type": "StateRef", "name": "new"},
                    },
                ),
            },
        ),
        "bind": {"type": "Empty"},
    }


def test_bind_defaults_to_empty():
    elem = Elem("input")
    ir = to_ir(elem)
    assert ir["type"] == "Elem"
    assert ir["bind"] == {"type": "Empty"}


def test_bind_compiles_to_its_state_ref():
    elem = Elem("input").bind(StateRef("new"))
    ir = to_ir(elem)
    assert ir["type"] == "Elem"
    assert ir["bind"] == {"type": "StateRef", "name": "new"}


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
