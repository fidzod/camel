import argparse
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Optional

from livereload import Server

from camel.route import PageError, load_pages
from camel.site import write_site


def _expect_exists(directory: Path, name: Optional[str] = None) -> None:
    if not directory.exists():
        sys.stderr.write(f"Could not find '{name or directory.name}'\n")
        raise SystemExit(1)


def watch():
    build()

    # Existence already confirmed in build
    src_dir = Path.cwd() / "src"

    server = Server()
    server.watch(src_dir, build)
    server.serve(root="build", port=5000)


def build():
    build_dir = Path.cwd() / "build"
    build_dir.mkdir(exist_ok=True)

    src_dir = Path.cwd() / "src"
    _expect_exists(src_dir)

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

    print("🐪✨ Build successful!")


def format_():
    subprocess.run(["black", "."], check=True)


def main():
    parser = argparse.ArgumentParser(prog="cml")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build")

    watch_parser = subparsers.add_parser("watch")

    subparsers.add_parser("format")

    args = parser.parse_args()

    if args.command == "build":
        build()
    elif args.command == "watch":
        watch()
    elif args.command == "format":
        format_()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
