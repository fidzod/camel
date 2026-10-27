__all__ = ["to_ir"]

from functools import singledispatch

from camel.dsl import Elem, Container


@singledispatch
def to_ir(node):
    raise TypeError(f"don't know how to compile {type(node)!r}")


@to_ir.register
def _(node: str):
    return {"type": "Text", "contents": node}


@to_ir.register
def _(node: Elem):
    return {
        "type": "Elem",
        "tag": node.tag,
        "class_list": node.class_list,
        "children": list(map(to_ir, node.children)),
    }


@to_ir.register
def _(node: Container):
    return {"type": "Container", "children": list(map(to_ir, node.children))}
