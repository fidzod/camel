r"""
The Camel Static Site Generator. A powerful tool for building
dynamic Single-Page Web Applications by utilising hash routing.
                  ,,__
        ..  ..   / o._)                   .---.
       /--'/--\  \-'||        .----.    .'     '.
      /        \_/ / |      .'      '..'         '-.
    .'\  \__\  __.'.'     .'          i-._
      )\ |  )\ |      _.'
     // \\ // \\
    ||_  \\|_  \\_
mrf '--' '--'' '--'
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

class Element:
    def __init__(self, tag: str, *children: str | Element):
        self.tag = tag
        self.attributes = []
        self.children = children

    def attr(self, name, value):
        self.attributes.append([name, "string", value])
        return self

    def style(self, atr: str, value: str) -> Element:
        style = f"{atr}: {value};"
        existing = next((atr for atr in self.attributes if atr[0] == "style"), None)
        if existing:
            existing[2] += f" {style}"
        else:
            self.attributes.append(["style", "string", style])
        return self

    def cls(self, name: str) -> Element:
        existing = next((atr for atr in self.attributes if atr[0] == "class"), None)
        if existing:
            existing[2] += f" {name}"
        else:
            self.attributes.append(["class", "string", name])
        return self

    def id_(self, value: str) -> Element:
        self.attr("id", value)
        return self

    def href(self, value: str) -> Element:
        self.attr("href", value)
        return self

    def onClick(self, action: list[str]) -> Element:
        self.attributes.append(["click", "action", action])
        return self


def div(*children):    return Element("div", *children)
def h1(*children):     return Element("h1", *children)
def h2(*children):     return Element("h2", *children)
def h3(*children):     return Element("h3", *children)
def p(*children):      return Element("p", *children)
def a(*children):      return Element("a", *children)
def ul(*children):     return Element("ul", *children)
def li(*children):     return Element("li", *children)
def pre(*children):    return Element("pre", *children)
def button(*children): return Element("button", *children)

class StateRef:
    def __init__(self, label: str):
        self.label = label


class StateProxy:
    def __getattr__(self, label: str) -> StateRef:
        return StateRef(label)


state = StateProxy()

def increment(var: StateRef):
    return ["increment", var.label]

def _makeText(text):
    return ["text", text]

def _makeElem(elem: Element):
    return [
        "elem",
        elem.tag,
        elem.attributes,
        [_makeJSElem(el) for el in elem.children],
    ]

def _makeStateRef(stateRef: StateRef):
    return ["stateRef", stateRef.label]

def _makeJSElem(elem):
    if isinstance(elem, str):
        return _makeText(elem)
    if isinstance(elem, Element):
        return _makeElem(elem)
    if isinstance(elem, StateRef):
        return _makeStateRef(elem)

def _makeJSRouter(router: dict[str, Route]):
    JSRouter = {}

    for key in router.keys():
        route = router[key]
        JSRouter[key] = {"tree": _makeJSElem(route.tree), "state": route.state}

    return JSRouter

@dataclass
class Route:
    tree: Element
    state: dict[str, Any]

    def useState(self, **kwargs: Any) -> Route:
        self.state = kwargs
        return self


class Router:
    def __init__(self):
        self.routes = {}

    def route(self, name: str, *children: str | Element):
        r = Route(tree=div(*children), state={})
        self.routes[name] = r
        return r

    def generate(self):
        js_doc = _makeJSRouter(self.routes)

        site = f"const site = {js_doc};"
        site_out = Path(os.environ.get("CAMEL_OUT", ".")) / "site.js"

        with open(site_out, "w") as f:
            f.write(site)

        runtime_file = Path(__file__).parent / "runtime.js"
        runtime_out = Path(os.environ.get("CAMEL_OUT", ".")) / "runtime.js"

        with open(runtime_file, "r") as f_in:
            with open(runtime_out, "w") as f_out:
                f_out.write(f_in.read())

        return js_doc

