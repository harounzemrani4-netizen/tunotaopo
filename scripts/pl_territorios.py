#!/usr/bin/env python3
"""Territorios de España para el directorio de Policía Local.

Municipios: relación INE a 1 de enero de 2026 (26codmun.xlsx).
CCAA y cruce provincia→comunidad: códigos oficiales INE.
No afirma qué municipios tienen Policía Local.
"""

from __future__ import annotations

import json
import re
import unicodedata
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "policia-local"
XLSX = DATA_DIR / "26codmun.xlsx"
CATALOG = DATA_DIR / "municipios.json"

INE_XLSX_URL = "https://www.ine.es/daco/daco42/codmun/26codmun.xlsx"
INE_TITLE = "Relación de municipios y códigos a 1 de enero de 2026"
INE_ACCESSED = "2026-09-03"

# Códigos INE de comunidad (CODAUTO) por código de provincia (CPRO).
PROVINCIA_TO_CCAA = {
    "01": "16",
    "02": "08",
    "03": "10",
    "04": "01",
    "05": "07",
    "06": "11",
    "07": "04",
    "08": "09",
    "09": "07",
    "10": "11",
    "11": "01",
    "12": "10",
    "13": "08",
    "14": "01",
    "15": "12",
    "16": "08",
    "17": "09",
    "18": "01",
    "19": "08",
    "20": "16",
    "21": "01",
    "22": "02",
    "23": "01",
    "24": "07",
    "25": "09",
    "26": "17",
    "27": "12",
    "28": "13",
    "29": "01",
    "30": "14",
    "31": "15",
    "32": "12",
    "33": "03",
    "34": "07",
    "35": "05",
    "36": "12",
    "37": "07",
    "38": "05",
    "39": "06",
    "40": "07",
    "41": "01",
    "42": "07",
    "43": "09",
    "44": "02",
    "45": "08",
    "46": "10",
    "47": "07",
    "48": "16",
    "49": "07",
    "50": "02",
    "51": "18",
    "52": "19",
}

# Nombres de uso (INE usa a veces «Madrid, Comunidad de»).
CCAA_META = {
    "01": {"nombre": "Andalucía", "slug": "andalucia"},
    "02": {"nombre": "Aragón", "slug": "aragon"},
    "03": {"nombre": "Principado de Asturias", "slug": "asturias"},
    "04": {"nombre": "Illes Balears", "slug": "illes-balears"},
    "05": {"nombre": "Canarias", "slug": "canarias"},
    "06": {"nombre": "Cantabria", "slug": "cantabria"},
    "07": {"nombre": "Castilla y León", "slug": "castilla-y-leon"},
    "08": {"nombre": "Castilla-La Mancha", "slug": "castilla-la-mancha"},
    "09": {"nombre": "Cataluña", "slug": "cataluna"},
    "10": {"nombre": "Comunitat Valenciana", "slug": "comunitat-valenciana"},
    "11": {"nombre": "Extremadura", "slug": "extremadura"},
    "12": {"nombre": "Galicia", "slug": "galicia"},
    "13": {"nombre": "Comunidad de Madrid", "slug": "comunidad-de-madrid"},
    "14": {"nombre": "Región de Murcia", "slug": "region-de-murcia"},
    "15": {"nombre": "Comunidad Foral de Navarra", "slug": "navarra"},
    "16": {"nombre": "País Vasco", "slug": "pais-vasco"},
    "17": {"nombre": "La Rioja", "slug": "la-rioja"},
    "18": {"nombre": "Ciudad de Ceuta", "slug": "ceuta"},
    "19": {"nombre": "Ciudad de Melilla", "slug": "melilla"},
}

PROVINCIA_SLUG = {
    "01": "araba-alava",
    "02": "albacete",
    "03": "alicante",
    "04": "almeria",
    "05": "avila",
    "06": "badajoz",
    "07": "illes-balears",
    "08": "barcelona",
    "09": "burgos",
    "10": "caceres",
    "11": "cadiz",
    "12": "castellon",
    "13": "ciudad-real",
    "14": "cordoba",
    "15": "a-coruna",
    "16": "cuenca",
    "17": "girona",
    "18": "granada",
    "19": "guadalajara",
    "20": "gipuzkoa",
    "21": "huelva",
    "22": "huesca",
    "23": "jaen",
    "24": "leon",
    "25": "lleida",
    "26": "la-rioja",
    "27": "lugo",
    "28": "madrid",
    "29": "malaga",
    "30": "murcia",
    "31": "navarra",
    "32": "ourense",
    "33": "asturias",
    "34": "palencia",
    "35": "las-palmas",
    "36": "pontevedra",
    "37": "salamanca",
    "38": "santa-cruz-de-tenerife",
    "39": "cantabria",
    "40": "segovia",
    "41": "sevilla",
    "42": "soria",
    "43": "tarragona",
    "44": "teruel",
    "45": "toledo",
    "46": "valencia",
    "47": "valladolid",
    "48": "bizkaia",
    "49": "zamora",
    "50": "zaragoza",
    "51": "ceuta",
    "52": "melilla",
}

