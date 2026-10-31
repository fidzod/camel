from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given, strategies as st

from camel.dsl import (
    Action,
    Condition,
    Elem,
    Empty,
    Event,
    Fragment,
    If,
    Let,
    Node,
    PartialIf,
    State,
    StateRef,
    StateRefProxy,
    StyleScope,
)


def test_bool_is_disallowed():
    with pytest.raises(TypeError):
        bool(Elem("div"))


def test_frozen():
    elem = Elem("div")
    with pytest.raises(dataclasses.FrozenInstanceError):
        elem.tag = "p"  # pyright: ignore[reportAttributeAccessIssue]


def test_equality():
    assert (Elem("div") > "x") == (Elem("div") > "x")
    assert (Elem("div") > "x") != (Elem("div") > "y")


def test_hashable():
    hash(Elem("div") > "x")  # must not raise


def test_emmet_classes_accumulate_in_order():
    styled = Elem("div").card.featured
    assert styled.classes == ("card", "featured")


def test_getattr_rejects_underscore_names():
    assert not hasattr(Elem("div"), "_private")
    with pytest.raises(AttributeError):
        Elem("div")._private


def test_radd_wraps_leading_string():
    assert ("prefix" + Elem("p")) == Fragment(("prefix", Elem("p")))


def test_gt_flattens_fragment_children():
    heading, listing = Elem("h2") > "heading", Elem("ul") > "list"
    nested = Elem("div") > (heading + listing)
    direct = (Elem("div") > heading) > listing
    assert nested.children == direct.children == (heading, listing)


def test_add_is_associative_and_flat():
    a, b, c = Elem("em") > "a", Elem("em") > "b", Elem("em") > "c"
    assert (a + b) + c == a + (b + c) == Fragment((a, b, c))


@given(
    st.lists(
        st.one_of(st.just(Elem("p")), st.just(Elem("span")), st.text(max_size=5)),
        min_size=1,
        max_size=5,
    )
)
def test_fragment_children_never_contain_a_fragment(parts):
    result = Elem("div")
    for part in parts:
        result = result + part
    if isinstance(result, Fragment):
        assert all(not isinstance(child, Fragment) for child in result.children)


def test_add_and_gt_reject_invalid_children():
    with pytest.raises(TypeError):
        _ = Elem("div") + Let((("clicks", 0),))  # pyright: ignore[reportOperatorIssue]
    with pytest.raises(TypeError):
        _ = Elem("div") > 42  # pyright: ignore[reportOperatorIssue]


def test_let_in_builds_state():
    built = Let((("clicks", 0),)).in_(Elem("h3"))
    assert built == State((("clicks", 0),), Elem("h3"))


def test_let_in_rejects_invalid_child():
    with pytest.raises(TypeError):
        Let((("clicks", 0),)).in_(42)  # pyright: ignore[reportArgumentType]


def test_state_and_let_are_hashable():
    hash(State((("clicks", 0),), Elem("h3")))  # must not raise
    hash(Let((("clicks", 0),)))  # must not raise


def test_state_nests_as_a_child():
    nested = Elem("div") > Let((("clicks", 0),)).in_(Elem("h3"))
    assert nested.children == (State((("clicks", 0),), Elem("h3")),)


def test_state_ref_eq_builds_condition():
    condition = StateRef("clicks") == 1
    assert condition == Condition("Eq", StateRef("clicks"), 1)


def test_condition_has_no_truth_value():
    with pytest.raises(TypeError):
        bool(StateRef("clicks") == 1)


def test_state_ref_proxy_builds_named_refs():
    proxy = StateRefProxy()
    assert proxy.clicks.name == StateRef("clicks").name


def test_state_ref_proxy_rejects_underscore_names():
    proxy = StateRefProxy()
    assert not hasattr(proxy, "_private")
    with pytest.raises(AttributeError):
        proxy._private


def test_empty_is_hashable_and_equal():
    assert Empty() == Empty()
    assert hash(Empty()) == hash(Empty())


def test_then_defaults_otherwise_to_empty():
    built = PartialIf(StateRef("clicks") == 1).then("click")
    assert built == If(Condition("Eq", StateRef("clicks"), 1), "click", Empty())


def test_otherwise_replaces_the_default():
    built = PartialIf(StateRef("clicks") == 1).then("click").otherwise("clicks")
    assert built == If(Condition("Eq", StateRef("clicks"), 1), "click", "clicks")


def test_then_and_otherwise_reject_invalid_children():
    with pytest.raises(TypeError):
        PartialIf(StateRef("clicks") == 1).then(42)  # pyright: ignore[reportArgumentType]
    with pytest.raises(TypeError):
        PartialIf(StateRef("clicks") == 1).then("click").otherwise(42)  # pyright: ignore[reportArgumentType]


