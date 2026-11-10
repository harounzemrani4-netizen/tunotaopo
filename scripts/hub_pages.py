"""Hubs de oposición: índice, página de cada oposición y secciones propias."""

from __future__ import annotations

import shutil
from xml.sax.saxutils import escape

from examenes_oficiales import EXAMENES
from fisicas_tables import fisicas_tables_html
from html_shell import crumbs, extra_paras, page_shell, rel_prefix, seo_title, write
from hub_nav import HUB_ANCHORS, HUB_SLUGS, hub_href, hub_nav
from hub_tools import gc_baremo_page, gc_fisicas_page, pl_fisicas_page, pn_fisicas_page
from hubs_data import HUBS
from site_catalog import catalog_cards, current_by_family, family_id, live_path, opo_search_form
from site_config import BRAND, REVIEWED_ON, ROOT, SITE
from site_widgets import (
    changelog_html,
    ext_a,
    process_flow,
    timeline_html,
    unpack_prueba,
)

STANDALONE = {"pruebas", "fisicas", "baremo", "temario"}


def oposiciones_index(opos: list[dict]) -> str:
    status_rows = "".join(
        f'<li><a href="{family}/index.html"><strong>{escape(hub["name"])}</strong></a>: {escape(hub["badge"])}.</li>'
        for family, hub in HUBS.items()
    )
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Oposiciones", "")], "oposiciones/")}
    <div class="hero">
      <h1>Oposiciones</h1>
      <p class="lede">Tu convocatoria, tus pruebas y tu calculadora. Cada cuerpo con su boletín. Sin temario de academia ni cortes inventados.</p>
      {opo_search_form()}
    </div>
    <div class="catalog" id="opo-catalog">{catalog_cards(opos, "../", dest="hub")}</div>
    <p id="opo-search-empty" class="search-empty" hidden>No hay una oposición con ese nombre en TuNotaOpo. Prueba PN, GC, local, AGE, IIPP o auxilio.</p>
    <section class="content">
      <h2>En qué punto está cada proceso</h2>
      <p>Revisado el {REVIEWED_ON} con los boletines y las webs de cada tribunal.</p>
      <ul>{status_rows}</ul>
      <p>Cada página de oposición junta en un solo sitio los requisitos, el calendario, los cortes publicados y los enlaces a exámenes y plantillas oficiales. Las pruebas físicas, el baremo y el temario tienen su propia página porque llevan calculadora o tablas largas.</p>
    </section>
    """
    return page_shell(
        seo_title("Oposiciones"),
        "Policía Nacional, Guardia Civil, Policía Local (hoy Madrid), Auxiliar AGE, Auxilio Judicial y Ayudantes IIPP: calculadora solo con boletín oficial.",
        "oposiciones/",
        1,
        body,
    )


def hub_tile_href(key: str, prefix: str, family: str, item: dict) -> str:
    if key == "calc":
        return prefix + live_path(item) + "index.html"
    if key.startswith("http"):
        return key
    return hub_href(family, prefix, key)


def requisitos_section(item: dict, hub: dict) -> str:
    rows = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>" for label, text in hub["requisitos"]
    )
    return (
        '<section class="content hub-section" id="requisitos" aria-labelledby="requisitos-title">'
        f'<h2 id="requisitos-title">Requisitos</h2>'
        f"<p>{escape(hub['requisitos_lead'])}</p>"
        f'<dl class="source-facts">{rows}</dl>'
        f"{extra_paras(hub.get('requisitos_extra'))}"
        "</section>"
    )


def pruebas_summary(prefix: str, family: str, hub: dict) -> str:
    return (
        '<section class="content hub-section" aria-labelledby="pruebas-title">'
        f'<h2 id="pruebas-title">Pruebas, en orden</h2>'
        f"<p>{escape(hub['pruebas_lead'])}</p>"
        f"{process_flow(hub)}"
        f'<p><a href="{hub_href(family, prefix, "pruebas")}">Ver cada prueba con sus mínimos →</a></p>'
        "</section>"
    )


def next_cycle_html(item: dict, hub: dict) -> str:
    year = int(item.get("anio") or 2026)
    nxt = year + 1
    note = hub.get("next_cycle") or (
        f"Cuando se publique la convocatoria {nxt}, esta página pasa a ese proceso y el de {year} queda como referencia."
    )
    return (
        '<aside class="next-cycle" role="note">'
        '<p class="source-kicker">Siguiente proceso</p>'
        f"<p>{escape(note)}</p>"
        "</aside>"
    )


def fechas_section(item: dict, hub: dict) -> str:
    rows = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>" for label, text in hub["fechas"]
    )
    return (
        '<section class="content hub-section" id="fechas" aria-labelledby="fechas-title">'
        f'<h2 id="fechas-title">Calendario {escape(str(item.get("anio", "")))}</h2>'
        f"<p>{escape(hub['fechas_lead'])}</p>"
        f'<dl class="source-facts">{rows}</dl>'
        f"{extra_paras(hub.get('fechas_extra'))}"
        f"{next_cycle_html(item, hub)}"
        "</section>"
    )


def notas_section(item: dict, hub: dict) -> str:
    rows = "".join(
        f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>"
        for a, b, c, d in hub["notas"]
    )
    note = f"<p>{escape(hub['notas_note'])}</p>" if hub.get("notas_note") else ""
    return (
        '<section class="content hub-section" id="notas-corte" aria-labelledby="notas-title">'
        f'<h2 id="notas-title">Notas de corte y mínimos</h2>'
        f"<p>{escape(hub['notas_lead'])}</p>"
        '<div class="table-scroll"><table class="plain-table"><thead><tr><th>Convocatoria</th><th>Dato</th><th>Qué es</th><th>Fuente</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
        f"{note}"
        f"{extra_paras(hub.get('notas_extra'))}"
        "</section>"
    )


def _exam_links(links: list) -> str:
    return "".join(f"<li>{ext_a(url, label)}</li>" for url, label in links)


def examenes_section(item: dict, hub: dict) -> str:
    family = family_id(item)
    exam = EXAMENES.get(family, {})
    lead = exam.get("lead") or hub.get("examenes_lead", "")
    groups = exam.get("groups") or hub.get("examenes", [])
    blocks = [f"<p>{escape(lead)}</p>"]
    for group in groups:
        blocks.append(f"<h3>{escape(group['year'])}</h3>")
        if group.get("note"):
            blocks.append(f"<p>{escape(group['note'])}</p>")
        if group.get("links"):
            blocks.append(f"<ul>{_exam_links(group['links'])}</ul>")
        for sub in group.get("subgroups") or []:
            blocks.append(f"<h4>{escape(sub['title'])}</h4>")
            if sub.get("note"):
                blocks.append(f'<p class="notice">{escape(sub["note"])}</p>')
            cls = ' class="exam-sedes"' if sub.get("kind") == "sedes" else ""
            blocks.append(f"<ul{cls}>{_exam_links(sub['links'])}</ul>")
    blocks.append(extra_paras(hub.get("examenes_extra")))
    return (
        '<section class="content hub-section" id="examenes-oficiales" aria-labelledby="examenes-title">'
        '<h2 id="examenes-title">Exámenes y plantillas oficiales</h2>'
        f"{''.join(blocks)}"
        "</section>"
    )


def hub_home(item: dict, hub: dict) -> str:
    prefix = rel_prefix(2)
    family = family_id(item)
    name = hub["name"]
    calc = prefix + live_path(item) + "index.html"
    pages = hub.get("pages") or []
    tiles = []
    for key, title, text in hub["tiles"]:
        if key in HUB_ANCHORS:
            continue
        href = hub_tile_href(key, prefix, family, item)
        extra = ' rel="noopener noreferrer"' if href.startswith("http") else ""
        tiles.append(
            f'<a class="card" href="{escape(href)}"{extra}><h3>{escape(title)}</h3><p>{escape(text)}</p></a>'
        )
    portal = hub.get("portal")
    if portal:
        url, title, text = portal
        tiles.append(
            f'<a class="card" href="{escape(url)}" rel="noopener noreferrer"><h3>{escape(title)}</h3><p>{escape(text)}</p></a>'
        )
    status = "".join(
        f'<div><p class="status-kicker">{escape(k)}</p><p class="status-value">{escape(v)}</p><p>{escape(n)}</p></div>'
        for k, v, n in hub["status"]
    )
    extra_btn = ""
    if "fisicas" in pages:
        extra_btn += (
            f'<a class="button button-secondary" href="{prefix}oposiciones/{family}/pruebas-fisicas/index.html">'
            "Calcular físicas</a>"
        )
    if "baremo" in pages:
        extra_btn += (
            f'<a class="button button-secondary" href="{prefix}oposiciones/{family}/baremo/index.html">'
            "Calcular baremo</a>"
        )
    scope = f'<p class="lede">{escape(hub["scope_note"])}</p>' if hub.get("scope_note") else ""
    sections = []
    if "requisitos" in pages:
        sections.append(requisitos_section(item, hub))
    if "pruebas" in pages:
        sections.append(pruebas_summary(prefix, family, hub))
    if "fechas" in pages:
        sections.append(fechas_section(item, hub))
    if "notas" in pages:
        sections.append(notas_section(item, hub))
    if "examenes" in pages:
        sections.append(examenes_section(item, hub))
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), (name, "")], f"oposiciones/{family}/")}
    <div class="hero">
      <p class="eyebrow">{escape(hub["eyebrow"])}</p>
      <h1>{escape(hub["h1"])}</h1>
      <p class="calc-badge">{escape(hub["badge"])}</p>
      {scope}
      {hub_nav(family, prefix, "hub")}
      <p class="hero-actions"><a class="button button-primary" href="{calc}">Calcular mi nota</a>{extra_btn}</p>
    </div>
    <section class="status-board" aria-label="Situación del proceso">{status}</section>
    <p class="status-updated">Calendario y estado revisados el {REVIEWED_ON} con las fuentes oficiales. Convocatoria: {ext_a(item["source_url"], item.get("source_identifier", "BOE"))}.</p>
    {timeline_html(hub.get("timeline"))}
    {changelog_html(hub)}
    {"".join(sections)}
    <h2 class="section-title">Herramientas y páginas de esta oposición</h2>
    <div class="hub-grid">{"".join(tiles)}</div>
    """
    return page_shell(
        seo_title(name, item.get("anio", "")),
        hub.get("description")
        or f"{name} {item.get('anio', '')}: estado del proceso, requisitos, calendario, notas de corte, exámenes oficiales y calculadora ({item.get('source_identifier', '')}).",
        f"oposiciones/{family}/",
        2,
        body,
    )


