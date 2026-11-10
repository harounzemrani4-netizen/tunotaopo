#!/usr/bin/env python3
"""SW, tema y security.txt alineados con ASSET_V."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from site_config import ASSET_V  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def main() -> int:
    sw = (ROOT / "sw.js").read_text(encoding="utf-8")
    if f"tunotaopo-core-{ASSET_V}" not in sw:
        fail("sw.js no usa ASSET_V en el nombre de caché")
    if "/offline.html" not in sw:
        fail("sw.js no cachea offline.html")
    if f"css/app.css?v={ASSET_V}" not in sw:
        fail("sw.js no cachea el CSS versionado")

    if not (ROOT / "offline.html").exists():
        fail("falta offline.html")
    if not (ROOT / "js" / "theme-boot.js").exists():
        fail("falta theme-boot.js")

    security = (ROOT / ".well-known" / "security.txt").read_text(encoding="utf-8")
    if "contacto@tunotaopo.es" not in security:
        fail("security.txt sin correo")
    if "2027-09-03" not in security:
        fail("security.txt sin Expires")

    css = (ROOT / "css" / "app.css").read_text(encoding="utf-8")
    if ".nav-short" not in css:
        fail("app.css no define .nav-short")
    if "grid-template-columns: 1fr 1fr" not in css:
        fail("la nav móvil debe ser una cuadrícula 2x2, no una sola línea")
    if "flex-wrap: nowrap" in css:
        fail("la nav móvil no debe forzar una sola línea")
    if "@media (max-width: 360px)" not in css:
        fail("app.css no tiene breakpoint 360px")
    if "@media (max-width: 320px)" not in css:
        fail("app.css no tiene breakpoint 320px")
    if ".nav a { font-size: 0.8rem; min-height: 36px; }" in css:
        fail("la nav no puede bajar de 44px")
    if "theme-toggle { width: 32px" in css:
        fail("el toggle no puede quedar en 32px")
    if "width: 44px;" not in css or "height: 44px;" not in css:
        fail("el toggle debe medir 44px")
    if 'html[data-theme="dark"] .button-primary' in css:
        fail("el CSS oscuro no debe duplicar selectores de componente")
    if "--suggest-hover-bg:" not in css:
        fail("el tema oscuro debe usar tokens, no bloques duplicados")
    if ".site-header a:hover:not(.button):not(.card)" not in css:
        fail("el hover del header debe ganar al color oscuro de los enlaces")
    if "--header-link-hover:" not in css:
        fail("el hover del header debe usar un color visible sobre el fondo oscuro")

    analytics = (ROOT / "js" / "components" / "analytics.js").read_text(encoding="utf-8")
    if 'hostname === "www.tunotaopo.es"' not in analytics:
        fail("sendBeacon solo debe dispararse en www.tunotaopo.es")

    event_api = (ROOT / "functions" / "api" / "event.js").read_text(encoding="utf-8")
    if "sameOrigin" not in event_api:
        fail("/api/event debe comprobar origen")
    if "url.host" not in event_api:
        fail("/api/event debe aceptar Host same-origin si falta Origin")

    packer = (ROOT / "scripts" / "package_cloudflare.py").read_text(encoding="utf-8")
    for needle in ('"sw.js"', '"offline.html"', '"manifest.webmanifest"', '".well-known"', '"embed"', '"functions"'):
        if needle not in packer:
            fail(f"package_cloudflare no incluye {needle}")

    if "url.searchParams.get(\"v\")" not in sw:
        fail("el SW no debe cachear JS/CSS sin ?v=")

    calc = (ROOT / "js" / "components" / "calculator.js").read_text(encoding="utf-8")
    if 'removeItem("notaopo:"' in calc:
        fail("calculator.js no debe limpiar claves notaopo: huerfanas")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    if f'name="asset-v" content="{ASSET_V}"' not in home:
        fail("el inicio no publica asset-v")
    if "theme-toggle" not in home:
        fail("el inicio no tiene toggle de tema")
    if "theme-icon-moon" not in home or "theme-icon-sun" not in home:
        fail("el toggle debe usar iconos SVG de sol y luna")
    if "box-shadow: inset 6px 0 0 currentColor" in css:
        fail("el icono del tema no debe ser un círculo CSS")
    if "theme-boot.js" not in home:
        fail("el inicio no carga theme-boot.js")
    if "js/site.js?v=" not in home:
        fail("el inicio debe versionar site.js")

    madrid_html = (ROOT / "oposiciones" / "policia-local" / "index.html").read_text(encoding="utf-8")
    if "theme-boot.js?v=" not in madrid_html:
        fail("Policía Local sí debe versionar theme-boot")
    if "theme-toggle" not in madrid_html:
        fail("Policía Local debe llevar toggle de tema")

    print(f"[OK] assets alineados con {ASSET_V}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
