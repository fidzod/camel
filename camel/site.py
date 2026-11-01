__all__ = ["generate"]

import json
import os
import shutil
from pathlib import Path

from camel.css import to_css
from camel.dsl import Node
from camel.ir import to_ir

_STATIC = Path(__file__).parent / "static"


def generate(tree: Node) -> None:
    out = Path(os.environ.get("CAMEL_OUT", "."))
    out.mkdir(parents=True, exist_ok=True)

    ir = to_ir(tree)
    (out / "site.js").write_text(f"const site = {json.dumps(ir)};")

    (out / "style.css").write_text(to_css(tree))

    shutil.copy(_STATIC / "runtime.js", out / "runtime.js")
    shutil.copy(_STATIC / "index.html", out / "index.html")
