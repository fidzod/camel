from __future__ import annotations

from pathlib import Path

import pytest

from camel.dsl import Elem
from camel.route import DEFAULT_404, PageError, load_pages


def _write_page(path: Path, tag: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'from camel.dsl import Elem\npage = Elem("{tag}")\n')


def _write_dynamic_page(path: Path, values: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "from camel.dsl import Elem\n"
        f"def paths():\n    return {values!r}\n"
        "def page(value):\n    return Elem('h1') > value\n"
    )


def test_load_pages_injects_a_default_404_when_none_is_defined(tmp_path: Path):
    _write_page(tmp_path / "app.py", "h1")
    routes = load_pages(tmp_path)
    assert routes["/404"] == DEFAULT_404


def test_load_pages_keeps_a_user_defined_404_page(tmp_path: Path):
    _write_page(tmp_path / "app.py", "h1")
    _write_page(tmp_path / "404" / "app.py", "p")
    routes = load_pages(tmp_path)
    assert routes["/404"] == Elem("p")


def test_load_pages_builds_one_route_per_path_value(tmp_path: Path):
    _write_dynamic_page(tmp_path / "docs" / "[slug]" / "app.py", ["a", "b"])
    routes = load_pages(tmp_path)
    assert routes["/docs/a"] == (Elem("h1") > "a")
    assert routes["/docs/b"] == (Elem("h1") > "b")
    assert "/docs/[slug]" not in routes


def test_load_pages_dynamic_page_coexists_with_static_sibling(tmp_path: Path):
    _write_page(tmp_path / "docs" / "app.py", "h1")
    _write_dynamic_page(tmp_path / "docs" / "[slug]" / "app.py", ["a"])
    routes = load_pages(tmp_path)
    assert routes["/docs"] == Elem("h1")
    assert routes["/docs/a"] == (Elem("h1") > "a")


def test_load_pages_empty_paths_contributes_no_routes(tmp_path: Path):
    _write_page(tmp_path / "app.py", "h1")
    _write_dynamic_page(tmp_path / "docs" / "[slug]" / "app.py", [])
    routes = load_pages(tmp_path)
    assert not any(route.startswith("/docs") for route in routes)


def test_load_pages_rejects_a_bracket_dir_without_paths(tmp_path: Path):
    path = tmp_path / "docs" / "[slug]" / "app.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "from camel.dsl import Elem\n" "def page(slug):\n    return Elem('h1')\n"
    )
    with pytest.raises(ExceptionGroup) as excinfo:
        load_pages(tmp_path)
    assert all(isinstance(e, PageError) for e in excinfo.value.exceptions)


def test_load_pages_rejects_paths_on_a_non_bracket_dir(tmp_path: Path):
    _write_dynamic_page(tmp_path / "docs" / "app.py", ["a", "b", "c"])
    with pytest.raises(ExceptionGroup) as excinfo:
        load_pages(tmp_path)
    assert all(isinstance(e, PageError) for e in excinfo.value.exceptions)
