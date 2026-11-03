from __future__ import annotations

from pathlib import Path

from camel.dsl import Elem
from camel.route import DEFAULT_404, load_pages


def _write_page(path: Path, tag: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'from camel.dsl import Elem\npage = Elem("{tag}")\n')


def test_load_pages_injects_a_default_404_when_none_is_defined(tmp_path: Path):
    _write_page(tmp_path / "app.py", "h1")
    routes = load_pages(tmp_path)
    assert routes["/404"] == DEFAULT_404


def test_load_pages_keeps_a_user_defined_404_page(tmp_path: Path):
    _write_page(tmp_path / "app.py", "h1")
    _write_page(tmp_path / "404" / "app.py", "p")
    routes = load_pages(tmp_path)
    assert routes["/404"] == Elem("p")
