"""Hubs de oposición: índice, fichas y secciones."""

from __future__ import annotations

from xml.sax.saxutils import escape

from examenes_oficiales import EXAMENES
from fisicas_tables import fisicas_tables_html
from html_shell import crumbs, extra_paras, page_shell, pretty_href, rel_prefix, seo_title, write
from hub_nav import HUB_SLUGS, hub_nav
from hub_tools import gc_baremo_page, gc_fisicas_page, pl_fisicas_page, pn_fisicas_page
from hubs_data import HUBS
from pl_directorio import write_all as write_pl_directorio
from site_catalog import catalog_cards, current_by_family, family_id, live_path, opo_search_form
from site_config import BRAND, ROOT, SITE
from site_widgets import (
    changelog_html,
    es_date,
    ext_a,
    process_flow,
    report_error_link,
    result_persist_actions,
    source_link,
    timeline_html,
    unpack_prueba,
)


def oposiciones_index(opos: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Oposiciones", "")], "oposiciones/")}
    <div class="hero">
      <h1>Oposiciones</h1>
      <p class="lede">Tu convocatoria, tus pruebas y tu calculadora. Cada cuerpo con su boletín. Sin temario de academia ni cortes inventados.</p>
      {opo_search_form()}
    </div>
    <div class="catalog" id="opo-catalog">{catalog_cards(opos, "../", dest="hub")}</div>
    <p id="opo-search-empty" class="search-empty" hidden>No hay una oposición con ese nombre en TuNotaOpo. Prueba PN, GC, local, AGE, IIPP o auxilio.</p>
    """
    return page_shell(
        seo_title("Oposiciones"),
        "Policía Nacional, Guardia Civil, Policía Local por ciudad y municipio, Auxiliar AGE, Auxilio Judicial y Ayudantes IIPP: calculadora solo con boletín oficial.",
        "oposiciones/",
        1,
        body,
    )


def hub_tile_href(key: str, prefix: str, family: str, item: dict) -> str:
    if key == "calc":
        return prefix + live_path(item) + "index.html"
    if key.startswith("http"):
        return key
    return f"{prefix}oposiciones/{family}/{HUB_SLUGS[key]}/index.html"


def hub_home(item: dict, hub: dict) -> str:
    prefix = rel_prefix(2)
    family = family_id(item)
    name = hub["name"]
    calc = prefix + live_path(item) + "index.html"
    tiles = []
    for key, title, text in hub["tiles"]:
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
    if "fisicas" in hub.get("pages", []):
        extra_btn += (
            f'<a class="button button-secondary" href="{prefix}oposiciones/{family}/pruebas-fisicas/index.html">'
            "Calcular físicas</a>"
        )
    if "baremo" in hub.get("pages", []):
        extra_btn += (
            f'<a class="button button-secondary" href="{prefix}oposiciones/{family}/baremo/index.html">'
            "Calcular baremo</a>"
        )
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), (name, "")], f"oposiciones/{family}/")}
    <div class="hero">
      <p class="eyebrow">{escape(hub["eyebrow"])}</p>
      <h1>{escape(hub["h1"])}</h1>
      <p class="calc-badge">{escape(hub["badge"])}</p>
      {hub_nav(family, prefix, "hub")}
      <p class="hero-actions"><a class="button button-primary" href="{calc}">Calcular mi nota</a>{extra_btn}</p>
    </div>
    <section class="status-board" aria-label="Datos de la convocatoria">{status}</section>
    <p class="status-updated">Última revisión de estas páginas: 19 de agosto de 2026. Fuente: {ext_a(item["source_url"], item.get("source_identifier", "BOE"))}.</p>
    {timeline_html(hub.get("timeline"))}
    {process_flow(hub)}
    {changelog_html(hub)}
    <div class="hub-grid">{"".join(tiles)}</div>
    """
    return page_shell(
        seo_title(name, item.get("anio", "")),
        f"{name} {item.get('anio', '')}: calculadora, proceso, temario índice y fuentes oficiales ({item.get('source_identifier', '')}).",
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
      <p>Fuente: {ext_a(item["source_url"], item.get("source_identifier", "BOE"))}. Consultado el 19 de agosto de 2026.</p>
    </section>
    """
    return page_shell(
        page_title or seo_title(title, name, year),
        description,
        f"oposiciones/{family}/{slug}/",
        3,
        body,
    )


def hub_requisitos(item: dict, hub: dict) -> str:
    name = hub["name"]
    year = item.get("anio", "")
    rows = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>" for label, text in hub["requisitos"]
    )
    family = family_id(item)
    extra_btn = ""
    if "fisicas" in hub.get("pages", []):
        extra_btn = (
            f' <a class="button button-secondary" href="{rel_prefix(3)}oposiciones/{family}/pruebas/index.html#tablas-fisicas">'
            "Ver marcas de las físicas</a>"
        )
    inner = (
        f"<p>{escape(hub['requisitos_lead'])}</p>"
        f'<dl class="source-facts">{rows}</dl>'
        f"{extra_paras(hub.get('requisitos_extra'))}"
        f'<p class="hero-actions"><a class="button button-primary" href="{rel_prefix(3)}{live_path(item)}index.html">Calcular mi nota</a>{extra_btn}</p>'
    )
    return hub_section(
        item, hub, "requisitos", "requisitos", "Requisitos",
        f"Requisitos {name} {year}",
        f"Requisitos de {name} {year} según {item.get('source_identifier', 'la convocatoria oficial')}.",
        inner,
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
    inner = f"<p>{escape(hub['temario_lead'])}</p>" + "".join(blocks)
    return hub_section(
        item, hub, "temario", "temario", "Temario",
        f"Temario {name} {item.get('anio', '')}",
        f"Índice oficial del temario de {name} {item.get('anio', '')}.",
        inner,
    )


def next_cycle_html(item: dict, hub: dict) -> str:
    year = item.get("anio") or 2026
    nxt = int(year) + 1
    name = hub["name"]
    return f"""<aside class="next-cycle" role="note">
      <p class="source-kicker">Siguiente proceso</p>
      <h2>{escape(name)} {nxt}</h2>
      <p>No hay convocatoria {nxt} en el BOE. Esta página es el calendario <strong>en vigor</strong> ({escape(str(year))}), no un pronóstico.</p>
      <p>Las IAs y muchas academias desplazan el año pasado (OEP en primavera, examen en verano, «mismas plazas»). Eso no es una norma. {BRAND} no publica meses inventados ni copia las plazas de {escape(str(year))}.</p>
      <p>Cuando salga la resolución {nxt}, se actualiza esta misma dirección: plazos, citaciones y, si cambia, la fórmula. Hasta entonces el calendario útil es el de {escape(str(year))}.</p>
    </aside>"""


def hub_fechas(item: dict, hub: dict) -> str:
    name = hub["name"]
    rows = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>" for label, text in hub["fechas"]
    )
    inner = (
        f"<p>{escape(hub['fechas_lead'])}</p>"
        f"{timeline_html(hub.get('timeline'))}"
        f'<dl class="source-facts">{rows}</dl>'
        f"{extra_paras(hub.get('fechas_extra'))}"
        f"{next_cycle_html(item, hub)}"
    )
    return hub_section(
        item, hub, "fechas", "fechas", "Fechas",
        f"Fechas {name} {item.get('anio', '')}",
        f"Calendario de {name} {item.get('anio', '')} según fuentes oficiales.",
        inner,
    )


def hub_notas(item: dict, hub: dict) -> str:
    name = hub["name"]
    rows = "".join(
        f"<tr><td>{escape(a)}</td><td>{escape(b)}</td><td>{escape(c)}</td><td>{escape(d)}</td></tr>"
        for a, b, c, d in hub["notas"]
    )
    inner = (
        f"<p>{escape(hub['notas_lead'])}</p>"
        '<table class="plain-table"><thead><tr><th>Convocatoria</th><th>Dato</th><th>Qué es</th><th>Fuente</th></tr></thead>'
        f"<tbody>{rows}</tbody></table>"
        f"<p>{escape(hub.get('notas_note', ''))}</p>"
        f"{extra_paras(hub.get('notas_extra'))}"
    )
    return hub_section(
        item, hub, "notas-corte", "notas", "Notas de corte",
        f"Histórico de notas {name}",
        f"Histórico de notas y cortes de {name} solo con fuente oficial.",
        inner,
        page_title=seo_title("Notas de corte", name),
    )


def _exam_links(links: list) -> str:
    return "".join(f"<li>{ext_a(url, label)}</li>" for url, label in links)


def hub_examenes(item: dict, hub: dict) -> str:
    name = hub["name"]
    family = family_id(item)
    exam = EXAMENES.get(family, {})
    lead = exam.get("lead") or hub.get("examenes_lead", "")
    groups = exam.get("groups") or hub.get("examenes", [])
    blocks = [f"<p>{escape(lead)}</p>"]
    for group in groups:
        blocks.append(f"<h2>{escape(group['year'])}</h2>")
        if group.get("note"):
            blocks.append(f"<p>{escape(group['note'])}</p>")
        if group.get("links"):
            blocks.append(f"<ul>{_exam_links(group['links'])}</ul>")
        for sub in group.get("subgroups") or []:
            blocks.append(f"<h3>{escape(sub['title'])}</h3>")
            if sub.get("note"):
                blocks.append(f'<p class="notice">{escape(sub["note"])}</p>')
            cls = ' class="exam-sedes"' if sub.get("kind") == "sedes" else ""
            blocks.append(f"<ul{cls}>{_exam_links(sub['links'])}</ul>")
    blocks.append(extra_paras(hub.get("examenes_extra")))
    return hub_section(
        item, hub, "examenes-oficiales", "examenes", "Exámenes oficiales",
        f"Exámenes oficiales {name}",
        f"Exámenes y plantillas oficiales de {name}, enlazados a la administración.",
        "".join(blocks),
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


def pn_hub(item: dict) -> str:
    prefix = rel_prefix(2)
    family = "policia-nacional"
    calc = prefix + live_path(item) + "index.html"
    tiles = [
        (calc, "Calculadora de nota", "Test de conocimientos según la base 6.1.1."),
        (f"{prefix}oposiciones/{family}/pruebas-fisicas/index.html", "Pruebas físicas", "Circuito, fuerza y 1.000 m con el anexo II."),
        (f"{prefix}oposiciones/{family}/temario/index.html", "Temario", "Índice oficial del anexo I. No es el tema desarrollado."),
        (f"{prefix}oposiciones/{family}/requisitos/index.html", "Requisitos", "Edad, título, idioma A2, permiso B."),
        (f"{prefix}oposiciones/{family}/fechas/index.html", "Fechas", "Lo que fija el BOE. Sin examen inventado."),
        (f"{prefix}oposiciones/{family}/pruebas/index.html", "Pruebas", "De conocimientos al curso de formación."),
        (f"{prefix}oposiciones/{family}/notas-corte/index.html", "Notas anteriores", "Corte aproximado 2025. El de 2026 aún no."),
        ("https://www.policia.es/portalaspirantes", "Portal del Aspirante", "Listas, citaciones y documentos oficiales."),
    ]
    cards = "".join(
        (
            f'<a class="card" href="{escape(href)}"'
            + (' rel="noopener noreferrer"' if href.startswith("http") else "")
            + f"><h3>{escape(title)}</h3><p>{escape(text)}</p></a>"
        )
        for href, title, text in tiles
    )
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), ("Policía Nacional", "")], "oposiciones/policia-nacional/")}
    <div class="hero">
      <p class="eyebrow">Escala Básica · categoría de Policía</p>
      <h1>Policía Nacional — oposición 2026</h1>
      <p class="calc-badge">Convocatoria publicada · BOE-A-2026-15055 · En curso</p>
      {hub_nav(family, prefix, "hub")}
      <p class="hero-actions"><a class="button button-primary" href="{calc}">Calcular mi nota</a>
      <a class="button button-secondary" href="{prefix}oposiciones/{family}/pruebas-fisicas/index.html">Calcular físicas</a></p>
    </div>
    <section class="status-board" aria-label="Datos de la convocatoria">
      <div><p class="status-kicker">Plazas</p><p class="status-value">2.704</p><p>2.163 libres · 541 tropa y marinería</p></div>
      <div><p class="status-kicker">Convocatoria</p><p class="status-value">Publicada</p><p>10 de julio de 2026</p></div>
      <div><p class="status-kicker">Solicitudes</p><p class="status-value">Plazo cerrado</p><p>15 días hábiles desde el 11 de julio</p></div>
      <div><p class="status-kicker">Examen</p><p class="status-value">Por anunciar</p><p>Portal del Aspirante. Aquí no se inventa la fecha.</p></div>
    </section>
    <p class="status-updated">Última revisión de estas páginas: 19 de agosto de 2026. Fuente: {ext_a(item["source_url"], "BOE-A-2026-15055")}.</p>
    <div class="hub-grid" id="calculadora">{cards}</div>
    """
    return page_shell(
        f"Policía Nacional Escala Básica 2026 — {BRAND}",
        "Oposición Policía Nacional Escala Básica 2026: calculadora de nota, físicas del anexo II, requisitos, temario índice y fechas según BOE-A-2026-15055.",
        "oposiciones/policia-nacional/",
        2,
        body,
    )


def pn_simple_section(item: dict, slug: str, title: str, h1: str, description: str, inner: str, current: str) -> str:
    prefix = rel_prefix(3)
    family = "policia-nacional"
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Nacional", prefix + "oposiciones/policia-nacional/index.html"),
        (title, ""),
    ], f"oposiciones/{family}/{slug}/")}
    <div class="hero">
      <h1>{escape(h1)}</h1>
      {hub_nav(family, prefix, current)}
    </div>
    <section class="content">
      {inner}
      <p>Fuente: {ext_a(item["source_url"], "BOE-A-2026-15055")}. Consultado el 19 de agosto de 2026.</p>
    </section>
    """
    return page_shell(f"{title} — {BRAND}", description, f"oposiciones/{family}/{slug}/", 3, body)


def pn_requisitos(item: dict) -> str:
    rows = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{escape(text)}</dd></div>" for label, text in PN_REQUISITOS
    )
    inner = (
        "<p>Requisitos a la fecha de fin de solicitudes, en lenguaje claro. El texto que manda es la base 2.1.1 de la convocatoria.</p>"
        f'<dl class="source-facts">{rows}</dl>'
        f'<p class="hero-actions"><a class="button button-primary" href="{rel_prefix(3)}{live_path(item)}index.html">Calcular mi nota</a></p>'
    )
    return pn_simple_section(
        item,
        "requisitos",
        "Requisitos",
        "Requisitos Policía Nacional 2026",
        "Requisitos de Policía Nacional Escala Básica 2026: edad, nacionalidad, Bachiller, permiso B e idioma A2, según BOE-A-2026-15055.",
        inner,
        "requisitos",
    )


def pn_pruebas(item: dict) -> str:
    steps = [
        "Conocimientos — test de 100 preguntas, 3 opciones, 50 minutos. Mínimo 3. Solo siguen 1,75 aspirantes por plaza de turno libre.",
        "Aptitud física — circuito, fuerza y 1.000 m. Cero en un ejercicio elimina. Media mínima 5.",
        "Reconocimiento médico — apto o no apto.",
        "Entrevista profesional y personal — apto o no apto.",
        "Test psicotécnicos — apto o no apto, con el mínimo que fije el tribunal.",
        "Curso de formación en la Escuela Nacional de Policía.",
        "Módulo de formación práctica en puesto de trabajo.",
    ]
    inner = (
        "<p>Fase de oposición, luego curso y prácticas (base 1.2 y 6.1). Cada prueba enlaza a la herramienta si existe.</p>"
        '<ol class="how-steps">'
        + "".join(f"<li>{escape(s)}</li>" for s in steps)
        + "</ol>"
        f'<p><a href="{rel_prefix(3)}{live_path(item)}index.html">Calculadora de conocimientos</a> · '
        f'<a href="{rel_prefix(3)}oposiciones/policia-nacional/pruebas-fisicas/index.html">Calculadora de físicas</a></p>'
    )
    return pn_simple_section(
        item,
        "pruebas",
        "Pruebas",
        "Cómo es la oposición de Policía Nacional",
        "Pruebas de Policía Nacional Escala Básica 2026: conocimientos, físicas, médico, entrevista y psicotécnico, según la convocatoria.",
        inner,
        "pruebas",
    )


def pn_temario(item: dict) -> str:
    blocks = []
    for heading, temas in PN_TEMAS.items():
        lis = "".join(f"<li><strong>Tema {n}.</strong> {escape(title)}</li>" for n, title in temas)
        blocks.append(f'<h2>{escape(heading)}</h2><ol class="tema-list">{lis}</ol>')
    inner = (
        "<p>Índice del anexo I. No es el temario desarrollado: no sustituye el boletín ni un manual.</p>"
        + "".join(blocks)
    )
    return pn_simple_section(
        item,
        "temario",
        "Temario",
        "Temario Policía Nacional 2026",
        "Índice oficial del temario de Policía Nacional Escala Básica 2026 (anexo I, BOE-A-2026-15055).",
        inner,
        "temario",
    )


def pn_fechas(item: dict) -> str:
    inner = """
      <p>Solo fechas que salen de la convocatoria o que se deducen de ella. El día del examen no está en el BOE: se publica en el Portal del Aspirante.</p>
      <dl class="source-facts">
        <div><dt>Convocatoria en el BOE</dt><dd>10 de julio de 2026</dd></div>
        <div><dt>Plazo de solicitudes</dt><dd>15 días hábiles desde el 11 de julio de 2026. Ese plazo ya terminó.</dd></div>
        <div><dt>Lista de admitidos</dt><dd>Se publica en el BOE (excluidos) y consulta individual en el Portal del Aspirante.</dd></div>
        <div><dt>Examen de conocimientos</dt><dd>Pendiente de anuncio oficial. No se estima aquí.</dd></div>
        <div><dt>Pruebas siguientes</dt><dd>Las cita el tribunal. Portal del Aspirante: policia.es/portalaspirantes</dd></div>
      </dl>
    """
    return pn_simple_section(
        item,
        "fechas",
        "Fechas",
        "Fechas Policía Nacional 2026",
        "Calendario de Policía Nacional Escala Básica 2026: convocatoria, plazo de solicitudes y lo que aún debe anunciar el tribunal.",
        inner,
        "fechas",
    )


def pn_notas(item: dict) -> str:
    inner = """
      <p>El mínimo 3 no es el corte. El corte de plaza lo marca el resto de aspirantes.</p>
      <table class="plain-table">
        <thead><tr><th>Convocatoria</th><th>Dato</th><th>Qué es</th><th>Fuente</th></tr></thead>
        <tbody>
          <tr><td>2026</td><td>Pendiente</td><td>Corte de conocimientos de esta promoción</td><td>Aún no publicado</td></tr>
          <tr><td>2025</td><td>7,17 aproximado</td><td>Corte de la prueba de conocimientos (promoción 42)</td><td>Portal del Aspirante, 3-11-2025</td></tr>
        </tbody>
      </table>
      <p>No hay lista pública de todos los examinados de 2025, así que no se da un número de orden.</p>
    """
    return pn_simple_section(
        item,
        "notas-corte",
        "Notas de corte",
        "Histórico de notas Policía Nacional",
        "Corte de conocimientos de Policía Nacional: 7,17 aproximado en 2025 (Portal del Aspirante). El de 2026, cuando salga.",
        inner,
        "notas",
    )


def write_hubs(opos: list[dict]) -> list[str]:
    urls = [f"{SITE}/oposiciones/"]
    write(ROOT / "oposiciones" / "index.html", oposiciones_index(opos))
    by_family = {family_id(item): item for item in current_by_family(opos)}
    writers = {
        "requisitos": hub_requisitos,
        "pruebas": hub_pruebas,
        "temario": hub_temario,
        "fechas": hub_fechas,
        "notas": hub_notas,
        "examenes": hub_examenes,
    }
    for family, item in by_family.items():
        hub = HUBS.get(family)
        if not hub:
            write(ROOT / "oposiciones" / family / "index.html", generic_hub(item))
            urls.append(f"{SITE}/oposiciones/{family}/")
            continue
        if family != "policia-local":
            write(ROOT / "oposiciones" / family / "index.html", hub_home(item, hub))
            urls.append(f"{SITE}/oposiciones/{family}/")
        for key in hub.get("pages") or []:
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
    if "policia-local" in by_family:
        urls.extend(write_pl_directorio(by_family["policia-local"], HUBS["policia-local"]))
    return urls
