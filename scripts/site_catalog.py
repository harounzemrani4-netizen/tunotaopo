"""Catálogo de oposiciones: familia, vigencia y tarjetas."""

from __future__ import annotations

from xml.sax.saxutils import escape

from hubs_data import HUBS
from site_config import FEATURED_FAMILIES


def family_id(item: dict) -> str:
    if item.get("family"):
        return item["family"]
    slug = item.get("slug", "")
    return slug.rsplit("-", 1)[0] if slug else slug


def live_path(item: dict) -> str:
    if item.get("is_current") and item.get("family_path"):
        return item["family_path"]
    return item["path"]


def path_depth(path: str) -> int:
    return len([part for part in path.strip("/").split("/") if part])


def current_by_family(items: list[dict]) -> list[dict]:
    chosen: dict[str, dict] = {}
    for item in items:
        fid = family_id(item)
        prev = chosen.get(fid)
        if prev is None:
            chosen[fid] = item
            continue
        if item.get("is_current") and not prev.get("is_current"):
            chosen[fid] = item
        elif item.get("is_current") == prev.get("is_current") and (item.get("anio") or 0) > (prev.get("anio") or 0):
            chosen[fid] = item
    order = {fid: i for i, fid in enumerate(FEATURED_FAMILIES)}
    return sorted(chosen.values(), key=lambda x: order.get(family_id(x), 99))


def card_tests(item: dict) -> str:
    scored = []
    pass_fail = []
    for stage in item.get("stages") or []:
        if stage.get("model") in {"aggregate", "multi_stage", "transform"}:
            continue
        if stage.get("model") in {"pass_fail_errors", "pass_fail"}:
            pass_fail.append(stage["label"])
        else:
            scored.append(stage["label"])
    labels = scored + pass_fail
    if item.get("merits"):
        labels.append(item["merits"].get("label") or "Méritos")
    if family_id(item) == "policia-nacional":
        labels.append("Pruebas físicas")
    if family_id(item) == "policia-local":
        labels.append("Pruebas físicas")
    if family_id(item) == "guardia-civil":
        labels.append("Pruebas físicas")
        labels.append("Baremo")
    return " · ".join(labels)


def catalog_cards(items: list[dict], href_prefix: str = "", *, dest: str = "calc") -> str:
    cards = []
    for item in current_by_family(items):
        name = item.get("family_name") or item["short_name"]
        year = item.get("anio", "")
        hub = HUBS.get(family_id(item), {})
        badge = hub.get("process_label") or f"Proceso {year}"
        if family_id(item) == "policia-local":
            href = f"{href_prefix}oposiciones/policia-local/index.html"
            cta = "Elige tu ciudad"
            name = "Policía Local"
            badge = "Directorio por municipio"
            kind = "Todas las ciudades. Calculadora solo con boletín oficial."
            source = "Listado INE 2026 · Madrid con fórmula"
        elif dest == "hub":
            href = f"{href_prefix}oposiciones/{family_id(item)}/index.html"
            cta = "Ver oposición"
            kind = f"Calcula tu nota de la convocatoria {year}"
            source = card_tests(item)
        else:
            href = f"{href_prefix}{live_path(item)}index.html"
            cta = "Calcular mi nota"
            kind = f"Calcula tu nota de la convocatoria {year}"
            source = card_tests(item)
        cards.append(
            f'<a class="card catalog-card" href="{href}" data-aliases="{escape(" ".join(item.get("aliases") or []))}">'
            f'<div class="card-meta"><span class="badge">{escape(badge)}</span>'
            f'<span class="card-org">Fuente: {escape(item.get("source_identifier", "") if family_id(item) != "policia-local" else "INE + BOE Madrid")}</span></div>'
            f"<h2>{escape(name)}</h2>"
            f'<p class="card-kind">{escape(kind)}</p>'
            f'<p class="card-source">{escape(source)}</p>'
            f'<span class="card-cta">{cta}</span></a>'
        )
    return "".join(cards)


def opo_search_form() -> str:
    return """
      <div class="opo-suggest">
        <form class="home-search" role="search" action="/oposiciones/" method="get">
          <label for="opo-search">¿Qué oposición preparas?</label>
          <input class="input" id="opo-search" name="q" type="search" placeholder="Escribe local, PN, GC, IIPP…" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="opo-suggest-list" aria-autocomplete="list" aria-activedescendant="">
        </form>
        <ul id="opo-suggest-list" class="opo-suggest-list" role="listbox" hidden></ul>
        <p id="opo-suggest-empty" class="search-empty" hidden>No hay una oposición con ese nombre. Prueba local, PN, GC, AGE, IIPP o auxilio.</p>
      </div>
    """
