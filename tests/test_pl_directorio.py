#!/usr/bin/env python3
"""El directorio de Policía Local lista todos los municipios INE y no clona Madrid."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from pl_territorios import CALCULADORAS, load_catalog, tree  # noqa: E402


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
    paths = []
    missing = []
    cloned = []
    indexed_empty = []
    for ccaa in built["comunidades"]:
        ccaa_file = ROOT / ccaa["path"] / "index.html"
        if not ccaa_file.exists():
            missing.append(ccaa["path"])
        for prov in ccaa["provincias"]:
            if not (ROOT / prov["path"] / "index.html").exists():
                missing.append(prov["path"])
            for muni in prov["municipios"]:
                paths.append(muni["path"])
                html_path = ROOT / muni["path"] / "index.html"
                if not html_path.exists():
                    missing.append(muni["path"])
                    continue
                html = html_path.read_text(encoding="utf-8")
                if muni["ine"] != "28079":
                    if "id=\"oposicion-config\"" in html or 'id="calc-form"' in html:
                        cloned.append(muni["path"])
                    if 'name="robots" content="noindex"' not in html:
                        indexed_empty.append(muni["path"])
                    if "10 × (A − E/3) / T" in html or "BOAM núm. 9829" in html:
                        cloned.append(muni["path"])
    if len(paths) != 8132:
        fail(f"el árbol tiene {len(paths)} municipios")
    if len(set(paths)) != 8132:
        fail("hay URLs de municipio repetidas")
    if missing:
        fail(f"faltan {len(missing)} páginas, p. ej. {missing[0]}")
    if cloned:
        fail(f"se clonó la calculadora de Madrid en {cloned[0]}")
    if indexed_empty:
        fail(f"municipio sin bases indexable: {indexed_empty[0]}")

    madrid = ROOT / "oposiciones" / "policia-local" / "comunidad-de-madrid" / "madrid" / "madrid" / "index.html"
    madrid_html = madrid.read_text(encoding="utf-8")
    if "Calcular nota de Madrid" not in madrid_html:
        fail("la ficha de Madrid no enlaza la calculadora")
    if "noindex" in madrid_html:
        fail("Madrid no debe ir noindex")

    hub = (ROOT / "oposiciones" / "policia-local" / "index.html").read_text(encoding="utf-8")
    if "8132 municipios" not in hub:
        fail("el hub nacional no declara los 8132 municipios")
    if "pl-search" not in hub:
        fail("el hub nacional no tiene buscador")

    empty = ROOT / "oposiciones" / "policia-local" / "comunitat-valenciana" / "valencia" / "valencia" / "index.html"
    empty_html = empty.read_text(encoding="utf-8")
    if "css/app.css?v=" in empty_html:
        fail("las fichas vacías no deben versionar el CSS: si no, un hover reescribe 8000 HTML")
    if "css/app.css?v=" not in madrid_html:
        fail("Madrid sí debe versionar el CSS")

    index = json.loads((ROOT / "js" / "data" / "pl-municipios.json").read_text(encoding="utf-8"))
    if len(index["items"]) != 8132:
        fail(f"el JSON de búsqueda tiene {len(index['items'])} filas")
    print("[OK] directorio Policía Local: 8132 municipios INE, calculadora solo en Madrid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
