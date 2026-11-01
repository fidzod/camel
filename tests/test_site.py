from __future__ import annotations

from pathlib import Path

import pytest

from camel.dsl import Elem
from camel.site import generate


@pytest.fixture
def out_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("CAMEL_OUT", str(tmp_path))
    return tmp_path


def test_generate_writes_site_js(out_dir: Path):
    generate(Elem("p"))
    assert (out_dir / "site.js").read_text().startswith("const site = ")


def test_generate_copies_runtime_js_and_index_html(out_dir: Path):
    generate(Elem("p"))
    assert (out_dir / "runtime.js").exists()
    assert (out_dir / "index.html").exists()


def test_generate_links_the_stylesheet_in_index_html(out_dir: Path):
    generate(Elem("p"))
    assert (
        '<link rel="stylesheet" href="style.css">'
        in (out_dir / "index.html").read_text()
    )


def test_generate_writes_an_empty_stylesheet_when_tree_has_no_style_scopes(
    out_dir: Path,
):
    generate(Elem("div") > Elem("p"))
    assert (out_dir / "style.css").read_text() == ""


def test_generate_writes_css_for_a_style_scope(out_dir: Path):
    scope = Elem("p").style({"p": {"color": "red"}})
    generate(scope)
    assert (out_dir / "style.css").read_text() == (
        f'p[data-scope~="{scope.id}"] {{\n\tcolor: red;\n}}'
    )


def test_generate_creates_the_out_dir_if_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    nested = tmp_path / "a" / "b"
    monkeypatch.setenv("CAMEL_OUT", str(nested))
    generate(Elem("p"))
    assert (nested / "site.js").exists()
