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
import os
from pathlib import Path

class Map(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Element:
    def __init__(self, tag: str, *children: str | Element):
        self.tag = tag
        self.attributes = []
        self.children = children

    def attr(self, name, value):
        self.attributes.append([name, value])
        return self

    def style(self, atr: str, value: str) -> Element:
        style = f"{atr}: {value};"
        existing = next(
            (atr for atr in self.attributes if atr[0] == "style"), None)
        if existing:
            existing += f" {style}"
        else:
            self.attributes.append(["style", style])
        return self

    def class_(self, name: str) -> Element:
        existing = next(
            (atr for atr in self.attributes if atr[0] == "style"), None)
        if existing:
            existing[1] += f" {name}"
        else:
            self.attributes.append(["class", name])
        return self

    def id_(self, name: str) -> Element:
        self.attributes.append(["id", name])
        return self

    def href(self, name: str) -> Element:
        self.attributes.append(["href", name])
        return self

def div(*children): return Element("div", *children)
def h1(*children):  return Element("h1",  *children)
def h2(*children):  return Element("h2",  *children)
def h3(*children):  return Element("h3",  *children)
def p(*children):   return Element("p",   *children)
def a(*children):   return Element("a",   *children)
def ul(*children):  return Element("ul",  *children)
def li(*children):  return Element("li",  *children)
def pre(*children): return Element("pre", *children)

def _makeText(text):
    return ["text", text]

def _makeElem(elem):
    return [
        "elem",
        elem.tag,
        elem.attributes,
        [_makeJSElem(el) for el in elem.children]
    ]

def _makeJSElem(elem):
    if isinstance(elem, str): return _makeText(elem)
    if isinstance(elem, Element): return _makeElem(elem)

def _makeJSRouter(router):
    JSRouter = {}

    for key in router.keys():
        if isinstance(router[key], Element):
            JSRouter[key] = _makeJSElem(router[key])

    return JSRouter

def Router():
    def route(name, *document):
        router[name] = document[0] if len(document) == 1 else div(*document)

    def generate():
        js_doc = _makeJSRouter(router)
        
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

    router = Map({
        "route": route,
        "generate": generate
    })

    return router

