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
from typing import Any, Callable


class StateRef:
    def __init__(self, label: str):
        self.label = label


class StateProxy:
    def __getattr__(self, label: str) -> StateRef:
        return StateRef(label)


state = StateProxy()


@dataclass
class Action:
    name: str
    arguments: list[StateRef]


def increment(
    var: StateRef,
) -> Action:
    return Action(name="increment", arguments=[var])


class Element:
    def __init__(self, tag: str, *children: str | Element):
        self.tag = tag
        self.attributes = []
        self.children = children

    def attr(self, name, value) -> Element:
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
        return self.attr("id", value)

    def href(self, value: str) -> Element:
        return self.attr("href", value)

    def onClick(self, action: Action) -> Element:
        self.attributes.append(["click", "action", action])
        return self


def div(*children):
    return Element("div", *children)


def h1(*children):
    return Element("h1", *children)


def h2(*children):
    return Element("h2", *children)


def h3(*children):
    return Element("h3", *children)


def p(*children):
    return Element("p", *children)


def a(*children):
    return Element("a", *children)


def ul(*children):
    return Element("ul", *children)


def li(*children):
    return Element("li", *children)


def pre(*children):
    return Element("pre", *children)


def button(*children):
    return Element("button", *children)


def _compileAction(action: Action):
    return [action.name, [_compileStateRef(arg) for arg in action.arguments]]


def _compileText(text: str):
    return ["text", text]


def _compileElement(elem: Element):
    for i, attr in enumerate(elem.attributes):
        if attr[1] == "action":
            elem.attributes[i][2] = _compileAction(attr[2])
    return [
        "elem",
        elem.tag,
        elem.attributes,
        [_compile(el) for el in elem.children],
    ]


def _compileStateRef(stateRef: StateRef):
    return ["stateRef", stateRef.label]


def _compile(elem):
    if isinstance(elem, str):
        return _compileText(elem)
    if isinstance(elem, Element):
        return _compileElement(elem)
    if isinstance(elem, StateRef):
        return _compileStateRef(elem)

    raise TypeError(f"Cannot compile object of type {type(elem).__name__}")


def _compileSite(routes: dict[str, Route]):
    site = {}

    for key in routes.keys():
        route = routes[key]
        site[key] = {"tree": _compile(route.tree), "state": route.state}

    return site


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

    def route(self, name: str) -> Callable[..., Route]:
        def inner(*children: str | Element | StateRef):
            r = Route(tree=div(*children), state={})
            self.routes[name] = r
            return r
        return inner

    def generate(self) -> None:
        site = f"const site = {_compileSite(self.routes)};"
        site_out = Path(os.environ.get("CAMEL_OUT", ".")) / "site.js"

        with open(site_out, "w") as f:
            f.write(site)

        runtime_file = Path(__file__).parent / "runtime.js"
        runtime_out = Path(os.environ.get("CAMEL_OUT", ".")) / "runtime.js"

        with open(runtime_file, "r") as f_in:
            with open(runtime_out, "w") as f_out:
                f_out.write(f_in.read())

