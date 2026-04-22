r"""
A reactive Python-native UI framework that compiles to
a self-contained vanilla JS bundle with hash routing.
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
from typing import Any, Callable, Optional


class StateRef:
    def __init__(self, label: str):
        self.label = label


class StateProxy:
    def __getattr__(self, label: str) -> StateRef:
        return StateRef(label)


state = StateProxy()


class VarRef:
    def __init__(self, label: str):
        self.label = label

    def __getattr__(self, label: str) -> VarRef:
        return VarRef(f"{self.label}.{label}")


class VarProxy:
    def __getattr__(self, label: str) -> VarRef:
        return VarRef(label)


var = VarProxy()


def fetch(*args: str) -> list[str]:
    return ["fetch", "/".join(list(args))]


@dataclass
class Action:
    name: str
    arguments: list[Any]

    def method(self, m: str) -> Action:
        self.arguments.append(m)
        return self


def increment(
    var: StateRef,
) -> Action:
    return Action(name="increment", arguments=[var])


def append(list_: StateRef, value: StateRef) -> Action:
    return Action(name="append", arguments=[list_, value])


def set_(stateRef: StateRef, value: Any) -> Action:
    return Action(name="set", arguments=[stateRef, value])


def delete(stateRef: StateRef, index: int | VarRef) -> Action:
    return Action(name="delete", arguments=[stateRef, index])


def post(*args: str | VarRef, **kwargs: Any) -> Action:
    return Action(
        name="post",
        arguments=[
            [_compile(arg) for arg in args],
            [[k, _compile(v)] for k, v in kwargs.items()],
        ],
    )


@dataclass
class Condition:
    name: str
    left: int | str | StateRef
    right: int | str | StateRef


def eq(left: int | str | StateRef, right: int | str | StateRef) -> Condition:
    return Condition(name="eq", left=left, right=right)


def gt(left: int | str | StateRef, right: int | str | StateRef) -> Condition:
    return Condition(name="gt", left=left, right=right)


def gte(left: int | str | StateRef, right: int | str | StateRef) -> Condition:
    return Condition(name="gte", left=left, right=right)


def lt(left: int | str | StateRef, right: int | str | StateRef) -> Condition:
    return Condition(name="lt", left=left, right=right)


def lte(left: int | str | StateRef, right: int | str | StateRef) -> Condition:
    return Condition(name="lte", left=left, right=right)


@dataclass
class If:
    condition: Condition
    consequent: str | Element
    alternate: Optional[str | Element]


def if_(
    condition: Condition,
    consequent: str | Element,
    alternate: Optional[str | Element] = None,
) -> If:
    return If(condition=condition, consequent=consequent, alternate=alternate)


@dataclass
class Each:
    list_: StateRef
    template: list[Element | str | VarRef | StateRef]
    itemName: str = "item"

    def as_(self, itemName: VarRef) -> Each:
        self.itemName = itemName.label
        return self

    def __call__(self, *children: Element | str | VarRef | StateRef) -> Each:
        self.template = list(children)
        return self


def each(list_: StateRef) -> Each:
    return Each(list_=list_, template=[])


@dataclass
class Element:
    tag: str
    children: tuple[str | Element]
    attributes: list[Any]

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

    def placeholder(self, value: str) -> Element:
        return self.attr("placeholder", value)

    def bind(self, stateVar: StateRef) -> Element:
        self.attributes.append(["bind", "bind", stateVar])
        return self

    def onClick(self, *actions: Action) -> Element:
        self.attributes.append(["click", "action", list(actions)])
        return self


def div(*children):
    return Element(tag="div", attributes=[], children=children)


def h1(*children):
    return Element(tag="h1", attributes=[], children=children)


def h2(*children):
    return Element(tag="h2", attributes=[], children=children)


def h3(*children):
    return Element(tag="h3", attributes=[], children=children)


def p(*children):
    return Element(tag="p", attributes=[], children=children)


def a(*children):
    return Element(tag="a", attributes=[], children=children)


def ul(*children):
    return Element(tag="ul", attributes=[], children=children)


def li(*children):
    return Element(tag="li", attributes=[], children=children)


def pre(*children):
    return Element(tag="pre", attributes=[], children=children)


def button(*children):
    return Element(tag="button", attributes=[], children=children)


def input_(*children):
    return Element(tag="input", attributes=[], children=children)


def _compileAction(action: Action):
    return [action.name, [_compile(arg) for arg in action.arguments]]


def _compileText(text: str):
    return ["text", text]


def _compileNumber(number: int):
    return ["number", number]


def _compileElement(elem: Element):
    for i, attr in enumerate(elem.attributes):
        if attr[1] == "action":
            elem.attributes[i][2] = [_compileAction(action) for action in attr[2]]
        elif attr[1] == "bind":
            elem.attributes[i][2] = _compileStateRef(attr[2])
    return [
        "elem",
        elem.tag,
        elem.attributes,
        [_compile(el) for el in elem.children],
    ]


def _compileStateRef(stateRef: StateRef):
    return ["stateRef", stateRef.label]


def _compileVarRef(varRef: VarRef):
    return ["varRef", varRef.label]


def _compileCondition(condition: Condition):
    left, right = condition.left, condition.right
    return [
        condition.name,
        (
            ["text", left]
            if isinstance(left, str)
            else ["number", left] if isinstance(left, int) else _compileStateRef(left)
        ),
        (
            ["text", right]
            if isinstance(right, str)
            else (
                ["number", right] if isinstance(right, int) else _compileStateRef(right)
            )
        ),
    ]


def _compileIf(if_: If):
    return [
        "if",
        _compileCondition(if_.condition),
        _compile(if_.consequent),
        _compile(if_.alternate or ""),
    ]


def _compileEach(each: Each):
    return ["each", _compile(each.list_), each.itemName, _compile(div(*each.template))]


def _compile(elem):
    if isinstance(elem, str):
        return _compileText(elem)
    if isinstance(elem, int):
        return _compileNumber(elem)
    if isinstance(elem, Element):
        return _compileElement(elem)
    if isinstance(elem, StateRef):
        return _compileStateRef(elem)
    if isinstance(elem, VarRef):
        return _compileVarRef(elem)
    if isinstance(elem, If):
        return _compileIf(elem)
    if isinstance(elem, Each):
        return _compileEach(elem)
    if isinstance(elem, list):
        return elem

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
