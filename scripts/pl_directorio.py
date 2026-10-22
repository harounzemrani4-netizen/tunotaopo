"""Páginas del directorio de Policía Local por CCAA, provincia y municipio."""

from __future__ import annotations

import json
import unicodedata
from pathlib import Path
from urllib.parse import quote

from html_shell import crumbs, page_shell, pretty_href, rel_prefix, seo_title, write
from pl_territorios import HUB_RESERVED, search_index, tree
from site_config import CONTACT_EMAIL, ROOT, SITE
from site_widgets import ext_a, source_link
from xml.sax.saxutils import escape

FAMILY = "policia-local"


def search_form(scope: str = "", placeholder: str = "Madrid, Valencia, un pueblo…") -> str:
    scope_attr = f' data-pl-scope="{escape(scope)}"' if scope else ""
    return f"""
      <div class="pl-search-wrap">
      <form class="home-search pl-search" role="search" action="/oposiciones/policia-local/" method="get">
        <label for="pl-search">Busca tu municipio</label>
        <input class="input" id="pl-search" name="q" type="search" placeholder="{escape(placeholder)}" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="pl-search-results" aria-autocomplete="list"{scope_attr}>
      </form>
      <div id="pl-search-results" class="pl-results" role="listbox" hidden></div>
      <p id="pl-search-empty" class="search-empty" hidden>Aún no hay calculadora para esa ciudad. Solo publicamos nota con boletín oficial.</p>
      </div>
    """


def ready_note(muni: dict) -> str:
    if muni.get("ready"):
        return '<span class="pl-flag pl-flag-ready">Calculadora publicada</span>'
    return '<span class="pl-flag">Sin bases recuperadas</span>'


def write_search_json(catalog: dict | None = None) -> None:
    payload = {
        "source": "INE · Relación de municipios y códigos a 1 de enero de 2026",
        "items": search_index(catalog, published_only=True),
    }
    write(ROOT / "js" / "data" / "pl-municipios.json", json.dumps(payload, ensure_ascii=False))


def published_municipios(catalog: dict) -> list[dict]:
    found = []
    for ccaa in catalog["comunidades"]:
        for prov in ccaa["provincias"]:
            for muni in prov["municipios"]:
                if muni.get("ready"):
                    found.append({"ccaa": ccaa, "prov": prov, "muni": muni})
    return found


