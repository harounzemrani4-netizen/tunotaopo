#!/usr/bin/env python3
"""El generador está partido y los hubs no importan generate_pages."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def imports_of(name: str) -> set[str]:
    tree = ast.parse((SCRIPTS / name).read_text(encoding="utf-8"), filename=name)
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return found


def main() -> int:
    if "generate_pages" in imports_of("hub_pages.py"):
        fail("hub_pages no debe importar generate_pages")
    if (SCRIPTS / "pl_directorio.py").exists():
        fail("el directorio territorial de Policía Local no debe volver")

    for module in (
        "site_catalog.py",
        "site_widgets.py",
        "hub_pages.py",
        "hub_nav.py",
        "hub_tools.py",
        "generate_pages.py",
    ):
        missing = module
        if not (SCRIPTS / missing).exists():
            fail(f"falta {missing}")

    gp_src = (SCRIPTS / "generate_pages.py").read_text(encoding="utf-8")
    if "def write_hubs(" in gp_src:
        fail("write_hubs debe vivir en hub_pages.py")
    if "def catalog_cards(" in gp_src:
        fail("catalog_cards debe vivir en site_catalog.py")
    if "def calculator_form(" in gp_src:
        fail("calculator_form debe vivir en site_widgets.py")
    hub_src = (SCRIPTS / "hub_pages.py").read_text(encoding="utf-8")
    if "def pn_fisicas_page(" in hub_src:
        fail("pn_fisicas_page debe vivir en hub_tools.py")
    if "NAV_LABELS = {" in hub_src:
        fail("NAV_LABELS debe vivir en hub_nav.py")

    import generate_pages  # noqa: F401
    import hub_nav  # noqa: F401
    import hub_pages  # noqa: F401
    import hub_tools  # noqa: F401
    import site_catalog  # noqa: F401
    import site_widgets  # noqa: F401

    print("[OK] modulos partidos y sin import circular hub_pages -> generate_pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
