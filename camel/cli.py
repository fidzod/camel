import argparse
import os
import subprocess
import sys
from pathlib import Path

from livereload import Server


def watch(app: str):
    build(app)
    server = Server()
    server.watch(app, lambda: build(app))
    server.serve(root="build", port=5000)


def build(app: str):
    build_dir = Path.cwd() / "build"
    build_dir.mkdir(exist_ok=True)

    env = os.environ.copy()
    env["CAMEL_OUT"] = str(build_dir)

    result = subprocess.run(
        [sys.executable, app], env=env, capture_output=True, text=True
    )

    if result.returncode != 0:
        print(result.stdout)
        print("Build failed with errors:\n")
        print(result.stderr)
        raise SystemExit(1)

    if result.stdout:
        print(result.stdout)

    print("🐪✨ Build successful!")


def format_():
    subprocess.run(["black", "."], check=True)


def main():
    parser = argparse.ArgumentParser(prog="cml")
    subparsers = parser.add_subparsers(dest="command")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("app")

    watch_parser = subparsers.add_parser("watch")
    watch_parser.add_argument("app")

    subparsers.add_parser("format")

    args = parser.parse_args()

    if args.command == "build":
        build(args.app)
    elif args.command == "watch":
        watch(args.app)
    elif args.command == "format":
        format_()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
