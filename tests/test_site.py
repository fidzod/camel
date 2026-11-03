from __future__ import annotations

import json
from pathlib import Path

from camel.dsl import Elem
from camel.site import write_site


def _read_site(out: Path) -> dict:
    text = (out / "site.js").read_text()
    assert text.startswith("const site = ")
    assert text.endswith(";")
    return json.loads(text.removeprefix("const site = ").removesuffix(";"))


def test_write_site_writes_site_js(tmp_path: Path):
    write_site({"/": Elem("p")}, tmp_path)
    assert (tmp_path / "site.js").read_text().startswith("const site = ")


def test_write_site_keys_the_bundle_by_route(tmp_path: Path):
    write_site({"/": Elem("p"), "/about": Elem("h1")}, tmp_path)
    site = _read_site(tmp_path)
    assert set(site) == {"/", "/about"}
    assert site["/"]["tag"] == "p"
    assert site["/about"]["tag"] == "h1"


def test_write_site_copies_runtime_js_and_index_html(tmp_path: Path):
    write_site({"/": Elem("p")}, tmp_path)
    assert (tmp_path / "runtime.js").exists()
    assert (tmp_path / "index.html").exists()


def test_write_site_links_assets_by_absolute_path_in_index_html(tmp_path: Path):
    write_site({"/": Elem("p")}, tmp_path)
    html = (tmp_path / "index.html").read_text()
    assert '<link rel="stylesheet" href="/style.css">' in html
    assert '<script src="/site.js"></script>' in html
    assert '<script src="/runtime.js"></script>' in html


def test_write_site_writes_an_empty_stylesheet_when_no_pages_have_style_scopes(
    tmp_path: Path,
):
    write_site({"/": Elem("div") > Elem("p")}, tmp_path)
    assert (tmp_path / "style.css").read_text() == ""


def test_write_site_writes_css_for_a_style_scope(tmp_path: Path):
    scope = Elem("p").style({"p": {"color": "red"}})
    write_site({"/": scope}, tmp_path)
    assert (tmp_path / "style.css").read_text() == (
        f'p[data-scope~="{scope.id}"] {{\n\tcolor: red;\n}}'
    )


def test_write_site_combines_css_across_multiple_pages(tmp_path: Path):
    home = Elem("p").style({"p": {"color": "red"}})
    about = Elem("h1").style({"h1": {"color": "blue"}})
    write_site({"/": home, "/about": about}, tmp_path)
    assert (tmp_path / "style.css").read_text() == "\n".join(
        [
            f'p[data-scope~="{home.id}"] {{\n\tcolor: red;\n}}',
            f'h1[data-scope~="{about.id}"] {{\n\tcolor: blue;\n}}',
        ]
    )


def test_write_site_combining_css_skips_pages_with_no_style_scopes(tmp_path: Path):
    scoped = Elem("p").style({"p": {"color": "red"}})
    plain = Elem("div") > Elem("p")
    write_site({"/": plain, "/about": scoped}, tmp_path)
    assert (tmp_path / "style.css").read_text() == (
        f'p[data-scope~="{scoped.id}"] {{\n\tcolor: red;\n}}'
    )


def test_write_site_creates_the_out_dir_if_missing(tmp_path: Path):
    nested = tmp_path / "a" / "b"
    write_site({"/": Elem("p")}, nested)
    assert (nested / "site.js").exists()


def test_write_site_writes_a_shell_at_every_routes_path(tmp_path: Path):
    write_site({"/": Elem("p"), "/about": Elem("p"), "/foo/bar": Elem("p")}, tmp_path)
    assert (tmp_path / "index.html").exists()
    assert (tmp_path / "about" / "index.html").exists()
    assert (tmp_path / "foo" / "bar" / "index.html").exists()


def test_write_site_shells_are_identical_across_routes(tmp_path: Path):
    write_site({"/": Elem("p"), "/about": Elem("p")}, tmp_path)
    assert (tmp_path / "index.html").read_text() == (
        tmp_path / "about" / "index.html"
    ).read_text()


def test_write_site_writes_only_one_copy_of_the_shared_assets(tmp_path: Path):
    write_site({"/": Elem("p"), "/about": Elem("p")}, tmp_path)
    assert not (tmp_path / "about" / "site.js").exists()
    assert not (tmp_path / "about" / "runtime.js").exists()
    assert not (tmp_path / "about" / "style.css").exists()


def test_write_site_writes_a_404_shell_identical_to_the_others(tmp_path: Path):
    write_site({"/": Elem("p"), "/404": Elem("h1")}, tmp_path)
    assert (tmp_path / "404.html").read_text() == (tmp_path / "index.html").read_text()