def national_hub(item: dict, hub: dict, catalog: dict) -> str:
    prefix = rel_prefix(2)
    src = catalog["source"]
    published = published_municipios(catalog)
    cards = []
    for row in published:
        muni = row["muni"]
        ready = muni["ready"]
        cards.append(
            f'<a class="card" href="{pretty_href(muni["path"])}">'
            f"<h3>{escape(muni['nombre'])}</h3>"
            f"<p>{escape(ready['cuerpo'])} · {escape(ready['fuente'])}</p></a>"
        )
    madrid = next(row["muni"] for row in published if row["muni"]["ine"] == "28079")
    n_pub = len(published)
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Local", ""),
    ], f"oposiciones/{FAMILY}/")}
    <div class="hero">
      <p class="eyebrow">Policía Local · Policía Municipal · Guardia Urbana</p>
      <h1>Calculadora de Policía Local con boletín oficial</h1>
      <p class="calc-badge">{n_pub} {'ciudad' if n_pub == 1 else 'ciudades'} con fórmula publicada · no hay ficha vacía por municipio</p>
      {search_form()}
      <p class="hero-actions">
        <a class="button button-primary" href="{pretty_href(madrid['path'])}">Ficha de Madrid</a>
        <a class="button button-secondary" href="{prefix}calculadoras/policia-local/index.html">Calcular nota de Madrid</a>
      </p>
    </div>
    <section class="content">
      <p>No hay una fórmula única de Policía Local para toda España. Cada ayuntamiento publica las suyas. En TuNotaOpo <strong>solo existe página cuando hemos leído el boletín</strong>. No se clona Madrid ni se inventa una nota genérica.</p>
      <p>Hoy hay calculadora de <a href="{pretty_href(madrid['path'])}">Policía Municipal de Madrid</a> ({escape(item.get('source_identifier', 'BOE'))}). Si tu ciudad no sale en el buscador, todavía no hay bases recuperadas. Puedes enviar el identificador del boletín a {escape(CONTACT_EMAIL)}.</p>
      <p>Esto no es Mossos d’Esquadra, Ertzaintza, Policía Foral, Policía Nacional ni Guardia Civil.</p>
    </section>
    <section>
      <h2 class="section-title">Ciudades con calculadora</h2>
      <div class="hub-grid">{"".join(cards)}</div>
    </section>
    <section class="content">
      <p>El listado INE ({ext_a(src['url'], src['title'])}, consultado el 3 de septiembre de 2026) sirve para saber qué municipio es cuál. No se publica una ficha por cada código INE.</p>
    </section>
    """
    return page_shell(
        seo_title("Calculadora de Policía Local"),
        "Calculadora de Policía Local solo con boletín oficial. Hoy Madrid (Policía Municipal). No hay ficha vacía por municipio ni fórmula copiada de otra ciudad.",
        f"oposiciones/{FAMILY}/",
        2,
        body,
    )


def ccaa_page(ccaa: dict, catalog: dict) -> str:
    prefix = rel_prefix(3)
    cards = []
    ready_total = 0
    for prov in ccaa["provincias"]:
        ready = [muni for muni in prov["municipios"] if muni.get("ready")]
        if not ready:
            continue
        ready_total += len(ready)
        cards.append(
            f'<a class="card" href="{pretty_href(prov["path"])}">'
            f"<h3>{escape(prov['nombre'])}</h3>"
            f"<p>{len(ready)} {'calculadora' if len(ready) == 1 else 'calculadoras'}</p></a>"
        )
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Local", prefix + f"oposiciones/{FAMILY}/index.html"),
        (ccaa["nombre"], ""),
    ], ccaa["path"])}
    <div class="hero">
      <p class="eyebrow">Policía Local · {escape(ccaa['nombre'])}</p>
      <h1>Policía Local en {escape(ccaa['nombre'])}</h1>
      <p class="calc-badge">{ready_total} {'ciudad' if ready_total == 1 else 'ciudades'} con boletín recuperado</p>
      {search_form(ccaa["path"], f"Municipio de {ccaa['nombre']}")}
    </div>
    <section class="content">
      <p>Solo aparecen provincias y ciudades de {escape(ccaa['nombre'])} con bases leídas. No hay un listado INE de fichas vacías ni se usa la fórmula de otra ciudad.</p>
    </section>
    <section>
      <h2 class="section-title">Provincias con calculadora</h2>
      <div class="hub-grid">{"".join(cards)}</div>
    </section>
    """
    return page_shell(
        seo_title(f"Policía Local en {ccaa['nombre']}"),
        f"Calculadoras de Policía Local en {ccaa['nombre']} con boletín oficial. Sin fichas vacías ni fórmula copiada de otra ciudad.",
        ccaa["path"],
        3,
        body,
    )


