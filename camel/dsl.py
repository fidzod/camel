from __future__ import annotations

__all__ = ["Node", "Elem", "Fragment"]

import dataclasses
from dataclasses import dataclass

type Child = Node | str


class Node:
    def __add__(self, sibling: Child):
        return _fragment(self, sibling)

    def __radd__(self, sibling: Child):
        return _fragment(sibling, self)

    def __bool__(self):
        raise TypeError("Nodes have no truth value; parenthesise `>` chains")


def _flatten(items):
    for item in items:
        if isinstance(item, Fragment):
            yield from _flatten(item.children)
        else:
            yield item


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
