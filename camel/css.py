__all__ = ["to_css"]

from collections.abc import Iterable, Iterator
from functools import singledispatch

from camel.dsl import Elem, ForEach, Fragment, If, Node, Rules, State, StyleScope

type ScopedRules = tuple[str, Rules]


@singledispatch
def _collect_styles(node: Node) -> Iterator[ScopedRules]:
    return iter(())  # most nodes have no rules of their own


@_collect_styles.register
def _(elem: Elem) -> Iterator[ScopedRules]:
    for child in elem.children:
        yield from _collect_styles(child)


@_collect_styles.register
def _(fragment: Fragment) -> Iterator[ScopedRules]:
    for child in fragment.children:
        yield from _collect_styles(child)


@_collect_styles.register
def _(state: State) -> Iterator[ScopedRules]:
    yield from _collect_styles(state.child)


@_collect_styles.register
def _(if_: If) -> Iterator[ScopedRules]:
    yield from _collect_styles(if_.then)
    yield from _collect_styles(if_.otherwise_)


@_collect_styles.register
def _(each: ForEach) -> Iterator[ScopedRules]:
    yield from _collect_styles(each.body)


@_collect_styles.register
def _(scope: StyleScope) -> Iterator[ScopedRules]:
    yield (scope.id, scope.rules)
    yield from _collect_styles(scope.child)


def to_css(tree: Node) -> str:
    return _to_css(_collect_styles(tree))


def _to_css(scoped_rules: Iterable[ScopedRules]) -> str:
    # fmt: off
    return "\n".join(
        [
            f"""{selector}[data-scope~="{scope_id}"] {{\n{
                "\n".join(
                    [f"\t{prop}: {value};" for prop, value in declarations]
                )
            }\n}}"""
            for scope_id, rules in scoped_rules
            for selector, declarations in rules
        ]
    )
    # fmt: on
