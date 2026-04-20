"""
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
import os
from pathlib import Path

class Map(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def _makeElement(tag, children):
    def atr(name, value):
        element.attributes.append([name, value])
        return element

    def style(atr, value):
        style_atr = list(filter(
            lambda a: a[0] == "style", element.attributes))
        if style_atr:
            for i, atr_ in enumerate(element.attributes):
                if atr_[0] == "style":
                    element.attributes[i][1] += " {}: {};".format(
                        atr, value
                    )
        else:
            element.attributes.append(["style", "{}: {};".format(
                atr, value
            )])
        return element

    def class_(classname):
        class_atr = list(filter(
            lambda c: c[0] == "class", element.attributes))
        if class_atr:
            for i, cls_ in enumerate(element.attributes):
                if cls_[0] == "class":
                    element.attributes[i][1] += " " + classname
        else:
            element.attributes.append(["class", classname])
        return element

    def id_(v): element.attributes.append(["id", v]); return element
    def href(v): element.attributes.append(["href", v]); return element

    element = Map({
        "tag": tag,
        "attributes": [],
        "children": children,
        "atr": atr,
        "style": style,
        "class_": class_,
        "id_": id_,
        "href": href,
    })

    return element

def div(*children): return _makeElement("div", children)
def h1(*children):  return _makeElement("h1",  children)
def h2(*children):  return _makeElement("h2",  children)
def h3(*children):  return _makeElement("h3",  children)
def p(*children):   return _makeElement("p",   children)
def a(*children):   return _makeElement("a",   children)
def ul(*children):  return _makeElement("ul",  children)
def li(*children):  return _makeElement("li",  children)
def pre(*children): return _makeElement("pre", children)

def _makeJSElem(elem):
    if isinstance(elem, str):
        return ["text", elem]

    return [
        elem.tag,
        elem.attributes,
        [_makeJSElem(el) for el in elem.children]
    ]

def _makeJSRouter(router):
    JSRouter = {}

    for key in router.keys():
        if isinstance(router[key], Map):
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

