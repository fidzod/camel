__all__ = ["load_pages", "PageError"]

import importlib.util
from pathlib import Path
import re
import sys

from camel.dsl import Elem, Node

DEFAULT_404 = Elem("h1") > "404 - Page not found"

_BRACKET = re.compile(r"^\[(\w+)\]$")


class PageError(Exception):
    """A single page module under pages_dir failed to load."""

    def __init__(self, path: Path, cause: Exception):
        super().__init__(f"{path}: {cause}")
        self.path = path


def _resolve(template: str, value: str) -> str:
    parts = template.split("/")
    parts = [value if _BRACKET.match(p) else p for p in parts]
    return "/".join(parts)


def _load_page(root: Path, path: Path) -> dict[str, Node]:
    rel = path.parent.relative_to(root)
    is_dynamic = bool(rel.parts) and _BRACKET.match(rel.parts[-1])

    name = "page_" + "_".join(rel.parts or ("index",))
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    has_paths = hasattr(module, "paths")

    if is_dynamic and not has_paths:
        raise ValueError(f"'{rel.parts[-1]}' must export paths()")
    if has_paths and not is_dynamic:
        raise ValueError("paths() expor from static route")

    if is_dynamic:
        if not callable(page := getattr(module, "page", None)):
            raise ValueError("Expected callable page export")
        template = "/" + "/".join(rel.parts)
        return {
            _resolve(template, value): module.page(value) for value in module.paths()
        }
    else:
        if (page := getattr(module, "page", None)) is None:
            raise ValueError("Missing page export")
        return {"/" + "/".join(rel.parts): module.page}


def load_pages(root: Path) -> dict[str, Node]:
    pages: dict[str, Node] = {}
    errors: list[PageError] = []

    for path in sorted(root.rglob("app.py")):
        try:
            pages.update(_load_page(root, path))
        except Exception as cause:
            errors.append(PageError(path, cause))

    if errors:
        raise ExceptionGroup("failed to load pages", errors)

    pages.setdefault("/404", DEFAULT_404)

    return pages
