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

JS_TEMPLATE = """const root=document.getElementById("root");""" + \
    """$$$;function renderElement(e){if("text"===e[0])return""" + \
    """ document.createTextNode(e[1]);let t=document.createE""" + \
    """lement(e[0]);for(let o of e[2])t.appendChild(renderEl""" + \
    """ement(o));for(let o of e[1])t.setAttribute(o[0],o[1])""" + \
    """;return t}function renderRoute(){let e=document.locat""" + \
    """ion.hash.split("#")[1]||"/",t=site[e]||site["/error40""" + \
    """4"];for(let e of root.children)root.removeChild(e);ro""" + \
    """ot.appendChild(renderElement(t));}window.addEventList""" + \
    """ener("hashchange",renderRoute),window.addEventListene""" + \
    """r("load",renderRoute);"""

class Map(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def makeElement(tag, children):
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
    def type_(v): element.attributes.append(["type", v]); return element
    def name(v): element.attributes.append(["name", v]); return element
    def value(v): element.attributes.append(["value", v]); return element
    def method(v): element.attributes.append(["method", v]); return element
    def action(v): element.attributes.append(["action", v]); return element
    def for_(v): element.attributes.append(["for", v]); return element

    element = Map({
        "tag": tag,
        "attributes": [],
        "children": children,
        "atr": atr,
        "style": style,
        "class_": class_,
        "id_": id_,
        "href": href,
        "type_": type_,
        "name": name,
        "value": value,
        "method": method,
        "action": action,
        "for_": for_,
    })

    return element

def div(*children):    return makeElement("div",   children)
def p(*children):      return makeElement("p",     children)
def h1(*children):     return makeElement("h1",    children)
def h2(*children):     return makeElement("h2",    children)
def h3(*children):     return makeElement("h3",    children)
def img(*children):    return makeElement("img",   children)
def a(*children):      return makeElement("a",     children)
def br(*children):     return makeElement("br",    children)
def hr(*children):     return makeElement("hr",    children)
def ul(*children):     return makeElement("ul",    children)
def li(*children):     return makeElement("li",    children)
def span(*children):   return makeElement("span",  children)
def form(*children):   return makeElement("form",  children)
def table(*children):  return makeElement("table", children)
def tr(*children):     return makeElement("tr",    children)
def td(*children):     return makeElement("td",    children)
def input_(*children): return makeElement("input", children)
def label(*children):  return makeElement("label", children)
def pre(*children):    return makeElement("pre", children)

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

def makeRouter():
    def route(name, document):
        router[name] = document

    def generate():
        js_doc = _makeJSRouter(router)
        
        _template = JS_TEMPLATE.replace(
                "$$$", "const site = " + str(js_doc))

        out = Path(os.environ.get("CAMEL_OUT", ".")) / "camel.js"

        with open(out, "w") as f:
            f.write(_template)

        return js_doc

    router = Map({
        "route": route,
        "generate": generate
    })

    return router