# Solo ciudades con boletín y fórmula recuperados. No clonar Madrid.
CALCULADORAS = {
    "28079": {
        "calc_path": "calculadoras/policia-local/",
        "fisicas_path": "oposiciones/policia-local/pruebas-fisicas/",
        "cuerpo": "Policía Municipal del Ayuntamiento de Madrid",
        "fuente": "BOE-A-2025-25740",
        "bases": "BOAM núm. 9829",
    }
}

HUB_RESERVED = {
    "requisitos",
    "pruebas",
    "pruebas-fisicas",
    "temario",
    "fechas",
    "notas-corte",
    "examenes-oficiales",
    "baremo",
}

ARTICLE_RE = re.compile(
    r"^(.+),\s+(La|El|Las|Los|L'|L’|A|O|Els|Les|Sa|Es|As)$",
    re.IGNORECASE,
)
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def slugify(text: str) -> str:
    folded = unicodedata.normalize("NFD", text)
    folded = "".join(ch for ch in folded if unicodedata.category(ch) != "Mn")
    folded = folded.replace("·", "-").replace("/", "-").replace("'", "").replace("’", "")
    folded = folded.lower()
    folded = re.sub(r"[^a-z0-9]+", "-", folded)
    return folded.strip("-")


def slug_from_nombre(nombre: str) -> str:
    match = ARTICLE_RE.match(nombre.strip())
    if match:
        return slugify(f"{match.group(2)} {match.group(1)}")
    return slugify(nombre)


