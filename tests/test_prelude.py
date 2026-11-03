from __future__ import annotations

import pytest

from camel.dsl import Elem
from camel.prelude import let


def test_let_converts_list_bindings_to_tuples():
    built = let(tasks=["milk", "eggs"]).in_(Elem("h1"))
    [(name, value)] = built.initial
    assert name == "tasks"
    assert value == ("milk", "eggs")
    assert isinstance(value, tuple)


def test_let_with_list_binding_is_hashable():
    # Regression: let() only converted the outer bindings dict into a tuple
    # of pairs, never the individual values - a list-valued binding (e.g.
    # tasks=[]) survived as a raw, unhashable list inside State.
    built = let(tasks=[]).in_(Elem("h1"))
    hash(built)  # must not raise


def test_let_rejects_a_tuple_binding():
    with pytest.raises(TypeError):
        let(tasks=("milk", "eggs"))  # pyright: ignore[reportArgumentType]


def test_let_rejects_a_list_with_invalid_elements():
    with pytest.raises(TypeError):
        let(tasks=[1.5])  # pyright: ignore[reportArgumentType]


def test_let_rejects_an_invalid_scalar():
    with pytest.raises(TypeError):
        let(tasks=1.5)  # pyright: ignore[reportArgumentType]


def test_let_leaves_scalar_bindings_untouched():
    built = let(clicks=0, label="x").in_(Elem("h1"))
    assert dict(built.initial) == {"clicks": 0, "label": "x"}
