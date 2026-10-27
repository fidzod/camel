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

from functools import singledispatch


class Node:
    def __add__(self, sibling: any):
        return Container(self, sibling)

    def __radd__(self, sibling: any):
        return Container(sibling, self)


class Elem(Node):
    def __init__(self, tag: str, class_list: list = None, children: list = None):
        self.tag = tag
        self.children = list(children) if children else []
        self.class_list = list(class_list) if class_list else []

    def compile(self):
        return {
            "type": "Elem",
            "tag": self.tag,
            "class_list": self.class_list,
            "children": list(map(compile, self.children)),
        }

    def _derived(self, class_list=None, children=None):
        return Elem(self.tag, class_list or self.class_list, children or self.children)

    def __gt__(self, child: any):
        return self._derived(children=self.children + [child])

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name) from None
        return self._derived(class_list=self.class_list + [name])


def _flatten(items):
    for item in items:
        if isinstance(item, Container):
            yield from _flatten(item.children)
        else:
            yield item


class Container(Node):
    def __init__(self, *args):
        self.children = list(_flatten(args))

    def compile(self):
        return {"type": "Container", "children": list(map(compile, self.children))}


@singledispatch
def compile(node):
    raise TypeError(f"don't know how to compile {type(node)!r}")


@compile.register
def _(node: str):
    return {"type": "Text", "contents": node}


@compile.register
def _(node: "Node"):
    return node.compile()


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
