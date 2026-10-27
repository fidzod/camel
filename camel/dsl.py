__all__ = ["Node", "Elem", "Container"]


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