def provincia_page(ccaa: dict, prov: dict) -> str:
    prefix = rel_prefix(4)
    ready = [muni for muni in prov["municipios"] if muni.get("ready")]
    items = []
    for muni in ready:
        items.append(
            f'<li><a href="{pretty_href(muni["path"])}">{escape(muni["nombre"])}</a> {ready_note(muni)}</li>'
        )
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Local", prefix + f"oposiciones/{FAMILY}/index.html"),
        (ccaa["nombre"], prefix + ccaa["path"] + "index.html"),
        (prov["nombre"], ""),
    ], prov["path"])}
    <div class="hero">
      <p class="eyebrow">Policía Local · {escape(ccaa['nombre'])}</p>
      <h1>Policía Local en la provincia de {escape(prov['nombre'])}</h1>
      <p class="calc-badge">{len(ready)} {'ciudad' if len(ready) == 1 else 'ciudades'} con boletín · código INE {escape(prov['id'])}</p>
    </div>
    <section class="content">
      <p>Solo hay ficha si el boletín de ese ayuntamiento está recuperado. El resto de municipios de la provincia no tiene página.</p>
    </section>
    <section>
      <h2 class="section-title">Ciudades con calculadora</h2>
      <ol class="pl-muni-list" id="pl-muni-list">{"".join(items)}</ol>
    </section>
    """
    return page_shell(
        seo_title(f"Policía Local en la provincia de {prov['nombre']}"),
        f"Calculadoras de Policía Local en la provincia de {prov['nombre']} ({ccaa['nombre']}) con boletín oficial. Sin fichas vacías.",
        prov["path"],
        4,
        body,
    )


def municipio_page(item: dict, ccaa: dict, prov: dict, muni: dict) -> str:
    prefix = rel_prefix(5)
    ready = muni.get("ready")
    if ready:
        inner = f"""
      <p class="calc-badge">Calculadora publicada · {escape(ready['fuente'])} · {escape(ready['bases'])}</p>
      <p>En Madrid el cuerpo se llama {escape(ready['cuerpo'])}. Esta es la única ciudad con fórmula atada a boletín en TuNotaOpo. No sirve para otro municipio.</p>
      <p class="hero-actions">
        <a class="button button-primary" href="{prefix}{ready['calc_path']}index.html">Calcular nota de Madrid</a>
        <a class="button button-secondary" href="{prefix}{ready['fisicas_path']}index.html">Pruebas físicas</a>
      </p>
      <nav class="opp-links" aria-label="Convocatoria de Madrid">
        <a href="{prefix}oposiciones/{FAMILY}/requisitos/index.html">Requisitos</a>
        <a href="{prefix}oposiciones/{FAMILY}/pruebas/index.html">Pruebas</a>
        <a href="{prefix}oposiciones/{FAMILY}/temario/index.html">Temario</a>
        <a href="{prefix}oposiciones/{FAMILY}/fechas/index.html">Fechas</a>
        <a href="{prefix}oposiciones/{FAMILY}/notas-corte/index.html">Notas</a>
        <a href="{prefix}oposiciones/{FAMILY}/examenes-oficiales/index.html">Exámenes</a>
      </nav>
        """
        extra = f"""
      <h2>Fuente de esta calculadora</h2>
      <p>Convocatoria: {escape(item.get('convocatoria', ''))}.</p>
      <p>{source_link(item)}.</p>
        """
        robots = None
        noindex = False
    else:
        inner = f"""
      <p class="calc-badge">Sin bases oficiales recuperadas</p>
      <p>Aún no hay una convocatoria de {escape(muni['nombre'])} con fórmula leída en un boletín. <strong>No se calcula una nota</strong> y no se copia la de Madrid ni la de otra ciudad.</p>
      <p>No todos los municipios tienen Policía Local. Si este no convoca, no hay nada que calcular aquí.</p>
      <p class="hero-actions">
        <a class="button button-secondary" href="{prefix}oposiciones/{FAMILY}/index.html">Volver al directorio</a>
        <a class="button button-ghost" href="mailto:{CONTACT_EMAIL}?subject={quote('Bases Policía Local ' + muni['nombre'])}">Enviar un boletín</a>
      </p>
        """
        extra = f"""
      <h2>Qué hace falta para publicar la calculadora</h2>
      <ul>
        <li>El boletín del ayuntamiento o del BOP/BOE de esa convocatoria.</li>
        <li>La fórmula (T, penalización, mínimos) en un apartado concreto.</li>
        <li>Tests del motor. Sin eso no se publica una nota.</li>
      </ul>
      <p>Puedes escribir a {escape(CONTACT_EMAIL)} con el identificador del boletín. No prometemos plazo.</p>
        """
        robots = "noindex"
        noindex = True
    title_city = f"Policía Local de {muni['nombre']}"
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Local", prefix + f"oposiciones/{FAMILY}/index.html"),
        (ccaa["nombre"], prefix + ccaa["path"] + "index.html"),
        (prov["nombre"], prefix + prov["path"] + "index.html"),
        (muni["nombre"], ""),
    ], muni["path"])}
    <div class="hero">
      <p class="eyebrow">{escape(prov['nombre'])} · {escape(ccaa['nombre'])}</p>
      <h1>{escape(title_city)}</h1>
      {inner}
    </div>
    <section class="content">
      <dl class="source-facts">
        <div><dt>Municipio</dt><dd>{escape(muni['nombre'])}</dd></div>
        <div><dt>Provincia</dt><dd>{escape(prov['nombre'])}</dd></div>
        <div><dt>Comunidad</dt><dd>{escape(ccaa['nombre'])}</dd></div>
        <div><dt>Código INE</dt><dd>{escape(muni['ine'])}</dd></div>
      </dl>
      {extra}
      <p>Listado de municipios: {ext_a(catalog_source_url(), "INE, relación a 1 de enero de 2026")}.</p>
    </section>
    """
    description = (
        f"Calculadora de Policía Municipal de Madrid atada a {ready['fuente']}. No vale para otra ciudad."
        if ready
        else (
            f"Ficha de Policía Local de {muni['nombre']} ({prov['nombre']}, código INE {muni['ine']}). "
            "Aún no hay bases recuperadas: no se inventa la nota."
        )
    )
    def _place_fold(value: str) -> str:
        text = unicodedata.normalize("NFD", (value or "").lower())
        return "".join(ch for ch in text if unicodedata.category(ch) != "Mn")

    muni_f = _place_fold(muni["nombre"])
    prov_f = _place_fold(prov["nombre"])
    same_place = bool(muni_f) and (muni_f == prov_f or muni_f in prov_f or prov_f in muni_f)
    title_extra = "" if same_place else prov["nombre"]
    return page_shell(
        seo_title(title_city, title_extra),
        description,
        muni["path"],
        5,
        body,
        noindex=noindex,
        robots=robots,
        pin_assets=not ready,
    )


