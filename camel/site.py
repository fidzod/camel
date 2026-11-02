__all__ = ["write_site"]

import json
import shutil
from pathlib import Path

from camel.css import to_css
from camel.dsl import Node
from camel.ir import to_ir

_STATIC = Path(__file__).parent / "static"


def write_site(routes: dict[str, Node], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)

    site_ir = {route: to_ir(page) for route, page in routes.items()}
    (out / "site.js").write_text(f"const site = {json.dumps(site_ir)};")

    css = "\n".join(filter(None, (to_css(page) for page in routes.values())))
    (out / "style.css").write_text(css)

    shutil.copy(_STATIC / "runtime.js", out / "runtime.js")
    shutil.copy(_STATIC / "index.html", out / "index.html")
