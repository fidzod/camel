__all__ = ["to_ir"]

from functools import singledispatch

from camel.dsl import Elem, Container


## TODO replace return type with TypedDict
## Depends on settling IR
@singledispatch
def to_ir(node) -> dict:
    raise TypeError(f"don't know how to compile {type(node)!r}")


@to_ir.register
def _(node: str):
    return {"type": "Text", "contents": node}


@to_ir.register
def _(node: Elem):
    return {
        "type": "Elem",
        "tag": node.tag,
        "classes": node.classes,
        "children": list(map(to_ir, node.children)),
    }


@to_ir.register
def _(node: Container):
    return {"type": "Container", "children": list(map(to_ir, node.children))}
