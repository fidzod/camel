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

from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from typing import Callable, Any, Optional


class Serialisable:
    def __call__(self) -> dict:
        raise NotImplementedError


class Renderable(Serialisable):
    @classmethod
    def make(cls, item: Any) -> Renderable:
        if isinstance(item, Renderable):
            return item
        if isinstance(item, str):
            return Text.make(item)
        if isinstance(item, int):
            return Number.make(item)
        raise TypeError(f"Cannot make Renderable from {type(item).__name__}")

    def __call__(self) -> dict:
        raise NotImplementedError


class Primitive(Renderable):
    @classmethod
    def make(cls, item: Any) -> Primitive:
        if isinstance(item, Primitive):
            return item
        if isinstance(item, str):
            return Text.make(item)
        if isinstance(item, int):
            return Number.make(item)
        if isinstance(item, list):
            return List.make(item)
        raise TypeError(f"Cannot make Primitive from {type(item).__name__}")

    def __call__(self) -> dict:
        raise NotImplementedError


@dataclass
class List(Primitive):
    items: list

    @classmethod
    def make(cls, item: list[int | str]) -> List:
        return List(items=[Primitive.make(p) for p in item])

    def __call__(self):
        return {"type": "List", "value": [p() for p in self.items]}


@dataclass
class Number(Primitive):
    number: int

    @classmethod
    def make(cls, item: int) -> Number:
        return Number(number=item)

    def __call__(self):
        return {"type": "Number", "value": self.number}


@dataclass
class Text(Primitive):
    text: str

    @classmethod
    def make(cls, item: str) -> Text:
        return Text(text=item)

    def __call__(self):
        return {"type": "Text", "value": self.text}


@dataclass
class StateRef(Primitive):
    label: str = ""

    def __getattr__(self, label: str) -> StateRef:
        return StateRef(label=f"{self.label}.{label}")

    def __call__(self):
        return {"type": "StateRef", "label": self.label}


class StateProxy:
    def __getattr__(self, label: str) -> StateRef:
        return StateRef(label=label)


state = StateProxy()


@dataclass
class VarRef(Primitive):
    label: str

    def __getattr__(self, label: str) -> VarRef:
        return VarRef(label=f"{self.label}.{label}")

    def __call__(self):
        return {"type": "VarRef", "label": self.label}


class VarProxy:
    def __getattr__(self, label: str) -> VarRef:
        return VarRef(label=label)


var = VarProxy()


@dataclass
class Fetch(Primitive):
    url: str

    def __call__(self):
        return {"type": "Fetch", "url": self.url}


def fetch(*partialUrl: str) -> Fetch:
    return Fetch(url="/".join(list(partialUrl)))


@dataclass
class Action(Serialisable):
    name: str
    arguments: list[Primitive]

    def __call__(self):
        return {
            "type": "Action",
            "name": self.name,
            "arguments": [Primitive.make(a)() for a in self.arguments],
        }


increment = lambda x: Action(name="increment", arguments=[x])
push = lambda l, x: Action(name="push", arguments=[l, x])
set_ = lambda sr, x: Action(name="set", arguments=[sr, x])
remove = lambda l, x: Action(name="remove", arguments=[l, x])
delete = lambda *url: Action(name="delete", arguments=list(url))
post = lambda *url, **body: Action(
    name="post", arguments=list(url) + [[k, body[k]] for k in body.keys()] + [len(url)]
)


@dataclass
class Event(Serialisable):
    name: str
    actions: list[Action]

    def __call__(self):
        return {
            "type": "Event",
            "name": self.name,
            "actions": [a() for a in self.actions],
        }


@dataclass
class Element(Renderable):
    tag: str
    children: list[Renderable]
    events: list[Event] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    class_list: list[str] = field(default_factory=list)
    bound_to: Optional[StateRef] = None

    def __call__(self):
        element = {
            "type": "Element",
            "tag": self.tag,
            "children": [Renderable.make(c)() for c in self.children],
            "attributes": self.attributes,
            "events": [e() for e in self.events],
            "classes": " ".join(self.class_list),
            "boundTo": None if self.bound_to is None else self.bound_to(),
        }
        return element

    def on_click(self, *actions: Action) -> Element:
        self.events.append(Event(name="click", actions=list(actions)))
        return self

    def bind(self, stateRef: StateRef) -> Element:
        self.bound_to = stateRef
        return self

    def attr(self, **attrs: str) -> Element:
        self.attributes |= attrs
        return self

    def cls(self, class_name: str) -> Element:
        self.class_list.append(class_name)
        return self

    def style(self, atrName: str, atrValue: str) -> Element:
        if self.attributes.get("style") is None:
            self.attr(style="")
        self.attributes["style"] += f"{atrName}: {atrValue};"
        return self

    def placeholder(self, value: str) -> Element:
        return self.attr(placeholder=value)