def hub_section(item: dict, hub: dict, slug: str, nav_key: str, title: str, h1: str, description: str, inner: str, page_title: str | None = None) -> str:
    prefix = rel_prefix(3)
    family = family_id(item)
    name = hub["name"]
    year = item.get("anio", "")
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        (name, prefix + f"oposiciones/{family}/index.html"),
        (title, ""),
    ], f"oposiciones/{family}/{slug}/")}
    <div class="hero">
      <h1>{escape(h1)}</h1>
      {hub_nav(family, prefix, nav_key)}
    </div>
    <section class="content">
      {inner}
      <p>Fuente: {ext_a(item["source_url"], item.get("source_identifier", "BOE"))}. Revisado el {REVIEWED_ON}.</p>
    </section>
    """
    return page_shell(
        page_title or seo_title(title, name, year),
        description,
        f"oposiciones/{family}/{slug}/",
        3,
        body,
    )


def hub_pruebas(item: dict, hub: dict) -> str:
    prefix = rel_prefix(3)
    family = family_id(item)
    name = hub["name"]
    steps = []
    for entry in hub["pruebas"]:
        text, link, tags = unpack_prueba(entry)
        tag_html = "".join(f'<span class="flow-tag">{escape(tag)}</span>' for tag in tags)
        if link == "calc":
            href = prefix + live_path(item) + "index.html"
            steps.append(f'<li>{escape(text)} {tag_html} <a href="{href}">Calcular esta prueba →</a></li>')
        elif link == "fisicas":
            href = f"{prefix}oposiciones/{family}/pruebas-fisicas/index.html"
            steps.append(f'<li>{escape(text)} {tag_html} <a href="{href}">Calcular esta prueba →</a></li>')
        elif link == "baremo":
            href = f"{prefix}oposiciones/{family}/baremo/index.html"
            steps.append(f'<li>{escape(text)} {tag_html} <a href="{href}">Calcular esta prueba →</a></li>')
        else:
            steps.append(f"<li>{escape(text)} {tag_html}</li>")
    inner = (
        f"<p>{escape(hub['pruebas_lead'])}</p>"
        f"{process_flow(hub)}"
        f'<ol class="how-steps">{"".join(steps)}</ol>'
        f"{extra_paras(hub.get('pruebas_extra'))}"
        f"{fisicas_tables_html(family)}"
        f'<p>Requisitos, calendario y notas de corte: <a href="{prefix}oposiciones/{family}/index.html">página de {escape(name)}</a>.</p>'
    )
    return hub_section(
        item, hub, "pruebas", "pruebas", "Pruebas",
        f"Cómo es la oposición de {name}",
        f"Pruebas y proceso de {name} {item.get('anio', '')} según la convocatoria oficial.",
        inner,
    )


def hub_temario(item: dict, hub: dict) -> str:
    name = hub["name"]
    blocks = []
    for heading, temas in hub["temario"].items():
        lis = "".join(f"<li><strong>Tema {n}.</strong> {escape(title)}</li>" for n, title in temas)
        blocks.append(f'<h2>{escape(heading)}</h2><ol class="tema-list">{lis}</ol>')
    inner = f"<p>{escape(hub['temario_lead'])}</p>" + "".join(blocks) + extra_paras(hub.get("temario_extra"))
    return hub_section(
        item, hub, "temario", "temario", "Temario",
        f"Temario {name} {item.get('anio', '')}",
        f"Índice oficial del temario de {name} {item.get('anio', '')}.",
        inner,
    )


def generic_hub(item: dict) -> str:
    prefix = rel_prefix(2)
    family = family_id(item)
    name = item.get("family_name") or item["short_name"]
    year = item.get("anio")
    calc = prefix + live_path(item) + "index.html"
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), (name, "")], f"oposiciones/{family}/")}
    <div class="hero">
      <p class="eyebrow">Convocatoria {escape(str(year))}</p>
      <h1>{escape(item.get("name") or name)}</h1>
      <p class="lede">{escape(item.get("lede", ""))}</p>
      {hub_nav(family, prefix, "hub")}
      <p class="hero-actions"><a class="button button-primary" href="{calc}">Calcular mi nota</a>
      <a class="button button-secondary" href="{prefix}fuentes/index.html">Ver fuente oficial</a></p>
    </div>
    <section class="content">
      <dl class="source-facts">
        <div><dt>Convocatoria</dt><dd>{escape(item.get("convocatoria", ""))}</dd></div>
        <div><dt>Organismo</dt><dd>{escape(item.get("administracion", ""))}</dd></div>
        <div><dt>Boletín</dt><dd>{escape(item.get("source_identifier", ""))}</dd></div>
        <div><dt>Apartado de la fórmula</dt><dd>{escape(item.get("source_section", ""))}</dd></div>
      </dl>
      <p>Requisitos, temario y calendario salen de esa convocatoria. Aquí no se resume lo que el boletín no deja calcular. Abre la calculadora o el PDF oficial.</p>
      <p>{ext_a(item.get("source_url") or item["fuente_oficial"]["url"], "Abrir el BOE")}</p>
    </section>
    """
    return page_shell(
        f"{name} {year} — {BRAND}",
        f"{name}: calculadora de nota de la convocatoria {year} con fuente {item.get('source_identifier', '')}.",
        f"oposiciones/{family}/",
        2,
        body,
    )


