from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import pytest
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from camel.cli import SpaFileHandler, build, init


def _write_page(path: Path, tag: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f'from camel.dsl import Elem\npage = Elem("{tag}")\n')


def test_build_writes_a_site_for_a_single_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")

    build()

    build_dir = tmp_path / "build"
    assert (build_dir / "_camel" / "site.js").exists()
    assert (build_dir / "_camel" / "style.css").exists()
    assert (build_dir / "_camel" / "runtime.js").exists()
    assert (build_dir / "index.html").exists()
    assert (build_dir / "404.html").exists()


def test_build_compiles_every_discovered_page(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    _write_page(tmp_path / "src" / "pages" / "about" / "app.py", "p")

    build()

    site_js = (tmp_path / "build" / "_camel" / "site.js").read_text()
    assert '"/"' in site_js
    assert '"/about"' in site_js


def test_build_does_not_write_a_shell_per_route(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    _write_page(tmp_path / "src" / "pages" / "about" / "app.py", "p")

    build()

    assert not (tmp_path / "build" / "about").exists()


def test_build_copies_static_assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "favicon.ico").write_bytes(b"\x00")

    build()

    assert (tmp_path / "build" / "favicon.ico").exists()


def test_build_404_mirrors_index_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")

    build()

    build_dir = tmp_path / "build"
    assert (build_dir / "404.html").read_text() == (
        build_dir / "index.html"
    ).read_text()


def test_build_static_index_html_overrides_the_generated_shell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html>custom shell</html>")

    build()

    assert (
        tmp_path / "build" / "index.html"
    ).read_text() == "<html>custom shell</html>"


def test_build_404_mirrors_a_static_index_html_override(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # Regression test: build/404.html is derived from the final index.html,
    # written after the static/ overlay - not from write_site's default
    # shell - so an override doesn't leave 404.html stale.
    monkeypatch.chdir(tmp_path)
    _write_page(tmp_path / "src" / "pages" / "app.py", "h1")
    static_dir = tmp_path / "static"
    static_dir.mkdir()
    (static_dir / "index.html").write_text("<html>custom shell</html>")

    build()

    build_dir = tmp_path / "build"
    assert (build_dir / "404.html").read_text() == "<html>custom shell</html>"


def test_build_exits_if_src_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit):
        build()

    assert "src" in capsys.readouterr().err


def test_build_exits_if_pages_dir_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
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
    assert not (tmp_path / "build" / "_camel" / "site.js").exists()


def test_init_scaffolds_the_expected_tree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)

    init()

    assert (tmp_path / "pyproject.toml").exists()
    assert (tmp_path / "src" / "pages" / "app.py").exists()
    assert (tmp_path / "src" / "components").is_dir()
    assert (tmp_path / "static").is_dir()


def test_init_scaffolds_a_page_that_builds_successfully(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.chdir(tmp_path)

    init()
    build()

    assert (tmp_path / "build" / "_camel" / "site.js").exists()


def test_init_refuses_when_the_directory_is_not_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys
):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "notes.txt").write_text("unrelated")

    with pytest.raises(SystemExit):
        init()

    assert "not empty" in capsys.readouterr().err
    assert not (tmp_path / "pyproject.toml").exists()


class TestSpaFileHandler(AsyncHTTPTestCase):
    """SpaFileHandler is what makes `cml watch` behave like a host
    configured for SPA fallback. `livereload.Server.serve(root="build",
    ...)` passes that root as a relative path, not absolute - the handler
    has to resolve a fallback path correctly under that condition too, so
    the test reproduces it with a relative `path` rather than an absolute
    tmp_path, via a real Tornado Application/AsyncHTTPTestCase instead of
    camel.cli.watch() itself (which blocks forever serving real sockets and
    touches livereload's shared watcher state - unrelated to this fix)."""

    def setUp(self):
        self._orig_cwd = os.getcwd()
        self._tmp_dir = tempfile.mkdtemp()
        os.chdir(self._tmp_dir)
        os.makedirs("build/_camel")
        Path("build/index.html").write_text("SHELL")
        Path("build/_camel/site.js").write_text("ASSET")
        super().setUp()

    def tearDown(self):
        super().tearDown()
        os.chdir(self._orig_cwd)
        shutil.rmtree(self._tmp_dir, ignore_errors=True)

    def get_app(self):
        return Application(
            [
                (
                    r"/(.*)",
                    SpaFileHandler,
                    {"path": "build", "default_filename": "index.html"},
                )
            ]
        )

    def test_serves_a_real_file_normally(self):
        response = self.fetch("/_camel/site.js")
        assert response.code == 200
        assert response.body == b"ASSET"

    def test_falls_back_to_the_shell_for_an_unmatched_route(self):
        response = self.fetch("/about")
        assert response.code == 200
        assert response.body == b"SHELL"

    def test_falls_back_to_the_shell_for_a_nested_unmatched_route(self):
        response = self.fetch("/foo/bar")
        assert response.code == 200
        assert response.body == b"SHELL"

    def test_falls_back_to_the_shell_for_a_missing_asset(self):
        # Same trade-off a host's SPA-fallback rewrite rule has: it can't
        # tell a client-side route from a genuinely missing file either.
        response = self.fetch("/missing.png")
        assert response.code == 200
        assert response.body == b"SHELL"
