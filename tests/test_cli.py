from __future__ import annotations

from pathlib import Path

import pytest

from camel.cli import build


def _write_page(path: Path, tag: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'from camel.dsl import Elem\npage = Elem("{tag}")\n')


def test_build_writes_a_site_for_a_single_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")

    build()

    build_dir = tmp_path / "build"
    assert (build_dir / "site.js").exists()
    assert (build_dir / "style.css").exists()
    assert (build_dir / "runtime.js").exists()
    assert (build_dir / "index.html").exists()


def test_build_compiles_every_discovered_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    _write_page(tmp_path / "src" / "pages" / "about" / "app.py", "p")

    build()

    site_js = (tmp_path / "build" / "site.js").read_text()
    assert '"/"' in site_js
    assert '"/about"' in site_js


def test_build_copies_static_assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "favicon.ico").write_bytes(b"\x00")

    build()

    assert (tmp_path / "build" / "favicon.ico").exists()


def test_build_exits_if_src_is_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        build()

    assert "src" in capsys.readouterr().err


def test_build_exits_if_pages_dir_is_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "src").mkdir()

    with pytest.raises(SystemExit):
        build()

    assert "pages" in capsys.readouterr().err


def test_build_exits_and_reports_every_broken_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    monkeypatch.chdir(tmp_path)
    good = tmp_path / "src" / "pages" / "app.py"
    good.parent.mkdir(parents=True, exist_ok=True)
    good.write_text('from camel.dsl import Elem\npage = Elem("h1")\n')

    broken_missing_export = tmp_path / "src" / "pages" / "oops" / "app.py"
    broken_missing_export.parent.mkdir(parents=True, exist_ok=True)
    broken_missing_export.write_text("not_page = 1\n")

    broken_raises = tmp_path / "src" / "pages" / "boom" / "app.py"
    broken_raises.parent.mkdir(parents=True, exist_ok=True)
    broken_raises.write_text("raise NameError('typo')\n")

    with pytest.raises(SystemExit):
        build()

    err = capsys.readouterr().err
    assert "oops" in err
    assert "boom" in err
    assert not (tmp_path / "build" / "site.js").exists()
