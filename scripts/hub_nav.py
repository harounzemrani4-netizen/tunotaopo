"""Navegación interna de cada oposición."""

from __future__ import annotations

from xml.sax.saxutils import escape

from hubs_data import HUBS

NAV_LABELS = {
    "requisitos": "Requisitos",
    "pruebas": "Pruebas",
    "fisicas": "Físicas",
    "baremo": "Baremo",
    "temario": "Temario",
    "fechas": "Fechas",
    "notas": "Notas",
    "examenes": "Exámenes",
}
HUB_SLUGS = {
    "requisitos": "requisitos",
    "pruebas": "pruebas",
    "fisicas": "pruebas-fisicas",
    "baremo": "baremo",
    "temario": "temario",
    "fechas": "fechas",
    "notas": "notas-corte",
    "examenes": "examenes-oficiales",
}
HUB_ANCHORS = {"requisitos", "fechas", "notas", "examenes"}


def hub_href(family: str, prefix: str, key: str) -> str:
    """URL de una sección: ancla en la página de la oposición o página propia."""
    if key in HUB_ANCHORS:
        return f"{prefix}oposiciones/{family}/index.html#{HUB_SLUGS[key]}"
    return f"{prefix}oposiciones/{family}/{HUB_SLUGS[key]}/index.html"


def hub_nav(family: str, prefix: str, current: str) -> str:
    calc_folder = "auxiliar-administrativo-age" if family == "auxiliar-age" else family
    items = [
        ("Resumen", f"{prefix}oposiciones/{family}/index.html", "hub"),
        ("Calcular nota", f"{prefix}calculadoras/{calc_folder}/index.html", "calc"),
    ]
    for key in (HUBS.get(family) or {}).get("pages") or []:
        items.append((NAV_LABELS[key], hub_href(family, prefix, key), key))
    bits = []
    for label, href, key in items:
        extra = ' class="is-current" aria-current="page"' if key == current else ""
        bits.append(f'<a href="{href}"{extra}>{escape(label)}</a>')
    return f'<nav class="opp-links" aria-label="Secciones">{"".join(bits)}</nav>'
