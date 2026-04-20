import argparse
import os
from livereload import Server
import shutil
import subprocess
from pathlib import Path

def watch():
    build()
    server = Server()
    server.watch("src", build)
    server.serve(root="build", port=5000)

def build():
    root = Path(__file__).parent.parent
    src = root / "src"
    build = root / "build"
    static = src / "static"
    app = src / "app.py"

    build.mkdir(exist_ok=True)

    if static.exists():
        shutil.copytree(static, build, dirs_exist_ok=True)

    env = os.environ.copy()
    env["CAMEL_OUT"] = str(build)

    result = subprocess.run(
        ["python", str(app)], env=env, capture_output=True, text=True
    )

    if result.returncode != 0:
        print(result.stdout)  # DEBUG
        print(result.stderr)
        raise SystemExit(1)

    if result.stdout:
        print(result.stdout)  # DEBUG

    print("🐪✨ Build successful!")

def format_():
    subprocess.run(["black", "src/"], check=True)

def main():
    parser = argparse.ArgumentParser(prog="cml")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build")
    subparsers.add_parser("watch")
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

