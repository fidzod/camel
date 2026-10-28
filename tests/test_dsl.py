from __future__ import annotations

import dataclasses

import pytest
from hypothesis import given, strategies as st

from camel.dsl import Elem, Fragment


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