def catalog_source_url() -> str:
    return "https://www.ine.es/daco/daco42/codmun/26codmun.xlsx"


def clear_generated_tree(root: Path) -> None:
    base = root / "oposiciones" / FAMILY
    if not base.exists():
        return
    for child in base.iterdir():
        if child.name in HUB_RESERVED or child.name == "index.html":
            continue
        if child.is_dir():
            import shutil

            shutil.rmtree(child)


def write_all(item: dict, hub: dict) -> list[str]:
    catalog = tree()
    write_search_json(catalog)
    clear_generated_tree(ROOT)
    write(ROOT / "oposiciones" / FAMILY / "index.html", national_hub(item, hub, catalog))
    urls = [f"{SITE}/oposiciones/{FAMILY}/"]
    for ccaa in catalog["comunidades"]:
        ready_provs = [
            prov for prov in ccaa["provincias"] if any(muni.get("ready") for muni in prov["municipios"])
        ]
        if not ready_provs:
            continue
        write(ROOT / ccaa["path"] / "index.html", ccaa_page(ccaa, catalog))
        urls.append(f"{SITE}/{ccaa['path']}")
        for prov in ready_provs:
            write(ROOT / prov["path"] / "index.html", provincia_page(ccaa, prov))
            urls.append(f"{SITE}/{prov['path']}")
            for muni in prov["municipios"]:
                if not muni.get("ready"):
                    continue
                write(ROOT / muni["path"] / "index.html", municipio_page(item, ccaa, prov, muni))
                urls.append(f"{SITE}/{muni['path']}")
    return urls