h1 = lambda *children: Element(tag="h1", children=list(children))
h2 = lambda *children: Element(tag="h2", children=list(children))
h3 = lambda *children: Element(tag="h3", children=list(children))
h4 = lambda *children: Element(tag="h4", children=list(children))
h5 = lambda *children: Element(tag="h5", children=list(children))
h6 = lambda *children: Element(tag="h6", children=list(children))
p = lambda *children: Element(tag="p", children=list(children))
span = lambda *children: Element(tag="span", children=list(children))
div = lambda *children: Element(tag="div", children=list(children))
ul = lambda *children: Element(tag="ul", children=list(children))
li = lambda *children: Element(tag="li", children=list(children))
button = lambda *children: Element(tag="button", children=list(children))
input_ = lambda **attrs: Element(tag="input", children=[], attributes=attrs)


@dataclass
class Condition:
    name: str
    x: Primitive
    y: Optional[Primitive] = None

    def __call__(self):
        return {
            "type": "Condition",
            "name": self.name,
            "x": Primitive.make(self.x)(),
            "y": None if self.y is None else Primitive.make(self.y)(),
        }


eq = lambda x, y: Condition(name="eq", x=x, y=y)
gt = lambda x, y: Condition(name="gt", x=x, y=y)
gte = lambda x, y: Condition(name="gte", x=x, y=y)
lt = lambda x, y: Condition(name="lt", x=x, y=y)
lte = lambda x, y: Condition(name="lte", x=x, y=y)


@dataclass
class If(Renderable):
    condition: Condition
    consequent: Renderable
    alternate: Optional[Renderable] = None

    def then(self, consequent: Renderable) -> If:
        self.consequent = consequent
        return self

    def else_(self, alternate: Renderable) -> If:
        self.alternate = alternate
        return self

    def __call__(self):
        return {
            "type": "If",
            "condition": self.condition(),
            "consequent": self.consequent(),
            "alternate": None if self.alternate is None else self.alternate(),
        }


def if_(condition: Condition) -> If:
    return If(condition=condition, consequent=span("True"))


@dataclass
class ForEach(Renderable):
    list_: List | StateRef
    var: str
    body: Renderable

    def __call__(self):
        return {
            "type": "ForEach",
            "list": self.list_(),
            "var": self.var,
            "body": self.body(),
        }


@dataclass
class ForEachPartial:
    list_: List | StateRef
    var: str = "item"

    def as_(self, var: str) -> ForEachPartial:
        self.var = var
        return self

    def __call__(self, body: Renderable) -> ForEach:
        return ForEach(list_=self.list_, var=self.var, body=body)


def for_each(list_: StateRef | list[str | int]) -> ForEachPartial:
    return ForEachPartial(
        list_=list_ if isinstance(list_, StateRef) else List.make(list_)
    )


@dataclass
class Route:
    tree: list[Renderable]
    state: dict[str, Primitive] = field(default_factory=dict)

    def __call__(self):
        return {
            "tree": [atom() for atom in self.tree],
            "state": {k: v() for k, v in self.state.items()},
        }

    def use_state(self, **stateVars: int | str | list[int | str] | Fetch) -> Route:
        for k, v in stateVars.items():
            self.state[k] = Primitive.make(v)
        return self


class Router:
    def __init__(self):
        self.routes: dict[str, Route] = {}

    def route(self, name: str) -> Callable[..., Route]:
        def inner(*children: Renderable):
            r = Route(tree=list(children))
            self.routes[name] = r
            return r

        return inner

    def generate(self) -> None:
        site = f"const site = {json.dumps(self())};"
        site_out = Path(os.environ.get("CAMEL_OUT", ".")) / "site.js"

        with open(site_out, "w") as f:
            f.write(site)

        runtime_file = Path(__file__).parent / "runtime.js"
        runtime_out = Path(os.environ.get("CAMEL_OUT", ".")) / "runtime.js"

        with open(runtime_file, "r") as f_in:
            with open(runtime_out, "w") as f_out:
                f_out.write(f_in.read())

    def __call__(self):
        return {k: v() for k, v in self.routes.items()}