def prune_family_dir(family: str, keep: set[str]) -> None:
    base = ROOT / "oposiciones" / family
    if not base.exists():
        return
    for child in base.iterdir():
        if child.is_dir() and child.name not in keep:
            shutil.rmtree(child)


def write_hubs(opos: list[dict]) -> list[str]:
    urls = [f"{SITE}/oposiciones/"]
    write(ROOT / "oposiciones" / "index.html", oposiciones_index(opos))
    by_family = {family_id(item): item for item in current_by_family(opos)}
    writers = {"pruebas": hub_pruebas, "temario": hub_temario}
    for family, item in by_family.items():
        hub = HUBS.get(family)
        if not hub:
            write(ROOT / "oposiciones" / family / "index.html", generic_hub(item))
            urls.append(f"{SITE}/oposiciones/{family}/")
            continue
        write(ROOT / "oposiciones" / family / "index.html", hub_home(item, hub))
        urls.append(f"{SITE}/oposiciones/{family}/")
        kept = set()
        for key in hub.get("pages") or []:
            if key not in STANDALONE:
                continue
            if key == "fisicas":
                if family == "policia-nacional":
                    page = pn_fisicas_page(item)
                elif family == "guardia-civil":
                    page = gc_fisicas_page(item)
                elif family == "policia-local":
                    page = pl_fisicas_page(item)
                else:
                    continue
            elif key == "baremo":
                page = gc_baremo_page(item)
            else:
                page = writers[key](item, hub)
            write(ROOT / "oposiciones" / family / HUB_SLUGS[key] / "index.html", page)
            urls.append(f"{SITE}/oposiciones/{family}/{HUB_SLUGS[key]}/")
            kept.add(HUB_SLUGS[key])
        prune_family_dir(family, kept)
    return urls
