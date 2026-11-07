import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Optional

from livereload import Server
from livereload.handlers import StaticFileHandler
from tornado.web import HTTPError

from camel.route import PageError, load_pages
from camel.site import write_site

INIT_APP_PY = """
from camel import *

page = h1 > "🐪 My Camel Site"
""".lstrip()

INIT_PYPROJECT_TOML = """
[project]
name = "my-camel-site"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["camel"]
""".lstrip()

INIT_IGNORE = {".DS_Store", ".git"}


class SpaFileHandler(StaticFileHandler):
    """Serves build/ like a host configured for SPA fallback: any path
    that isn't a real file resolves to the shell, not a 404."""

    def validate_absolute_path(self, root, absolute_path):
        try:
            return super().validate_absolute_path(root, absolute_path)
        except HTTPError as e:
            if e.status_code == 404:
                return super().validate_absolute_path(
                    root,
                    str(
                        (
                            Path(root) / (self.default_filename or "index.html")
                        ).absolute()
                    ),
                )
            raise


def _expect_exists(directory: Path, name: Optional[str] = None) -> None:
    if not directory.exists():
        sys.stderr.write(f"Could not find '{name or directory.name}'\n")
        raise SystemExit(1)


def build():
    build_dir = Path.cwd() / "build"
    build_dir.mkdir(exist_ok=True)

    src_dir = Path.cwd() / "src"
    _expect_exists(src_dir)

    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    pages_dir = src_dir / "pages"
    _expect_exists(pages_dir, "src/pages")

    try:
        routes = load_pages(pages_dir)
    except* PageError as eg:
        for error in eg.exceptions:
            sys.stderr.write(f"{error}\n")
        raise SystemExit(1)

    write_site(routes, build_dir)

    static = Path.cwd() / "static"
    if static.exists():
        shutil.copytree(static, build_dir, dirs_exist_ok=True)

    shutil.copy(build_dir / "index.html", build_dir / "404.html")

    print("🐪✨ Build successful!")


def format_():
    subprocess.run(["black", "."], check=True)


def init():
    cwd = Path.cwd()

    if any(p.name not in INIT_IGNORE for p in cwd.iterdir()):
        sys.stderr.write("Directory is not empty\n")
        raise SystemExit(1)

    (cwd / "src" / "pages").mkdir(parents=True)
    (cwd / "src" / "components").mkdir()
    (cwd / "static").mkdir()

    (cwd / "src" / "pages" / "app.py").write_text(INIT_APP_PY)
    (cwd / "pyproject.toml").write_text(INIT_PYPROJECT_TOML)

    print("🐪✨ You're all set!")
    print("Run: cml watch")


def watch():
    build()

    # Existence already confirmed in build
    src_dir = Path.cwd() / "src"

    server = Server()
    server.SFH = SpaFileHandler
    server.watch(src_dir, build)
    server.serve(root="build", port=5000)


def main():
    parser = argparse.ArgumentParser(prog="cml")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build")
    subparsers.add_parser("fmt")
    subparsers.add_parser("init")
    subparsers.add_parser("watch")

    args = parser.parse_args()

    match args.command:
        case "build":
            build()
        case "fmt":
            format_()
        case "init":
            init()
        case "watch":
            watch()
        case _:
            parser.print_help()


if __name__ == "__main__":
    main()
