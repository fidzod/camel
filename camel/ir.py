from __future__ import annotations

__all__ = ["to_ir"]

from functools import singledispatch
from typing import Literal, TypedDict
from camel.dsl import Elem, Fragment

# See docs/ir.md
type IRNode = ElemIR | FragmentIR | TextIR


class ElemIR(TypedDict):
    type: Literal["Elem"]
    tag: str
    classes: tuple[str, ...]
    children: tuple[IRNode, ...]


class FragmentIR(TypedDict):
    type: Literal["Fragment"]
    children: tuple[IRNode, ...]


class TextIR(TypedDict):
    type: Literal["Text"]
    contents: str


@singledispatch
def to_ir(node) -> IRNode:
    raise TypeError(f"don't know how to compile {type(node)!r}")


@to_ir.register
def _(node: str) -> TextIR:
    return {"type": "Text", "contents": node}


@to_ir.register
def _(elem: Elem) -> ElemIR:
    return {
        "type": "Elem",
        "tag": elem.tag,
        "classes": elem.classes,
        "children": tuple(map(to_ir, elem.children)),
    }


@to_ir.register
def _(fragment: Fragment) -> FragmentIR:
    return {
        "type": "Fragment",
        "children": tuple(map(to_ir, fragment.children)),
    }
