from __future__ import annotations

__all__ = ["Node", "Elem", "Container"]

import dataclasses
from dataclasses import dataclass

type Child = Node | str


class Node:
    def __add__(self, sibling: Child):
        return _container(self, sibling)

    def __radd__(self, sibling: Child):
        return _container(sibling, self)

    def __bool__(self):
        raise TypeError("Nodes have no truth value; parenthesise `>` chains")


@dataclass(frozen=True)
class Elem(Node):
    tag: str
    children: tuple[Child, ...] = ()
    classes: tuple[str, ...] = ()

    def __gt__(self, child: Child):
        return dataclasses.replace(self, children=self.children + (child,))

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name) from None
        return dataclasses.replace(self, classes=self.classes + (name,))


def _flatten(items):
    for item in items:
        if isinstance(item, Container):
            yield from _flatten(item.children)
        else:
            yield item


@dataclass(frozen=True)
class Container(Node):
    children: tuple[Child, ...]


def _container(*items) -> Container:
    return Container(tuple(_flatten(items)))
