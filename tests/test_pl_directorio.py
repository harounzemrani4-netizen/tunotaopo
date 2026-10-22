#!/usr/bin/env python3
"""El directorio de Policía Local solo publica ciudades con boletín."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pl_territorios import CALCULADORAS, HUB_RESERVED, load_catalog, tree  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def main() -> int:
    data = load_catalog()
    if len(data["municipios"]) != 8132:
        fail(f"municipios INE={len(data['municipios'])}, se esperaban 8132")
    if len(data["provincias"]) != 52:
        fail(f"provincias={len(data['provincias'])}, se esperaban 52")
    if len(data["comunidades"]) != 19:
        fail(f"CCAA={len(data['comunidades'])}, se esperaban 19")
    ines = [row["ine"] for row in data["municipios"]]
    if len(set(ines)) != 8132:
        fail("hay códigos INE duplicados")
    if "28079" not in ines:
        fail("falta Madrid (28079)")
    if set(CALCULADORAS) != {"28079"}:
        fail("solo Madrid puede tener calculadora hasta que haya otro boletín")

    built = tree()
    pl_root = ROOT / "oposiciones" / "policia-local"
    extra_dirs = [
        path.name
        for path in pl_root.iterdir()
        if path.is_dir() and path.name not in HUB_RESERVED
    ]
    if extra_dirs != ["comunidad-de-madrid"]:
        fail(f"solo debe existir la CCAA con calculadora, hay {extra_dirs}")

    empty = ROOT / "oposiciones" / "policia-local" / "andalucia" / "almeria" / "abla" / "index.html"
    if empty.exists():
        fail("sigue publicada una ficha INE sin boletín (Abla)")
    if (ROOT / "oposiciones" / "policia-local" / "andalucia" / "index.html").exists():
        fail("sigue publicada una CCAA sin calculadora")
    if (ROOT / "oposiciones" / "policia-local" / "comunitat-valenciana" / "valencia" / "valencia" / "index.html").exists():
        fail("sigue publicada Valencia sin boletín")

    published = 0
    for ccaa in built["comunidades"]:
        for prov in ccaa["provincias"]:
            for muni in prov["municipios"]:
                html_path = ROOT / muni["path"] / "index.html"
                if muni.get("ready"):
                    published += 1
                    if not html_path.exists():
                        fail(f"falta la ficha publicada {muni['path']}")
                    continue
                if html_path.exists():
                    fail(f"ficha sin boletín publicada: {muni['path']}")
    if published != 1:
        fail(f"hay {published} fichas publicadas, se esperaba 1")

    madrid = ROOT / "oposiciones" / "policia-local" / "comunidad-de-madrid" / "madrid" / "madrid" / "index.html"
    madrid_html = madrid.read_text(encoding="utf-8")
    if "Calcular nota de Madrid" not in madrid_html:
        fail("la ficha de Madrid no enlaza la calculadora")
    if "noindex" in madrid_html:
        fail("Madrid no debe ir noindex")
    if "css/app.css?v=" not in madrid_html:
        fail("Madrid sí debe versionar el CSS")
    if "ad-slot" not in madrid_html:
        fail("Madrid sí puede reservar publicidad: tiene calculadora")

    hub = (ROOT / "oposiciones" / "policia-local" / "index.html").read_text(encoding="utf-8")
    if "8132 municipios" in hub or "todos los municipios" in hub.lower():
        fail("el hub no debe venderse como directorio de 8132 fichas")
    if "pl-search" not in hub:
        fail("el hub nacional no tiene buscador")
    if "Ciudades con calculadora" not in hub:
        fail("el hub debe listar solo ciudades con boletín")
    if "/oposiciones/policia-local/andalucia/" in hub:
        fail("el hub no debe enlazar CCAA sin calculadora")

    ccaa = (ROOT / "oposiciones" / "policia-local" / "comunidad-de-madrid" / "index.html").read_text(encoding="utf-8")
    if "noindex" in ccaa:
        fail("la CCAA de Madrid tiene calculadora: no debe ir noindex")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if "Disallow: /oposiciones/policia-local/" not in robots:
        fail("robots.txt debe cerrar el árbol de fichas INE antiguas")
    if "Allow: /oposiciones/policia-local/comunidad-de-madrid/" not in robots:
        fail("robots.txt debe dejar pasar Madrid")
    if "AdsBot-Google" not in robots or "Mediapartners-Google" not in robots:
        fail("robots.txt debe hablarle a los robots de AdSense")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    if "/oposiciones/policia-local/andalucia/" in sitemap:
        fail("el sitemap no debe listar CCAA sin calculadora")
    if "/oposiciones/policia-local/comunidad-de-madrid/madrid/madrid/" not in sitemap:
        fail("el sitemap debe incluir la ficha de Madrid")

    index = json.loads((ROOT / "js" / "data" / "pl-municipios.json").read_text(encoding="utf-8"))
    if len(index["items"]) != 1:
        fail(f"el JSON de búsqueda tiene {len(index['items'])} filas; solo Madrid")
    if index["items"][0][0] != "28079":
        fail("el JSON de búsqueda debe empezar por Madrid")
    print("[OK] directorio Policía Local: fichas solo con boletín, calculadora en Madrid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
