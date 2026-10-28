__all__ = [
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "b",
    "a",
    "i",
    "div",
    "ul",
    "li",
    "button",
    "input_",
    "pre",
    "code",
    "let",
    "state",
    "if_",
    "generate",
]

from camel.dsl import Condition, Elem, Let, PartialIf, StateRefProxy
from camel.site import generate

# HTML Tags
h1 = Elem("h1")
h2 = Elem("h2")
h3 = Elem("h3")
h4 = Elem("h4")
h5 = Elem("h5")
h6 = Elem("h6")
p = Elem("p")
b = Elem("b")
a = Elem("a")
i = Elem("i")
div = Elem("div")
ul = Elem("ul")
li = Elem("li")
button = Elem("button")
input_ = Elem("input")
pre = Elem("pre")
code = Elem("code")


# State
def let(**bindings: int | str):
    return Let(tuple(bindings.items()))


state = StateRefProxy()


# Conditionals
def if_(cond: Condition) -> PartialIf:
    return PartialIf(cond)
