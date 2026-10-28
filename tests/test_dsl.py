from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given, strategies as st

from camel.dsl import Elem, Fragment, Let, State, StateRef, StateRefProxy


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


def test_state_ref_equality():
    assert StateRef("clicks") == StateRef("clicks")
    assert StateRef("clicks") != StateRef("other")


def test_state_ref_proxy_builds_named_refs():
    proxy = StateRefProxy()
    assert proxy.clicks == StateRef("clicks")


def test_state_ref_proxy_rejects_underscore_names():
    proxy = StateRefProxy()
    assert not hasattr(proxy, "_private")
    with pytest.raises(AttributeError):
        proxy._private
