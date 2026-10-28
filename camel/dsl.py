from __future__ import annotations

__all__ = ["Node", "Elem", "Fragment", "Let", "StateRefProxy"]

from collections.abc import Iterable, Iterator
import dataclasses
from dataclasses import dataclass
from typing import Any

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


class StateRefProxy:
    def __getattr__(self, name: str) -> StateRef:
        if name.startswith("_"):
            raise AttributeError(name) from None
        return StateRef(name)
