from __future__ import annotations

from camel.css import ScopedRules, _collect_styles, to_css
from camel.dsl import Elem, Empty, Let, PartialIf, StateRef


def _rules(node) -> list[ScopedRules]:
    return list(_collect_styles(node))


def test_collect_styles_finds_nothing_without_a_style_scope():
    assert _rules(Elem("div") > Elem("p")) == []


def test_collect_styles_finds_nothing_in_a_leaf_node():
    assert _rules(Empty()) == []
    assert _rules("hello") == []


def test_collect_styles_finds_a_style_scope_inside_an_elem():
    scope = Elem("p").style({"p": {"color": "red"}})
    tree = Elem("div") > scope
    assert _rules(tree) == [(scope.id, scope.rules)]


def test_collect_styles_finds_a_style_scope_inside_a_fragment():
    scope = Elem("p").style({"p": {"color": "red"}})
    tree = Elem("div") + scope
    assert _rules(tree) == [(scope.id, scope.rules)]


def test_collect_styles_finds_a_style_scope_inside_state():
    scope = Elem("p").style({"p": {"color": "red"}})
    tree = Let((("x", 0),)).in_(scope)
    assert _rules(tree) == [(scope.id, scope.rules)]


def test_collect_styles_finds_a_style_scope_in_an_ifs_then_branch():
    scope = Elem("p").style({"p": {"color": "red"}})
    built = PartialIf(StateRef("x") == 1).then(scope).otherwise(Elem("span"))
    assert _rules(built) == [(scope.id, scope.rules)]


def test_collect_styles_finds_a_style_scope_in_an_ifs_otherwise_branch():
    # Regression: the If registration once read `if_.otherwise` (the
    # method that builds a new If) instead of `if_.otherwise_` (the
    # field), so anything styled only in the otherwise branch was
    # silently dropped - no exception, it just vanished.
    scope = Elem("span").style({"span": {"color": "red"}})
    built = PartialIf(StateRef("x") == 1).then(Elem("p")).otherwise(scope)
    assert _rules(built) == [(scope.id, scope.rules)]


def test_collect_styles_finds_a_style_scope_inside_a_foreach_body():
    scope = Elem("li").style({"li": {"color": "red"}})
    tree = StateRef("items").each(lambda item: scope)
    assert _rules(tree) == [(scope.id, scope.rules)]


def test_collect_styles_finds_nested_style_scopes():
    inner = Elem("p").style({"p": {"color": "red"}})
    outer = (Elem("div") > inner).style({"div": {"margin": "0"}})
    assert _rules(outer) == [(outer.id, outer.rules), (inner.id, inner.rules)]


def test_collect_styles_finds_sibling_style_scopes():
    s1 = Elem("p").style({"p": {"color": "red"}})
    s2 = Elem("span").style({"span": {"color": "blue"}})
    tree = s1 + s2
    assert _rules(tree) == [(s1.id, s1.rules), (s2.id, s2.rules)]


def test_to_css_of_empty_input_is_empty_string():
    assert to_css([]) == ""


def test_to_css_formats_one_rule_block_per_selector():
    scope = Elem("p").style({"p": {"color": "red", "font-weight": "bold"}})
    css = to_css([(scope.id, scope.rules)])
    assert css == (
        f'p[data-scope~="{scope.id}"] {{\n'
        "\tcolor: red;\n"
        "\tfont-weight: bold;\n"
        "}"
    )


def test_to_css_emits_a_block_per_selector_across_multiple_scopes():
    scope1 = Elem("p").style({"p": {"color": "red"}})
    scope2 = Elem("span").style({"span": {"color": "blue"}, "a": {"color": "green"}})
    css = to_css([(scope1.id, scope1.rules), (scope2.id, scope2.rules)])
    assert css == (
        f'p[data-scope~="{scope1.id}"] {{\n'
        "\tcolor: red;\n"
        "}\n"
        f'span[data-scope~="{scope2.id}"] {{\n'
        "\tcolor: blue;\n"
        "}\n"
        f'a[data-scope~="{scope2.id}"] {{\n'
        "\tcolor: green;\n"
        "}"
    )


def test_collect_styles_then_to_css_end_to_end():
    scope = (Elem("ul") > Elem("li")).style({"li": {"font-weight": "bold"}})
    css = to_css(_collect_styles(scope))
    assert css == f'li[data-scope~="{scope.id}"] {{\n\tfont-weight: bold;\n}}'
