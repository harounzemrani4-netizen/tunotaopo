#!/usr/bin/env python3
"""Policía Local: una sola página de oposición (Madrid) y el árbol territorial retirado."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pl_territorios import CALCULADORAS  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def main() -> int:
    if set(CALCULADORAS) != {"28079"}:
        fail("solo Madrid puede tener calculadora hasta que haya otro boletín")

    pl_root = ROOT / "oposiciones" / "policia-local"
    dirs = sorted(path.name for path in pl_root.iterdir() if path.is_dir())
    if dirs != ["pruebas", "pruebas-fisicas", "temario"]:
        fail(f"Policía Local solo publica pruebas, físicas y temario como páginas propias, hay {dirs}")
    if (ROOT / "js" / "data" / "pl-municipios.json").exists():
        fail("el índice de municipios ya no se publica")

    hub = (pl_root / "index.html").read_text(encoding="utf-8")
    for anchor in ('id="requisitos"', 'id="fechas"', 'id="notas-corte"', 'id="examenes-oficiales"'):
        if anchor not in hub:
            fail(f"la página de Policía Local debe incluir la sección {anchor}")
    if "comunidad-de-madrid" in hub or "pl-search" in hub:
        fail("la página de Policía Local no debe enlazar el árbol territorial")
    if "noindex" in hub:
        fail("la página de Policía Local debe ser indexable")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "policia-local" in robots:
        fail("robots.txt no debe bloquear Policía Local: Google tiene que ver los 410")
    if "AdsBot-Google" not in robots or "Mediapartners-Google" not in robots:
        fail("robots.txt debe hablarle a los robots de AdSense")

    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if "comunidad-de-madrid" in sitemap:
        fail("el sitemap no debe listar el árbol territorial")
    for slug in ("requisitos", "fechas", "notas-corte", "examenes-oficiales"):
        if f"/{slug}/" in sitemap:
            fail(f"el sitemap no debe listar la sección fusionada {slug}")

    middleware = (ROOT / "functions" / "_middleware.js").read_text(encoding="utf-8")
    for needle in ("status: 410", '"/calculadoras/policia-local/"', "MERGED_SECTIONS"):
        if needle not in middleware:
            fail(f"el middleware debe redirigir o retirar las URLs antiguas ({needle})")

    print("[OK] Policía Local: página única de Madrid, árbol territorial con 301/410")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