def _xlsx_strings(zf: zipfile.ZipFile) -> list[str]:
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    values = []
    for si in root.findall("m:si", NS):
        values.append("".join(node.text or "" for node in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
    return values


def _cell_value(cell: ET.Element, strings: list[str]) -> str:
    kind = cell.attrib.get("t")
    node = cell.find("m:v", NS)
    if node is None or node.text is None:
        return ""
    if kind == "s":
        return strings[int(node.text)]
    return node.text


def _row_cells(row: ET.Element, strings: list[str]) -> dict[str, str]:
    out = {}
    for cell in row.findall("m:c", NS):
        ref = cell.attrib.get("r", "")
        col = "".join(ch for ch in ref if ch.isalpha())
        out[col] = _cell_value(cell, strings)
    return out


def parse_xlsx(path: Path | None = None) -> dict:
    xlsx = path or XLSX
    if not xlsx.exists():
        raise FileNotFoundError(f"Falta el Excel del INE: {xlsx}")
    provincias: dict[str, dict] = {}
    municipios: list[dict] = []
    with zipfile.ZipFile(xlsx) as zf:
        strings = _xlsx_strings(zf)
        for index in range(1, 53):
            sheet = ET.fromstring(zf.read(f"xl/worksheets/sheet{index}.xml"))
            rows = sheet.findall("m:sheetData/m:row", NS)
            if len(rows) < 4:
                raise ValueError(f"Hoja {index} del INE incompleta")
            title_row = _row_cells(rows[1], strings)
            nombre_prov = (title_row.get("A") or "").strip()
            if not nombre_prov:
                raise ValueError(f"Hoja {index} sin nombre de provincia")
            for row in rows[3:]:
                cells = _row_cells(row, strings)
                cpro = (cells.get("A") or "").strip().zfill(2)
                cmun = (cells.get("B") or "").strip().zfill(3)
                dc = (cells.get("C") or "").strip()
                nombre = (cells.get("D") or "").strip()
                if not nombre or not cpro or not cmun:
                    continue
                if cpro not in provincias:
                    ccaa_id = PROVINCIA_TO_CCAA[cpro]
                    provincias[cpro] = {
                        "id": cpro,
                        "nombre": nombre_prov,
                        "slug": PROVINCIA_SLUG[cpro],
                        "ccaa_id": ccaa_id,
                    }
                municipios.append(
                    {
                        "ine": f"{cpro}{cmun}",
                        "nombre": nombre,
                        "slug": slug_from_nombre(nombre),
                        "provincia_id": cpro,
                        "cmun": cmun,
                        "dc": dc,
                    }
                )
    used: dict[str, set[str]] = {}
    for muni in municipios:
        key = f"{muni['provincia_id']}"
        bucket = used.setdefault(key, set())
        slug = muni["slug"]
        if slug in bucket:
            slug = f"{slug}-{muni['cmun']}"
            muni["slug"] = slug
        bucket.add(slug)
        if muni["slug"] in HUB_RESERVED:
            muni["slug"] = f"{muni['slug']}-municipio"
    comunidades = [
        {"id": cid, "nombre": meta["nombre"], "slug": meta["slug"]}
        for cid, meta in CCAA_META.items()
    ]
    return {
        "source": {
            "publisher": "INE",
            "title": INE_TITLE,
            "url": INE_XLSX_URL,
            "accessed_at": INE_ACCESSED,
            "path": "data/policia-local/26codmun.xlsx",
        },
        "comunidades": comunidades,
        "provincias": [provincias[key] for key in sorted(provincias)],
        "municipios": municipios,
    }


def write_catalog(data: dict | None = None) -> dict:
    payload = data or parse_xlsx()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def load_catalog() -> dict:
    if not CATALOG.exists():
        return write_catalog()
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def tree() -> dict:
    data = load_catalog()
    ccaa_by_id = {row["id"]: {**row, "provincias": []} for row in data["comunidades"]}
    prov_by_id = {row["id"]: {**row, "municipios": []} for row in data["provincias"]}
    for muni in data["municipios"]:
        ready = CALCULADORAS.get(muni["ine"])
        row = {**muni, "ready": ready}
        ccaa = CCAA_META[PROVINCIA_TO_CCAA[muni["provincia_id"]]]
        prov = prov_by_id[muni["provincia_id"]]
        row["path"] = (
            f"oposiciones/policia-local/{ccaa['slug']}/{prov['slug']}/{muni['slug']}/"
        )
        row["provincia"] = prov
        row["ccaa"] = ccaa_by_id[prov["ccaa_id"]]
        prov["municipios"].append(row)
    for prov in prov_by_id.values():
        prov["municipios"].sort(key=lambda item: slugify(item["nombre"]))
        ccaa_by_id[prov["ccaa_id"]]["provincias"].append(prov)
    comunidades = []
    for cid in sorted(ccaa_by_id):
        item = ccaa_by_id[cid]
        item["provincias"].sort(key=lambda row: slugify(row["nombre"]))
        item["path"] = f"oposiciones/policia-local/{item['slug']}/"
        item["n_municipios"] = sum(len(prov["municipios"]) for prov in item["provincias"])
        for prov in item["provincias"]:
            prov["path"] = f"oposiciones/policia-local/{item['slug']}/{prov['slug']}/"
            prov["ccaa"] = {"id": item["id"], "nombre": item["nombre"], "slug": item["slug"], "path": item["path"]}
        comunidades.append(item)
    return {
        "source": data["source"],
        "comunidades": comunidades,
        "n_municipios": len(data["municipios"]),
        "n_provincias": len(data["provincias"]),
        "n_comunidades": len(data["comunidades"]),
    }


def search_index(catalog: dict | None = None, *, published_only: bool = False) -> list[list]:
    built = catalog or tree()
    rows = []
    for ccaa in built["comunidades"]:
        for prov in ccaa["provincias"]:
            for muni in prov["municipios"]:
                ready = bool(muni.get("ready"))
                if published_only and not ready:
                    continue
                rows.append(
                    [
                        muni["ine"],
                        muni["nombre"],
                        prov["nombre"],
                        muni["path"],
                        1 if ready else 0,
                    ]
                )
    rows.sort(key=lambda row: (row[4] * -1, slugify(row[1]), slugify(row[2])))
    return rows


def municipio_by_ine(ine: str) -> dict | None:
    built = tree()
    for ccaa in built["comunidades"]:
        for prov in ccaa["provincias"]:
            for muni in prov["municipios"]:
                if muni["ine"] == ine:
                    return muni
    return None


if __name__ == "__main__":
    payload = write_catalog()
    print(
        f"INE {payload['source']['title']}: "
        f"{len(payload['municipios'])} municipios, "
        f"{len(payload['provincias'])} provincias, "
        f"{len(payload['comunidades'])} CCAA"
    )
