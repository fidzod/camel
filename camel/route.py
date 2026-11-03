__all__ = ["load_pages", "PageError"]

import importlib.util
from pathlib import Path
import sys

from camel.dsl import Elem, Node

DEFAULT_404 = Elem("h1") > "404 - Page not found"


class PageError(Exception):
    """A single page module under pages_dir failed to load."""

    def __init__(self, path: Path, cause: Exception):
        super().__init__(f"{path}: {cause}")
        self.path = path


def _route_for(root: Path, path: Path) -> str:
    rel = path.parent.relative_to(root)
    return "/" + "/".join(rel.parts)


def _load_page(root: Path, path: Path) -> Node:
    rel = path.parent.relative_to(root)

    name = "page_" + "_".join(rel.parts or ("index",))
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    if (page := getattr(module, "page", None)) is None:
        raise ValueError("Missing page export")

    return page


def load_pages(root: Path) -> dict[str, Node]:
    pages: dict[str, Node] = {}
    errors: list[PageError] = []

    for path in sorted(root.rglob("app.py")):
        try:
            pages[_route_for(root, path)] = _load_page(root, path)
        except Exception as cause:
            errors.append(PageError(path, cause))

    if errors:
        raise ExceptionGroup("failed to load pages", errors)

    pages.setdefault("/404", DEFAULT_404)

    return pages
