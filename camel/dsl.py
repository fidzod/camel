from __future__ import annotations

__all__ = ["Node", "Elem", "Fragment", "Let", "StateRefProxy"]

from collections.abc import Iterable, Iterator
import dataclasses
from dataclasses import dataclass
from typing import Any, Literal

type Child = Node | str


def _is_child(x: Any) -> bool:
    return isinstance(x, Child.__value__)


def _require_child(x: Any) -> None:
    if not _is_child(x):
        raise TypeError(f"{x!r} is not a valid child: expected a Node or str")


def _flatten(items: Iterable[Child]) -> Iterator[Child]:
    for item in items:
        if isinstance(item, Fragment):
            yield from _flatten(item.children)
        else:
            _require_child(item)
            yield item


class Node:
    def __add__(self, sibling: Child):
        return _fragment(self, sibling)

    def __radd__(self, sibling: Child):
        return _fragment(sibling, self)

    def __bool__(self):
        raise TypeError("Nodes have no truth value; parenthesise `>` chains")


@dataclass(frozen=True)
class Elem(Node):
    tag: str
    children: tuple[Child, ...] = ()
    classes: tuple[str, ...] = ()

    def __gt__(self, child: Child):
        return dataclasses.replace(
            self, children=tuple(_flatten(self.children + (child,)))
        )

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name) from None
        return dataclasses.replace(self, classes=self.classes + (name,))


@dataclass(frozen=True)
class Fragment(Node):
    children: tuple[Child, ...]


def _fragment(*items) -> Fragment:
    return Fragment(tuple(_flatten(items)))


type Bindings = tuple[tuple[str, int | str], ...]


@dataclass(frozen=True)
class State(Node):
    initial: Bindings
    child: Child


@dataclass(frozen=True)
class Let:
    bindings: Bindings

    def in_(self, child: Child) -> State:
        _require_child(child)
        return State(self.bindings, child)


@dataclass(frozen=True)
class StateRef(Node):
    name: str

    def __eq__(self, value: Value) -> Condition: # pyright: ignore[reportIncompatibleMethodOverride]
        # Deliberately violate __eq__'s contract: state.x == y builds a
        # reactive Condition, not a bool.
        return Condition("Eq", self, value)


class StateRefProxy:
    def __getattr__(self, name: str) -> StateRef:
        if name.startswith("_"):
            raise AttributeError(name) from None
        return StateRef(name)


@dataclass(frozen=True)
class Empty(Node):
    pass


type Value = int | str | StateRef


def _value_equal(a: Value, b: Value) -> bool:
    if isinstance(a, StateRef) or isinstance(b, StateRef):
        return isinstance(a, StateRef) and isinstance(b, StateRef) and a.name == b.name
    return a == b


@dataclass(frozen=True)
class Condition:
    op: Literal["Eq"]  # "Gt", ...
    left: Value
    right: Value

    # Hand-written because the generated __eq__ would compare left/right
    # with `==`, and when either is a StateRef that calls StateRef.__eq__,
    # which returns a Condition instead of a bool - poisoning equality for
    # Condition itself and, transitively, for anything containing one
    # (If, and any Elem/Fragment tree with a conditional anywhere inside).
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Condition):
            return NotImplemented
        return (
                self.op == other.op
                and _value_equal(self.left, other.left)
                and _value_equal(self.right, other.right)
            )

    def __bool__(self):
        raise TypeError("Conditions have no truth value; use .then()/.otherwise()")


@dataclass(frozen=True)
class If(Node):
    condition: Condition
    then: Child
    otherwise_: Child

    def otherwise(self, otherwise: Child) -> If:
        _require_child(otherwise)
        return dataclasses.replace(self, otherwise_=otherwise)


@dataclass(frozen=True)
class PartialIf:
    condition: Condition

    def then(self, then: Child) -> If:
        _require_child(then)
        return If(self.condition, then, Empty())