def test_if_equality_survives_nested_state_refs():
    # Regression: Condition's default eq would recurse into StateRef.__eq__,
    # which returns a Condition rather than a bool, poisoning equality for
    # anything containing one - including a full Elem tree.
    tree1 = Elem("h3") > PartialIf(StateRef("clicks") == 1).then("click")
    tree2 = Elem("h3") > PartialIf(StateRef("clicks") == 1).then("click")
    assert tree1 == tree2


def test_state_ref_inequality_raises_rather_than_lying():
    with pytest.raises(TypeError):
        StateRef("clicks") != StateRef("other")  # pyright: ignore[reportUnusedExpression]


def test_add_builds_an_action():
    action = StateRef("clicks").add(1)
    assert isinstance(action, Action)


def test_on_click_builds_event():
    action = StateRef("clicks").add(1)
    built = Elem("button").on_click(action)
    assert built.events == (Event("click", (action,)),)


def test_on_click_accepts_multiple_actions():
    a1, a2 = StateRef("clicks").add(1), StateRef("other").add(2)
    built = Elem("button").on_click(a1, a2)
    assert built.events == (Event("click", (a1, a2)),)


def test_on_click_rejects_invalid_actions():
    with pytest.raises(TypeError):
        Elem("button").on_click(42)  # pyright: ignore[reportArgumentType]


def test_add_action_is_hashable():
    hash(StateRef("clicks").add(1))  # must not raise


def test_add_action_equality_survives_state_ref():
    # Regression: AddAction's default eq would recurse into StateRef.__eq__,
    # which returns a Condition rather than a bool, poisoning equality for
    # AddAction itself and, transitively, for anything containing one
    # (Event, and any Elem tree with an on_click action anywhere inside).
    a1 = StateRef("clicks").add(1)
    a2 = StateRef("clicks").add(1)
    assert a1 == a2

    tree1 = Elem("button").on_click(a1)
    tree2 = Elem("button").on_click(a2)
    assert tree1 == tree2


def test_restore_builds_an_action():
    action = StateRef("new").restore()
    assert isinstance(action, Action)


def test_restore_action_is_hashable():
    hash(StateRef("new").restore())  # must not raise


def test_restore_action_equality_survives_state_ref():
    # Same StateRef-poisoning hazard as AddAction/AppendAction, see above.
    a1 = StateRef("new").restore()
    a2 = StateRef("new").restore()
    assert a1 == a2

    tree1 = Elem("button").on_click(a1)
    tree2 = Elem("button").on_click(a2)
    assert tree1 == tree2


def test_elem_bind_defaults_to_empty():
    assert Elem("input").bind_ == Empty()


def test_bind_attaches_the_state_ref():
    elem = Elem("input").bind(StateRef("new"))
    assert isinstance(elem.bind_, StateRef)
    assert elem.bind_.name == "new"


def test_bind_rejects_a_non_input_element():
    with pytest.raises(TypeError):
        Elem("p").bind(StateRef("new"))


def test_append_builds_an_action():
    action = StateRef("tasks").append("milk")
    assert isinstance(action, Action)


def test_append_action_is_hashable():
    hash(StateRef("tasks").append("milk"))  # must not raise


def test_append_action_equality_survives_state_ref():
    # Same StateRef-poisoning hazard as AddAction, see above.
    a1 = StateRef("tasks").append("milk")
    a2 = StateRef("tasks").append("milk")
    assert a1 == a2

    tree1 = Elem("button").on_click(a1)
    tree2 = Elem("button").on_click(a2)
    assert tree1 == tree2


def test_style_wraps_the_node_in_a_style_scope():
    node = Elem("div")
    scope = node.style({"p": {"color": "red"}})
    assert isinstance(scope, StyleScope)
    assert scope.child is node


def test_style_converts_rules_to_tuples():
    scope = Elem("div").style(
        {
            "p": {"color": "red", "font-weight": "bold"},
            ".large:hover": {"color": "blue"},
        }
    )
    assert scope.rules == (
        ("p", (("color", "red"), ("font-weight", "bold"))),
        (".large:hover", (("color", "blue"),)),
    )


def test_style_scope_is_a_node_and_is_usable_as_a_child():
    scope = Elem("p").style({"p": {"color": "red"}})
    assert isinstance(scope, Node)
    built = Elem("div") > scope
    assert scope in built.children


def test_style_scope_is_hashable():
    hash(Elem("div").style({"p": {"color": "red"}}))  # must not raise


def test_style_scope_equality_and_hash_are_structural():
    s1 = Elem("div").style({"p": {"color": "red"}})
    s2 = Elem("div").style({"p": {"color": "red"}})
    assert s1 == s2
    assert hash(s1) == hash(s2)


def test_style_scope_inequality_for_different_rules():
    s1 = Elem("div").style({"p": {"color": "red"}})
    s2 = Elem("div").style({"p": {"color": "blue"}})
    assert s1 != s2


def test_style_scopes_nest():
    inner = Elem("p").style({"p": {"color": "red"}})
    outer = (Elem("div") > inner).style({"div": {"margin": "0"}})
    assert isinstance(outer, StyleScope)
    assert isinstance(outer.child, Elem)
    assert inner in outer.child.children
