#!/usr/bin/env python3
"""Generate indexable static pages from opposition configs."""

from __future__ import annotations

import json
import shutil
from urllib.parse import quote
from xml.sax.saxutils import escape

from content import DISCLAIMER, PAGES
from html_shell import (
    ad_slot,
    crumbs,
    embed_shell,
    legal_identity,
    page_shell,
    pretty_href,
    rel_prefix,
    seo_title,
    write,
)
from hub_pages import write_hubs
from hubs_data import HUBS
from site_assets import write_generated_assets
from site_catalog import (
    card_tests,
    catalog_cards,
    current_by_family,
    family_id,
    live_path,
    opo_search_form,
    path_depth,
)
from site_config import (
    ACADEMIAS_PATH,
    BRAND,
    CONTACT_EMAIL,
    DATA_DIR,
    FEATURED_FAMILIES,
    ADSENSE_PUBLISHER,
    LASTMOD,
    PROGRESO_PATH,
    ROOT,
    SITE,
)
from site_widgets import (
    boe_pdf_url,
    calculator_form,
    es_date,
    ext_a,
    form_guide,
    report_error_link,
    source_link,
)


def with_historical(cfg: dict) -> dict:
    packed = json.loads(json.dumps(cfg))
    hist = packed.get("historical")
    if not hist:
        return packed
    rel = hist.pop("scores_file", None)
    if rel:
        payload = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        hist["scores"] = payload["scores"]
        hist["n"] = payload.get("n") or len(payload["scores"])
        hist["cut"] = payload.get("cut", payload["scores"][-1] if payload.get("scores") else None)
        hist["source_identifier"] = hist.get("source_identifier") or payload.get("source_identifier")
        hist["source_url"] = hist.get("source_url") or payload.get("source_url")
        hist["label"] = hist.get("label") or payload.get("label")
        hist["year"] = hist.get("year") or payload.get("year")
    return packed


def load_oposiciones() -> list[dict]:
    items = []
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status", "published") == "published":
            items.append(data)
    return items


def related_cards(current: dict, all_items: list[dict], prefix: str, ads: bool = True) -> str:
    cards = []
    current_family = family_id(current)
    for item in current_by_family(all_items):
        if family_id(item) == current_family:
            continue
        if family_id(item) == "policia-local":
            href = prefix + "oposiciones/policia-local/index.html"
            name = "Policía Local"
            cta = "Ver Madrid"
            kind = "Calculadora solo con boletín. Hoy: Policía Municipal de Madrid."
        else:
            href = prefix + live_path(item) + "index.html"
            name = item.get("family_name") or item["short_name"]
            cta = "Calcular nota"
            kind = card_tests(item)
        cards.append(
            f'<a class="card" href="{href}"><span class="badge">En vigor</span>'
            f'<h3>{escape(name)}</h3><p>{escape(kind)}</p>'
            f'<span class="card-cta">{escape(cta)}</span></a>'
        )
    if not cards:
        return ""
    return (
        '<section class="related-block"><h2>Calculadoras relacionadas</h2><div class="related">'
        + "".join(cards)
        + "</div></section>"
        + (ad_slot("after-related") if ads else "")
    )


def list_block(title: str, items: list[str]) -> str:
    return f"<h2>{escape(title)}</h2><ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>"


def faq_block(faqs: list[tuple[str, str]]) -> str:
    bits = ["<h2>Preguntas frecuentes</h2>"]
    for q, a in faqs:
        bits.append(f"<h3>{escape(q)}</h3><p>{escape(a)}</p>")
    return "".join(bits)


def calc_kind(item: dict) -> str:
    models = {stage.get("model") for stage in item.get("stages") or []}
    parts = []
    if "scaled_score" in models:
        parts.append("Escala oficial")
    if "fixed_value" in models:
        parts.append("Valores fijos de la convocatoria")
    if "net_score" in models:
        parts.append("Puntuación directa")
    if "pass_fail_errors" in models or "pass_fail" in models:
        parts.append("Apto / no apto")
    if item.get("merits"):
        merit_label = (item["merits"].get("label") or "").lower()
        if "idioma" in merit_label:
            parts.append("Idiomas opcionales")
        else:
            parts.append("Concurso opcional")
    return " · ".join(parts) or (item.get("formula_human") or "")

def calculator_page(
    cfg: dict,
    all_items: list[dict],
    page_path: str,
    canonical_path: str,
    variant: str,
) -> str:
    copy = PAGES[cfg["slug"]]
    depth = path_depth(page_path)
    prefix = rel_prefix(depth)
    src = cfg.get("fuente_oficial") or {}
    family_name = cfg.get("family_name") or cfg["short_name"]
    family_path = cfg.get("family_path") or cfg["path"]
    hub = f"oposiciones/{family_id(cfg)}/"
    heading = cfg["h1"] if str(cfg.get("anio", "")) in cfg["h1"] else f'{cfg["h1"]} {cfg["anio"]}'
    crumb_items = [
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        (family_name, prefix + hub + "index.html"),
        ("Calculadora", ""),
    ]
    if variant == "archive":
        crumb_items = [
            ("Inicio", prefix + "index.html"),
            ("Calculadoras", prefix + "calculadoras/index.html"),
            (family_name, prefix + family_path + "index.html"),
            (f"Convocatoria {cfg['anio']}", ""),
        ]
        banner = (
            f'<p class="calc-badge">Archivo {escape(str(cfg["anio"]))} · {escape(cfg.get("source_identifier", ""))} '
            f'· <a href="{prefix}{family_path}index.html">Calculadora en vigor</a></p>'
        )
    else:
        banner = (
            f'<p class="calc-badge">Actualizada para la convocatoria {escape(str(cfg["anio"]))} · '
            f'{escape(cfg.get("source_identifier", ""))} · BOE oficial</p>'
        )
    faqs = [
        (
            "¿Sirve el año que viene?",
            "Sí. Esta es la calculadora de la oposición, no de un único año. Usas siempre la convocatoria en vigor. "
            "Si el próximo boletín cambia la fórmula, se actualiza esta página y la anterior queda en una URL de archivo.",
        )
    ] + list(copy["faqs"])
    extra_hub = ""
    hub_cfg = HUBS.get(family_id(cfg), {})
    if "fisicas" in hub_cfg.get("pages", []):
        extra_hub += f'<a href="{prefix}{hub}pruebas-fisicas/index.html">Pruebas físicas</a>'
    if "baremo" in hub_cfg.get("pages", []):
        extra_hub += f'<a href="{prefix}{hub}baremo/index.html">Baremo</a>'
    if "examenes" in hub_cfg.get("pages", []):
        extra_hub += f'<a href="{prefix}{hub}index.html#examenes-oficiales">Exámenes</a>'
    hub_links = (
        f'<nav class="opp-links" aria-label="Esta oposición">'
        f'<a href="{prefix}{hub}index.html">Oposición</a>'
        f'<a href="{prefix}{live_path(cfg)}index.html">Calcular nota</a>'
        + extra_hub
        + f'<a href="{prefix}fuentes/index.html">Fuentes</a></nav>'
    )
    body = f"""
    {crumbs(crumb_items, canonical_path)}
    <div class="hero hero-calc">
      <h1>{escape(heading)}</h1>
      {banner}
      {hub_links}
    </div>
    <div class="layout">
      <article class="tool">
        {calculator_form(cfg, prefix, f"{SITE}/{canonical_path}")}
        {"" if variant == "archive" else ad_slot("after-result")}
        <section class="source-card">
          <p class="source-kicker">De dónde sale la fórmula</p>
          <p class="source-id">{escape(cfg.get("source_identifier", ""))}</p>
          <p>Convocatoria: {escape(cfg["convocatoria"])}.</p>
          <p>Organismo: {escape(cfg["administracion"])}.</p>
          <p>Apartado usado: {escape(cfg.get("source_section", ""))}.</p>
          <p>Última revisión: {escape(str(cfg.get("last_verified") or src.get("reviewed_at", "")))}.</p>
          <p>{source_link(cfg)} <span aria-hidden="true">→</span></p>
        </section>
        {report_error_link(family_name, cfg["convocatoria"], f"{SITE}/{canonical_path}", "nota")}
        <p class="notice">{escape(DISCLAIMER)}</p>
      </article>
    </div>
    <section class="content">
      {form_guide(cfg)}
      <aside class="glossary" role="note">
        <h2>Tres ideas que no son lo mismo</h2>
        <dl>
          <div><dt>Mínimo oficial</dt><dd>El suelo que marcan las bases para esa prueba. Si no lo alcanzas, sueles quedar fuera de esa prueba.</dd></div>
          <div><dt>Nota de corte</dt><dd>La marca el resto de aspirantes cuando el tribunal publica la lista. Esta página no la inventa.</dd></div>
          <div><dt>Plaza</dt><dd>Depende de la lista final. Superar un mínimo no es obtener plaza.</dd></div>
        </dl>
      </aside>
      <h2>Cómo se calcula</h2>
      {''.join(f'<p>{escape(p)}</p>' for p in copy["how"])}
      <div class="formula-note">
        <h2>Fórmula de esta convocatoria</h2>
        <p>{escape(cfg["formula_human"])}</p>
      </div>
      {"" if variant == "archive" else ad_slot("in-content")}
      {list_block("Un ejemplo con números", copy["example"])}
      {list_block("Errores frecuentes al calcular", copy["mistakes"])}
      <h2>Fuente oficial</h2>
      <p>El enlace abre el boletín. Consultado el {escape(str(src.get("accessed_at", cfg.get("last_verified", ""))))}.</p>
      <p>{source_link(cfg)}.</p>
      {list_block("Qué no calcula esta página", copy["limits"])}
      {faq_block(faqs)}
      {related_cards(cfg, all_items, prefix, ads=variant != "archive")}
    </section>
    <script type="application/json" id="oposicion-config">{json.dumps(with_historical(cfg), ensure_ascii=False)}</script>
    """
    title = heading if heading == cfg["title"] else heading
    archive_alias = variant == "archive" and canonical_path.rstrip("/") != page_path.rstrip("/")
    return page_shell(
        f"{title} | {BRAND}",
        cfg["meta_description"],
        canonical_path,
        depth,
        body,
        calculator=True,
        noindex=archive_alias,
    )

def home(all_items: list[dict]) -> str:
    body = f"""
    <div class="hero hero-home">
      <p class="eyebrow">{BRAND}</p>
      <h1>Calculadoras de nota para oposiciones</h1>
      <p class="lede">Tu nota, con la fórmula de la convocatoria oficial. Elige el cuerpo, escribe aciertos y errores, y calcula con el boletín en vigor.</p>
      {opo_search_form()}
      <ul class="proof">
        <li><a href="/oposiciones/">Convocatoria en vigor</a></li>
        <li><a href="/privacidad/">Sin cuenta ni servidor</a></li>
        <li><a href="/fuentes/">Fuente oficial enlazada</a></li>
      </ul>
    </div>
    <section>
      <h2 class="section-title">Oposiciones</h2>
      <div class="catalog" id="opo-catalog">{catalog_cards(all_items, dest="hub")}</div>
      <p id="opo-search-empty" class="search-empty" hidden>No hay una oposición con ese nombre en TuNotaOpo. Prueba PN, GC, local, AGE, IIPP o auxilio.</p>
    </section>
    {ad_slot("home-mid")}
    <section class="content">
      <h2>Cómo funciona</h2>
      <ol class="how-steps">
        <li><strong>Entra en tu oposición.</strong> Ahí está la calculadora, el proceso y lo que dice el boletín. No es una media genérica para todos los cuerpos.</li>
        <li><strong>Escribe aciertos y errores.</strong> Los blancos se calculan solos. Si el tribunal anuló preguntas, cambia el número de preguntas válidas.</li>
        <li><strong>Lee el resultado con calma.</strong> Verás la puntuación y si llegas al mínimo oficial. Eso no es la nota de corte ni una plaza.</li>
      </ol>
      <p>No hay cuenta. El cálculo se hace en tu navegador. Los simulacros se quedan en este dispositivo: <a href="{pretty_href(PROGRESO_PATH)}">Mi progreso</a>. <a href="/fuentes/">Fuentes oficiales</a>.</p>
      <p>{escape(DISCLAIMER)}</p>
    </section>
    """
    return page_shell(
        f"{BRAND} — calculadoras de nota para oposiciones",
        "Calcula la nota de Guardia Civil, Policía Nacional, Policía Local por ciudad, IIPP, Auxilio Judicial y Auxiliar AGE. Cada fórmula sale del boletín. En el navegador.",
        "",
        0,
        body,
        website=True,
    )


def calculadoras_index(all_items: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Calculadoras", "")], "calculadoras/")}
    <div class="hero">
      <h1>Calculadoras de nota</h1>
      <p class="lede">Una calculadora por cuerpo, atada al boletín en vigor. Si cambia la fórmula, se actualiza aquí.</p>
    </div>
    <div class="catalog">{catalog_cards(all_items, "../")}</div>
    {ad_slot("catalog")}
    <section class="content">
      <h2>Cómo puntúa cada examen</h2>
      <p>No hay una regla común. Cada convocatoria fija cuánto vale un acierto, cuánto resta un error y qué mínimo hay que pasar. Por eso cada cuerpo tiene su calculadora y no sirve usar la de otro.</p>
      <div class="table-scroll"><table class="plain-table">
        <thead><tr><th>Oposición</th><th>Examen</th><th>Cómo resta el error</th><th>Mínimo de las bases</th></tr></thead>
        <tbody>
          <tr><td>Guardia Civil</td><td>Ortografía, gramática, 100 de conocimientos, 20 de inglés y psicotécnico</td><td>Un tercio de acierto (4 opciones) en las pruebas que puntúan</td><td>50 en conocimientos, 8 en inglés, 12 en psicotécnico; 6 errores eliminan en ortografía y gramática</td></tr>
          <tr><td>Policía Nacional</td><td>Test de 100 preguntas con 3 opciones</td><td>Medio acierto (3 opciones)</td><td>3 sobre 10; luego pasan 1,75 aspirantes por plaza</td></tr>
          <tr><td>Auxiliar AGE</td><td>60 preguntas + 50 de ofimática</td><td>Un tercio de acierto</td><td>Lo fija la Comisión cada año (29,00 y 21,33 en 2026)</td></tr>
          <tr><td>Auxilio Judicial</td><td>100 de teórico + 40 de práctico</td><td>0,15 en el teórico y 0,25 en el práctico</td><td>30 y 20</td></tr>
          <tr><td>Ayudantes IIPP</td><td>120 de test + 40 de supuestos</td><td>Un tercio de acierto</td><td>Lo fija el tribunal (67 y 26,6667 en 2026)</td></tr>
          <tr><td>Policía Municipal de Madrid</td><td>Temario (90 %) e idioma (10 %)</td><td>Un tercio de acierto</td><td>5 en cada parte; pasan 3,5 aspirantes por plaza</td></tr>
        </tbody>
      </table></div>
      <p>Las preguntas en blanco no restan en ninguna de estas convocatorias. El mínimo de las bases tampoco es la nota de corte: el corte real depende del número de plazas y de cómo salga el resto de aspirantes. Cada página de oposición muestra los cortes que ya ha publicado el tribunal.</p>
      <p>Todas las calculadoras funcionan en tu navegador. No piden cuenta y no envían tus aciertos a ningún servidor.</p>
    </section>
    """
    return page_shell(
        seo_title("Calculadoras de nota oposiciones"),
        "Calculadoras de Guardia Civil, Policía Nacional, Policía Municipal de Madrid, Ayudantes IIPP, Auxilio Judicial y Auxiliar AGE, con la penalización y los mínimos de cada convocatoria.",
        "calculadoras/",
        1,
        body,
    )


def ordered_opos(opos: list[dict]) -> list[dict]:
    rank = {family: index for index, family in enumerate(FEATURED_FAMILIES)}
    return sorted(opos, key=lambda item: (rank.get(item.get("family", ""), 99), item.get("short_name", "")))


def source_facts(rows: list[tuple[str, str]]) -> str:
    items = "".join(
        f"<div><dt>{escape(label)}</dt><dd>{value}</dd></div>" for label, value in rows if value
    )
    return f'<dl class="source-facts">{items}</dl>' if items else ""


def source_links(links: list[tuple[str, str]]) -> str:
    parts = []
    for url, label in links:
        if not url:
            continue
        if url.startswith("http"):
            parts.append(ext_a(url, label))
        else:
            parts.append(f'<a href="{escape(url)}">{escape(label)}</a>')
    return f'<p class="source-links">{" · ".join(parts)}</p>' if parts else ""


def formula_card(item: dict, prefix: str) -> str:
    fuente = item.get("fuente_oficial") or {}
    identifier = item.get("source_identifier") or ""
    html_url = item.get("source_url") or fuente.get("url") or ""
    published = fuente.get("published_date") or item.get("source_date") or ""
    calc_href = f"{prefix}{live_path(item)}index.html"
    rows = [
        ("Cuerpo", escape(item.get("name") or item["short_name"])),
        ("Organismo", escape(item.get("administracion", ""))),
        ("Convocatoria", escape(item.get("convocatoria", ""))),
        ("Apartado usado", escape(item.get("source_section", ""))),
        ("Qué controla el cálculo", escape(fuente.get("used_for") or item.get("formula_human", ""))),
        ("Fórmula", escape(item.get("formula_human", ""))),
        ("Fecha de la norma", escape(es_date(fuente.get("source_date", "")))),
        ("Publicación en el BOE", escape(es_date(published))),
        ("Consultado / verificado", escape(es_date(fuente.get("reviewed_at") or item.get("last_verified", "")))),
    ]
    links = [(html_url, "Texto en el BOE" if str(identifier).startswith("BOE-") else "Texto oficial")]
    if identifier and published and str(identifier).startswith("BOE-"):
        links.append((boe_pdf_url(identifier, published), "PDF del BOE"))
    for extra_url, extra_label in item.get("source_extra_links") or []:
        links.append((extra_url, extra_label))
    links.append((calc_href, "Calculadora"))
    return f"""<article class="source-entry" id="fuente-{escape(item.get("family") or item["slug"])}">
      <p class="source-kicker">Convocatoria en vigor</p>
      <h3>{escape(item.get("family_name") or item["short_name"])}</h3>
      <p class="source-id">{escape(identifier)}</p>
      {source_facts(rows)}
      {source_links(links)}
    </article>"""


def historical_cards(item: dict) -> str:
    hist = item.get("historical") or {}
    if not hist:
        return ""
    identifier = hist.get("source_identifier") or ""
    url = hist.get("source_url") or ""
    kind = hist.get("kind")
    if kind == "cut":
        cut = str(hist.get("cut")).replace(".", ",")
        used = (
            f"El tribunal publicó un corte aproximado de {cut} en la prueba de conocimientos del año pasado. "
            "No es el corte de esta convocatoria ni un puesto en el ranking de todos los examinados."
        )
        published = ""
        pdf = ""
    else:
        used = (
            hist.get("disclaimer")
            or "Lista oficial de quienes obtuvieron plaza el año pasado. No es el ranking de todos los opositores."
        )
        published = "2025-10-24" if identifier == "BOE-A-2025-21403" else ""
        pdf = boe_pdf_url(identifier, published) if identifier.startswith("BOE-") and published else ""
    rows = [
        ("Qué es", escape(hist.get("what") or hist.get("title") or "")),
        ("Identificador", escape(identifier)),
        ("Para qué se usa aquí", escape(used)),
        ("Año de referencia", escape(str(hist.get("year") or ""))),
    ]
    links = [(url, "Fuente oficial")]
    if pdf:
        links.append((pdf, "PDF del BOE"))
    return f"""<article class="source-entry" id="historico-{escape(item.get("family") or item["slug"])}">
      <p class="source-kicker">Histórico del año pasado</p>
      <h3>{escape(item.get("family_name") or item["short_name"])}</h3>
      <p class="source-id">{escape(identifier)}</p>
      {source_facts(rows)}
      {source_links(links)}
    </article>"""


def fuentes_page(opos: list[dict]) -> str:
    prefix = rel_prefix(1)
    items = ordered_opos(opos)
    formula_html = "".join(formula_card(item, prefix) for item in items)
    hist_html = "".join(historical_cards(item) for item in items)
    extra_hist = f"""<article class="source-entry" id="historico-gc-convocatoria-2025">
      <p class="source-kicker">Contexto histórico</p>
      <h3>Guardia Civil 2025 — convocatoria</h3>
      <p class="source-id">BOE-A-2025-10521</p>
      {source_facts([
        ("Norma", escape("Resolución 160/38240/2025, de 23 de mayo, Dirección General de la Guardia Civil")),
        ("Publicación en el BOE", escape("28 de mayo de 2025")),
        ("Para qué se cita", escape(
            "Es la convocatoria que produjo la lista de propuestos a alumno de 2025 (BOE-A-2025-21403). "
            "No es la fórmula de la calculadora en vigor; esa es BOE-A-2026-9982."
        )),
      ])}
      {source_links([
        ("https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-10521", "Texto en el BOE"),
        (boe_pdf_url("BOE-A-2025-10521", "2025-05-28"), "PDF del BOE"),
      ])}
    </article>"""
    portals = [
        (
            "Boletín Oficial del Estado",
            "https://www.boe.es/",
            "Diario oficial donde se publican las convocatorias y las listas que usa esta web.",
        ),
        (
            "Portal del Aspirante (Policía Nacional)",
            "https://www.policia.es/portalaspirantes",
            "Canal oficial de la Dirección General de la Policía para procesos de ingreso. De ahí sale el comunicado del corte aproximado de conocimientos de 2025.",
        ),
        (
            "Procesos de Cabos y Guardias (Ministerio del Interior)",
            "https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/empleo-publico/oposiciones/cuerpo-de-la-guardia-civil/escala-de-cabos-y-guardias/",
            "Página del Ministerio del Interior sobre el ingreso en la Escala de Cabos y Guardias. No sustituye el apartado del BOE que fija la fórmula.",
        ),
        (
            "Oferta de empleo público 2026 — Fuerzas y Cuerpos de Seguridad",
            "https://www.interior.gob.es/opencms/es/servicios-al-ciudadano/empleo-publico/procesos-selectivos/oferta-de-empleo-publico-2026-fuerzas-y-cuerpos-de-seguridad-del-estado/",
            "Comunicación oficial del Ministerio del Interior sobre la oferta 2026 de Policía Nacional y Guardia Civil.",
        ),
        (
            "Sede electrónica de la Guardia Civil",
            "https://sede.guardiacivil.gob.es/",
            "Sede oficial citada en las convocatorias para la solicitud de ingreso. No sustituye al BOE como fuente de la fórmula.",
        ),
        (
            "Ayuntamiento de Madrid — Policía Municipal",
            "https://www.madrid.es/portales/munimadrid/es/Inicio/Seguridad-y-emergencias/Policia-Municipal/Policia-del-Cuerpo-de-Policia-Municipal-del-Ayuntamiento-de-Madrid-concurso-oposicion-libre-con-reserva-de-plazas-tropa-y-marineria-convocatoria-diciembre-2025-reserva-turno-libre/?vgnextchannel=3926bb21278fe410VgnVCM1000000b205a0aRCRD&vgnextoid=987256187a8ea910VgnVCM200000f921e388RCRD",
            "Ficha del proceso de Policía Municipal de Madrid. Las bases (BOAM 9829) fijan la fórmula; el BOE solo anuncia las 561 plazas.",
        ),
    ]
    portal_html = "".join(
        f"""<article class="source-entry">
      <h3>{escape(name)}</h3>
      <p>{escape(note)}</p>
      {source_links([(url, "Abrir portal")])}
    </article>"""
        for name, url, note in portals
    )
    toc = "".join(
        f'<li><a href="#fuente-{escape(item.get("family") or item["slug"])}">{escape(item.get("family_name") or item["short_name"])}</a></li>'
        for item in items
    )
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Fuentes oficiales", "")], "fuentes/")}
    <div class="hero">
      <h1>Fuentes oficiales</h1>
      <p class="lede">Normas, listas y portales que sustentan las calculadoras. Cada fórmula sale de un boletín concreto, no de una academia ni de un vídeo. Verificado el 19 de agosto de 2026.</p>
    </div>
    <section class="content">
      <p>Si el tribunal anula preguntas, publica un corte o cambia la convocatoria, prevalece el documento oficial. Esta página no inventa plazas, puestos ni méritos que el boletín no liste.</p>
      <nav class="source-toc" aria-label="En esta página">
        <p class="source-kicker">En esta página</p>
        <ul>
          <li><a href="#formulas">Fórmulas en vigor</a></li>
          {toc}
          <li><a href="#historico">Histórico del año pasado</a></li>
          <li><a href="#portales">Portales institucionales</a></li>
        </ul>
      </nav>
      <h2 id="formulas">Fórmulas en vigor</h2>
      <p>Estas normas controlan el cálculo publicado. El enlace HTML y el PDF son del boletín; la calculadora es la URL estable de cada oposición.</p>
      <div class="source-catalog">{formula_html}</div>
      <h2 id="historico">Histórico del año pasado</h2>
      <p>Solo hay comparación cuando existe un dato oficial: un comunicado de corte o una lista de quienes sacaron plaza. No hay ranking de todos los examinados si el organismo no lo publica.</p>
      <div class="source-catalog">{hist_html}{extra_hist}</div>
      <h2 id="portales">Portales institucionales</h2>
      <p>Sitios del Estado relacionados con estos procesos. Un portal no sustituye el apartado de la convocatoria que fija la fórmula.</p>
      <div class="source-catalog">{portal_html}</div>
      <h2>Qué no es fuente</h2>
      <p>Blogs de academias, resúmenes de YouTube, foros o calculadoras genéricas no mandan sobre el BOE. Si una cifra no está en las normas o portales de esta página, {BRAND} no la usa.</p>
    </section>
    """
    return page_shell(
        seo_title("Fuentes oficiales"),
        f"Boletines del BOE, PDFs, listas históricas y portales oficiales que controlan las fórmulas de {BRAND}. Verificado el 19 de agosto de 2026.",
        "fuentes/",
        1,
        body,
    )


def html_ul(items: list[str]) -> str:
    return "<ul>" + "".join(f"<li>{escape(x)}</li>" for x in items) + "</ul>"


def metodologia_card(item: dict, prefix: str) -> str:
    copy = PAGES.get(item["slug"]) or {}
    how = "".join(f"<p>{escape(p)}</p>" for p in copy.get("how") or [])
    example = html_ul(copy["example"]) if copy.get("example") else ""
    mistakes = html_ul(copy["mistakes"]) if copy.get("mistakes") else ""
    limits = html_ul(copy["limits"]) if copy.get("limits") else ""
    hist = item.get("historical") or {}
    hist_p = ""
    if hist.get("kind") == "cut":
        hist_p = (
            "<p>Si hay comparación histórica, se contrasta tu nota de conocimientos con el corte "
            "oficial aproximado del año pasado. No hay lista pública de todos los examinados, "
            "así que no se da un número de orden.</p>"
        )
    elif hist.get("kind") == "selected_list":
        hist_p = (
            "<p>Si hay comparación histórica, se coloca tu total en la lista oficial de quienes "
            "obtuvieron plaza el año pasado. No es el ranking de todos los que se examinaron "
            "ni tu puesto en esta convocatoria.</p>"
        )
    calc_href = f"{prefix}{live_path(item)}index.html"
    fuente_href = f"{prefix}fuentes/index.html#fuente-{escape(item.get('family') or item['slug'])}"
    return f"""<article class="source-entry" id="metodo-{escape(item.get('family') or item['slug'])}">
      <p class="source-kicker">{escape(calc_kind(item))}</p>
      <h3>{escape(item.get("family_name") or item["short_name"])}</h3>
      <p class="source-id">{escape(item.get("source_identifier", ""))} · {escape(item.get("source_section", ""))}</p>
      <p><strong>Fórmula:</strong> {escape(item.get("formula_human", ""))}</p>
      {how}
      {"<h4>Un ejemplo con números</h4>" + example if example else ""}
      {"<h4>Errores frecuentes</h4>" + mistakes if mistakes else ""}
      {"<h4>Qué no calcula</h4>" + limits if limits else ""}
      {hist_p}
      <p class="source-links"><a href="{escape(calc_href)}">Calculadora</a> · <a href="{fuente_href}">Fuente oficial</a></p>
    </article>"""


def metodologia_page(opos: list[dict]) -> str:
    prefix = rel_prefix(1)
    items = ordered_opos(opos)
    cards = "".join(metodologia_card(item, prefix) for item in items)
    toc = "".join(
        f'<li><a href="#metodo-{escape(item.get("family") or item["slug"])}">{escape(item.get("family_name") or item["short_name"])}</a></li>'
        for item in items
    )
    models = [
        (
            "Puntuación neta",
            "Aciertos por el valor de cada acierto, menos errores por la penalización. En Auxiliar AGE y Ayudantes IIPP cada error resta un tercio: A − E/3. El resultado es puntuación directa, no una nota sobre 10 ni sobre 50.",
        ),
        (
            "Escala oficial",
            "La convocatoria fija un máximo Y (o 10) y un número de preguntas válidas T (o P). Guardia Civil usa Px = Y × (A − E/(N−1)) / T, con N = 4. Policía Nacional usa [A − E/(n−1)] × 10/P, con n = 3. No es la misma cuenta.",
        ),
        (
            "Valor fijo",
            "Cada acierto y cada error valen lo que dice el boletín, no 1 y 1/3. Auxilio Judicial: 0,60/−0,15 en el teórico y 1/−0,25 en el práctico.",
        ),
        (
            "Apto / no apto",
            "No hay nota numérica. En Guardia Civil, ortografía y gramática excluyen con 6 o más errores. Un 5 no es no apto.",
        ),
        (
            "Transformada",
            f"Pasa de puntuación directa a una escala (por ejemplo 0–20) con un umbral que publica el tribunal. Sin ese umbral de esta convocatoria, {BRAND} no interpola ni afirma el 10. En IIPP el recuadro es opcional y vacío significa «sin umbral».",
        ),
        (
            "Suma y concurso",
            "Las pruebas que puntúan se suman. El concurso de Guardia Civil se puede introducir como total ya baremado o calcularse ítem a ítem en la calculadora de baremo del apéndice I.",
        ),
    ]
    models_html = "".join(
        f"<div><dt>{escape(name)}</dt><dd>{escape(text)}</dd></div>" for name, text in models
    )
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Metodología", "")], "metodologia/")}
    <div class="hero">
      <h1>Metodología</h1>
      <p class="lede">Cómo se calcula cada nota: de qué archivo sale la fórmula, qué significa cada casilla y qué queda fuera. El motor no tiene un «si es Guardia Civil»: lee el boletín modelado en datos. Verificado el 19 de agosto de 2026.</p>
    </div>
    <section class="content">
      <nav class="source-toc" aria-label="En esta página">
        <p class="source-kicker">En esta página</p>
        <ul>
          <li><a href="#principios">Principios</a></li>
          <li><a href="#glosario">Tres ideas que no son lo mismo</a></li>
          <li><a href="#casillas">Qué haces en el formulario</a></li>
          <li><a href="#motor">Cómo calcula el motor</a></li>
          <li><a href="#oposiciones">Por oposición</a></li>
          {toc}
          <li><a href="#historico-metodo">Histórico del año pasado</a></li>
          <li><a href="#limites">Qué no se inventa</a></li>
          <li><a href="#pruebas">Cómo se comprueba</a></li>
        </ul>
      </nav>

      <h2 id="principios">Principios</h2>
      <p>Cada oposición tiene una <strong>página estable</strong>. Hoy calcula con el boletín en vigor. Cuando salga el siguiente, se actualiza esa misma dirección y la convocatoria anterior queda en una URL de archivo. No se mezcla la fórmula de un año con la de otro.</p>
      <p>La fórmula sale del boletín enlazado en cada página y en <a href="{prefix}fuentes/index.html">Fuentes oficiales</a>, no de un blog ni de una academia. Un resumen de YouTube no manda sobre el BOE.</p>
      <p>No hay cuenta. El cálculo se ejecuta en tu navegador: aciertos y errores no se envían a un servidor. Si usas «Compartir URL», los números van en la dirección, no en una cookie, y se descartan al cambiar de página.</p>
      <p>Ante cualquier discrepancia prevalece la convocatoria oficial. {BRAND} es independiente: no está afiliada ni respaldada por el organismo convocante.</p>

      <h2 id="glosario">Tres ideas que no son lo mismo</h2>
      <aside class="glossary" role="note">
        <dl>
          <div><dt>Puntuación</dt><dd>Lo que sale de tus aciertos, errores y blancos con la fórmula de esa prueba. Es tu nota de ese ejercicio, no una plaza.</dd></div>
          <div><dt>Mínimo oficial</dt><dd>El umbral de las bases para no ser eliminado en esa prueba (50/8/12 en Guardia Civil, 3 en Policía Nacional, 30 y 20 en Auxilio Judicial). Superarlo no es corte ni plaza.</dd></div>
          <div><dt>Nota de corte</dt><dd>La marca el resto de aspirantes cuando el tribunal publica la lista. Depende de plazas y de quién se examinó. Esta web no la inventa.</dd></div>
          <div><dt>Plaza</dt><dd>Sale de la lista final, tras el resto de pruebas (físicas, entrevista, médico, etc.). Superar un mínimo no es obtener plaza.</dd></div>
          <div><dt>Puntuación directa</dt><dd>Aciertos menos penalización, sin pasar aún a una escala 0–10, 0–20 o 0–50. En Auxiliar AGE e IIPP el BOE cierra la directa; la transformada exige un umbral del tribunal de esa convocatoria.</dd></div>
          <div><dt>Calificación transformada</dt><dd>La interpolación a la escala del tribunal. Sin el umbral publicado para <em>esta</em> convocatoria, no se afirma un 10 sobre 20 ni un 25 sobre 50.</dd></div>
        </dl>
      </aside>

      <h2 id="casillas">Qué haces en el formulario</h2>
      <ol class="how-steps">
        <li><strong>Aciertos y errores.</strong> Las correctas van en aciertos y los fallos en errores. Los blancos se calculan solos: preguntas válidas menos aciertos menos errores. En las convocatorias publicadas aquí las blancas no restan (valen 0).</li>
        <li><strong>Preguntas válidas.</strong> Viene relleno con el T o P del boletín. Solo se cambia si el tribunal anuló preguntas y entra reserva. La reserva no suma siempre: sustituye, por su orden, a las anuladas. El recuadro no puede superar cuestionario más reserva.</li>
        <li><strong>Lo opcional.</strong> Concurso, idiomas, umbral del tribunal u objetivo: vacío significa que no se suma ni se usa. El concurso de Guardia Civil admite un total ya baremado (0 a 45) o la calculadora de baremo ítem a ítem.</li>
        <li><strong>Calcular.</strong> Verás cada prueba, blancos, penalización, si llegas al mínimo de las bases y, si el dato existe, una comparación con el año pasado. Si un número es imposible (más aciertos que preguntas, decimales donde toca entero), se marca la casilla y no se finge un resultado.</li>
      </ol>
      <p>Si la puntuación bruta sale negativa, se deja en 0: las convocatorias publicadas aquí no admiten nota negativa en esas pruebas.</p>

      <h2 id="motor">Cómo calcula el motor</h2>
      <p>Cada calculadora arranca de un archivo de datos con la convocatoria, la fórmula, la fuente y la fecha de verificación. El motor (notaopo-engine-2.0) interpreta modelos; no hay lógica del tipo «si la oposición es Guardia Civil haz esto».</p>
      <dl class="source-facts">{models_html}</dl>
      <p>Cuando la prueba tiene un mínimo, el motor también puede decir, con tus aciertos, cuántos errores te puedes permitir, o cuántos aciertos harían falta para un objetivo. Solo si la cuenta es resoluble con esa fórmula.</p>

      <h2 id="oposiciones">Por oposición</h2>
      <p>La misma penalización no vale para todos los cuerpos. Guardia Civil y AGE restan un tercio; Policía Nacional, con tres opciones, resta medio acierto; Auxilio Judicial usa 0,60 y 0,15. Abre la calculadora de tu oposición.</p>
      <div class="source-catalog">{cards}</div>

      <h2 id="historico-metodo">Histórico del año pasado</h2>
      <p>Solo se compara cuando hay un dato oficial. No se fabrica un ranking de todos los opositores si el organismo no lo publica.</p>
      <ul>
        <li><strong>Policía Nacional:</strong> se compara la nota de conocimientos con el corte aproximado 7,17 que el Portal del Aspirante dio el 3 de noviembre de 2025. No da puesto.</li>
        <li><strong>Guardia Civil:</strong> se coloca el total en la lista BOE de propuestos a alumno, turno libre 2025 (BOE-A-2025-21403). Si no llegarías al último de esa lista, se dice así. Hay que haber superado también el resto de pruebas.</li>
        <li><strong>IIPP, Auxilio Judicial y Auxiliar AGE:</strong> no hay corte ni lista comparable publicada aquí. No se inventa.</li>
      </ul>

      <h2 id="limites">Qué no se inventa</h2>
      <ul>
        <li>Físicas de Policía Nacional fuera de las tablas del anexo II, o físicas de Guardia Civil fuera de los mínimos del apéndice II de esa convocatoria. Entrevista, reconocimiento médico o psicotécnico de Policía Nacional calificado por el tribunal.</li>
        <li>Méritos que no figuren en el apéndice I de Guardia Civil, ni títulos no listados, ni el baremo de deportista de alto nivel de Policía Nacional.</li>
        <li>Una carrera o un grado superior como puntos extra en Escala Básica: el título exigido es Bachiller.</li>
        <li>La transformada de Auxiliar AGE 0–50 sin el PDF de criterios CPS de esta convocatoria.</li>
        <li>El umbral directo de IIPP tomado de 2025 como si ya valiera para 2026.</li>
        <li>Un corte de plaza de esta convocatoria, el número de convocados a psicofísicas o cuántos caben en el 1,75 por plaza de Policía Nacional.</li>
        <li>Policía Local / Municipal: no hay una fórmula única de España. Hace falta ciudad y boletín.</li>
      </ul>

      <h2 id="pruebas">Cómo se comprueba</h2>
      <p>Antes de publicar una calculadora se ejecutan casos independientes: todo correcto, todo a cero, mezcla, justo el mínimo, justo por debajo, apto/no apto, desbordes (más aciertos que preguntas) y valores no enteros donde toca entero. Si el BOE y el motor no coinciden, prevalece el BOE y no se publica esa cuenta.</p>
      <p>Última revisión de estas reglas: 19 de agosto de 2026. Las normas concretas están en <a href="{prefix}fuentes/index.html">Fuentes oficiales</a>.</p>

      <p class="notice">{escape(DISCLAIMER)}</p>
    </section>
    """
    return page_shell(
        seo_title("Metodología de cálculo"),
        f"Cómo {BRAND} calcula la nota: modelos del motor, mínimo frente a corte, blancos y reserva, y la fórmula de cada oposición según su BOE.",
        "metodologia/",
        1,
        body,
    )

def progress_trackers(opos: list[dict]) -> list[dict]:
    trackers = []
    for item in current_by_family(opos):
        family = family_id(item)
        name = item.get("family_name") or item["short_name"]
        trackers.append(
            {
                "key": f"tunotaopo:progress:{item['slug']}",
                "name": name,
                "href": live_path(item),
                "kind": "nota",
            }
        )
        if family == "policia-nacional":
            trackers.append(
                {
                    "key": "tunotaopo:progress:policia-nacional-fisicas-2026",
                    "name": "Policía Nacional · físicas",
                    "href": "oposiciones/policia-nacional/pruebas-fisicas/",
                    "kind": "fisicas",
                }
            )
        if family == "policia-local":
            trackers.append(
                {
                    "key": "tunotaopo:progress:policia-local-madrid-fisicas-2026",
                    "name": "Policía Local Madrid · físicas",
                    "href": "oposiciones/policia-local/pruebas-fisicas/",
                    "kind": "fisicas",
                }
            )
        if family == "guardia-civil":
            trackers.append(
                {
                    "key": "tunotaopo:progress:guardia-civil-fisicas-2026",
                    "name": "Guardia Civil · físicas",
                    "href": "oposiciones/guardia-civil/pruebas-fisicas/",
                    "kind": "fisicas",
                }
            )
            trackers.append(
                {
                    "key": "tunotaopo:progress:guardia-civil-baremo-2026",
                    "name": "Guardia Civil · baremo",
                    "href": "oposiciones/guardia-civil/baremo/",
                    "kind": "baremo",
                }
            )
    return trackers


def progreso_page(opos: list[dict]) -> str:
    prefix = rel_prefix(2)
    config = json.dumps(progress_trackers(opos), ensure_ascii=False)
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Mi progreso", ""),
    ], PROGRESO_PATH)}
    <div class="hero">
      <h1>Mi progreso</h1>
      <p class="lede">Calcular no guarda nada. Solo se añade un simulacro si pulsas <strong>Guardar en Mi progreso</strong> en la calculadora. El historial queda en este navegador, no en una cuenta ni en un servidor.</p>
      <p class="hero-actions">
        <button type="button" class="button button-secondary" id="progress-export">Exportar JSON</button>
        <label class="button button-ghost" for="progress-import">Importar JSON</label>
        <input id="progress-import" type="file" accept="application/json,.json" hidden>
      </p>
    </div>
    <p id="progress-backup-note" class="search-empty" hidden></p>
    <script type="application/json" id="progreso-config">{config}</script>
    <div id="progreso-root" class="progress-board"></div>
    <section class="content">
      <p>Si cambias de dispositivo, exporta el JSON y lo importas en el otro. No se sincroniza solo. Borrar los datos del sitio también borra esto.</p>
      <p id="usage-local" class="note-quiet" hidden></p>
    </section>
    """
    return page_shell(
        seo_title("Mi progreso"),
        "Historial de simulacros de nota y físicas guardado en este navegador. Sin cuenta ni servidor.",
        PROGRESO_PATH,
        2,
        body,
        tools=("progreso",),
        noindex=True,
    )


def simple_page(
    slug_title: str,
    h1: str,
    description: str,
    path: str,
    paragraphs: list[str],
    extra: str = "",
    lead: str = "",
) -> str:
    depth = 1
    prefix = rel_prefix(depth)
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), (h1, "")], path)}
    <div class="hero"><h1>{escape(h1)}</h1></div>
    <section class="content">
      {lead}
      {''.join(f"<p>{escape(p)}</p>" for p in paragraphs)}
      {extra}
    </section>
    """
    return page_shell(slug_title, description, path, depth, body, ads=False)


def embed_family_slug(item: dict) -> str:
    family_path = (item.get("family_path") or "").strip("/")
    if family_path.startswith("calculadoras/"):
        return family_path.split("/", 1)[1]
    return family_id(item)


def calculator_embed_page(cfg: dict) -> str:
    open_href = "/" + live_path(cfg) + "index.html"
    embed_path = f"embed/{embed_family_slug(cfg)}/"
    src = cfg.get("fuente_oficial") or {}
    heading = cfg["h1"] if str(cfg.get("anio", "")) in cfg["h1"] else f'{cfg["h1"]} {cfg["anio"]}'
    body = f"""
    <div class="hero hero-calc">
      <h1>{escape(heading)}</h1>
      <p class="calc-badge">{escape(cfg.get("source_identifier", ""))} · convocatoria {escape(str(cfg.get("anio", "")))}</p>
    </div>
    <article class="tool">
      {calculator_form(cfg, "/", f"{SITE}/{embed_path}")}
      <section class="source-card">
        <p class="source-kicker">Fuente oficial</p>
        <p class="source-id">{escape(cfg.get("source_identifier", ""))}</p>
        <p>Convocatoria: {escape(cfg["convocatoria"])}.</p>
        <p>Última revisión: {escape(str(cfg.get("last_verified") or src.get("reviewed_at", "")))}.</p>
        <p>{source_link(cfg)}</p>
      </section>
      {report_error_link(cfg.get("family_name") or cfg["short_name"], cfg["convocatoria"], f"{SITE}/{embed_path}", "nota (embed)")}
    </article>
    <script type="application/json" id="oposicion-config">{json.dumps(with_historical(cfg), ensure_ascii=False)}</script>
    """
    return embed_shell(
        f"{heading} · embed | {BRAND}",
        cfg["meta_description"] + " Versión para insertar en un iframe. No indexable.",
        embed_path,
        body,
        tools=("calculator",),
        open_href=open_href,
    )


def academias_page(opos: list[dict]) -> str:
    prefix = rel_prefix(2)
    cards = []
    snippets = []
    for item in current_by_family(opos):
        name = item.get("family_name") or item["short_name"]
        slug = embed_family_slug(item)
        calc = "/" + live_path(item) + "index.html"
        classroom = calc + "?mode=classroom"
        embed = f"{SITE}/embed/{slug}/"
        cards.append(
            f'<a class="card" href="{calc}"><h3>{escape(name)}</h3>'
            f"<p>Calculadora de la convocatoria {escape(str(item.get('anio', '')))}.</p>"
            f'<span class="card-cta">Ver herramientas</span></a>'
        )
        snippets.append(
            f"<h3>{escape(name)}</h3>"
            f"<pre><code>&lt;iframe src=&quot;{embed}&quot; width=&quot;100%&quot; height=&quot;700&quot; loading=&quot;lazy&quot; title=&quot;Calculadora {escape(name)}&quot;&gt;&lt;/iframe&gt;</code></pre>"
            f'<p><a href="{classroom}">Abrir modo aula</a> · <a href="/embed/{slug}/index.html">Ver embed</a></p>'
        )
    request = (
        f'<p><a class="button button-secondary" href="mailto:{CONTACT_EMAIL}'
        f'?subject={quote("Solicitar oposición en TuNotaOpo")}'
        f'&body={quote("Oposición que preparo:\\nConvocatoria (si la conoces):\\n\\nNo es una petición de plazo ni una promesa de inclusión.")}">Solicitar / contactar</a></p>'
    )
    body = f"""
    {crumbs([("Inicio", prefix + "index.html"), ("Academias y preparadores", "")], ACADEMIAS_PATH)}
    <div class="hero">
      <h1>TuNotaOpo para academias y preparadores</h1>
      <p class="lede">Las herramientas de TuNotaOpo pueden utilizarse gratuitamente con alumnos y opositores. Sin registro, sin servidor de notas y con la fórmula de cada convocatoria.</p>
    </div>
    <ul class="proof">
      <li>Gratis</li>
      <li>Sin registro</li>
      <li>Basado en fuentes oficiales</li>
      <li>Calculadoras por convocatoria</li>
      <li>Código QR</li>
      <li>Modo aula</li>
      <li>Resultados imprimibles</li>
      <li>Sin almacenar las notas de los alumnos en servidores</li>
    </ul>
    <section class="content">
      <h2>Herramientas disponibles</h2>
      <div class="catalog">{''.join(cards)}</div>
      <h2>Úsalo en clase</h2>
      <ol class="how-steps">
        <li><strong>Abre la calculadora</strong> de la oposición en el navegador.</li>
        <li><strong>Activa modo aula</strong> (botón o <code>?mode=classroom</code>) para verlo en proyector.</li>
        <li><strong>Muestra el QR</strong> o comparte el enlace. Los alumnos calculan en su móvil.</li>
        <li><strong>Imprime</strong> el resultado si hace falta papel. No se crea una cuenta.</li>
      </ol>
      <h2>Calculadora embebible</h2>
      <p>Misma fórmula que la página pública. Sin menú, sin anuncios y con <code>noindex</code>. Ejemplo:</p>
      {''.join(snippets)}
      <h2>¿Falta la oposición que preparas?</h2>
      <p>Puedes escribirnos. No prometemos incluirla ni damos plazo. Solo se publica con fuente oficial y tests.</p>
      {request}
    </section>
    """
    return page_shell(
        seo_title("TuNotaOpo para academias y preparadores"),
        "Usa las calculadoras de TuNotaOpo en clase: modo aula, QR y embed gratuito, sin registro ni servidor de notas.",
        ACADEMIAS_PATH,
        2,
        body,
    )


def remove_retired_urls(published: list[dict]) -> None:
    keep = {item["path"].rstrip("/") for item in published}
    keep.update(item["family_path"].rstrip("/") for item in published if item.get("family_path"))
    calc_root = ROOT / "calculadoras"
    if not calc_root.exists():
        return
    for child in calc_root.iterdir():
        if not child.is_dir():
            continue
        rel = f"calculadoras/{child.name}"
        if not any(path.startswith(rel) for path in keep):
            shutil.rmtree(child)


def robots_txt() -> str:
    shared = (
        "Disallow: /research/\nDisallow: /tests/\nDisallow: /scripts/\n"
        "Disallow: /release/\nDisallow: /data/\nDisallow: /embed/\n"
    )
    return (
        "User-agent: *\n"
        "Allow: /\n"
        f"{shared}\n"
        "User-agent: AdsBot-Google\n"
        "User-agent: Mediapartners-Google\n"
        f"{shared}\n"
        f"Sitemap: {SITE}/sitemap.xml\n"
    )


def build() -> None:
    opos = load_oposiciones()
    write_generated_assets()
    remove_retired_urls(opos)
    write(ROOT / "index.html", home(opos))
    write(ROOT / "calculadoras" / "index.html", calculadoras_index(opos))
    write(ROOT / "oposiciones" / "progreso" / "index.html", progreso_page(opos))
    write(ROOT / "oposiciones" / "academias" / "index.html", academias_page(opos))
    for item in current_by_family(opos):
        slug = embed_family_slug(item)
        write(ROOT / "embed" / slug / "index.html", calculator_embed_page(item))
    stale = ROOT / "progreso"
    if stale.exists():
        shutil.rmtree(stale)
    stale_academias = ROOT / "academias"
    if stale_academias.exists():
        shutil.rmtree(stale_academias)
    hub_urls = write_hubs(opos)
    for cfg in opos:
        year_path = cfg["path"]
        family = cfg.get("family_path")
        if cfg.get("is_current") and family:
            write(
                ROOT / family / "index.html",
                calculator_page(cfg, opos, family, family, "current"),
            )
            write(
                ROOT / year_path / "index.html",
                calculator_page(cfg, opos, year_path, family, "archive"),
            )
        else:
            write(
                ROOT / year_path / "index.html",
                calculator_page(cfg, opos, year_path, year_path, "archive"),
            )

    write(ROOT / "metodologia" / "index.html", metodologia_page(opos))

    write(ROOT / "fuentes" / "index.html", fuentes_page(opos))

    write(
        ROOT / "aviso-legal" / "index.html",
        simple_page(
            seo_title("Aviso legal"),
            "Aviso legal",
            f"Aviso legal de {BRAND}. Titular: Haroun Zemrani El Hadri.",
            "aviso-legal/",
            [
                "El sitio ofrece herramientas de cálculo orientativo sobre convocatorias públicas. No presta asesoramiento jurídico ni garantiza el resultado de un proceso selectivo.",
                "Los contenidos propios se publican para su uso personal e informativo. Las normas oficiales pertenecen a sus editores.",
            ],
            lead=legal_identity(),
        ),
    )
    write(
        ROOT / "privacidad" / "index.html",
        simple_page(
            seo_title("Política de privacidad"),
            "Privacidad",
            f"Política de privacidad de {BRAND}. En esta versión no hay analítica ni publicidad de terceros activa.",
            "privacidad/",
            [
                "El cálculo se ejecuta en el navegador. Mi progreso es opcional: solo se guarda si pulsas el botón. Queda en el almacenamiento local de este dispositivo, no se envía a TuNotaOpo y no requiere cuenta. Puedes borrar cada historial o los datos del sitio en el navegador.",
                "El tema (claro u oscuro) y un recuento local de uso (páginas vistas, cálculos) se guardan en este navegador. En el hosting, el mismo recuento puede enviarse a /api/event del propio dominio, sin nombre ni DNI. No hay analítica de terceros.",
                "No se piden nombre, DNI ni correo para usar las calculadoras. El correo de contacto solo se usa si tú escribes.",
                "No hay cookies de analítica, AdSense ni redes publicitarias activas. Cuando exista un Publisher ID y un consentimiento válido, esta página se actualizará y se activará un CMP antes de cargar esos scripts.",
            ],
            extra='<p><a href="/oposiciones/progreso/">Abrir Mi progreso</a>.</p>',
            lead=legal_identity(),
        ),
    )
    write(
        ROOT / "cookies" / "index.html",
        simple_page(
            seo_title("Política de cookies"),
            "Cookies",
            f"Política de cookies de {BRAND}. No hay cookies no esenciales activas en esta versión.",
            "cookies/",
            [
                "Esta versión no instala cookies de analítica ni publicidad.",
                "Los simulacros de nota y físicas se guardan en el almacenamiento local del navegador, no en una cookie. Si usas Compartir URL, los datos van en la dirección.",
                "Si más adelante se activa AdSense o una medición, se incorporará un banner de consentimiento válido para el EEE antes de cargar esos scripts.",
            ],
        ),
    )
    write(
        ROOT / "contacto" / "index.html",
        simple_page(
            seo_title("Contacto"),
            "Contacto",
            f"Contacto de {BRAND}. Correo del proyecto para correcciones de fórmula.",
            "contacto/",
            [
                f"Para correcciones de fórmula o avisos de nueva convocatoria: {CONTACT_EMAIL}.",
                "Indica la oposición, el identificador del boletín y el apartado concreto. No envíes datos personales innecesarios.",
            ],
            lead=legal_identity(),
        ),
    )

    write(
        ROOT / "404.html",
        page_shell(
            f"Página no encontrada — {BRAND}",
            f"Esa URL no existe en {BRAND}. Vuelve al inicio o al índice de oposiciones.",
            "404.html",
            0,
            """
    <div class="hero hero-home">
      <p class="eyebrow">Error 404</p>
      <h1>Esta página no existe</h1>
      <p class="lede">Comprueba la dirección o entra por el índice de oposiciones. Si buscabas un municipio de Policía Local sin boletín, esa ficha ya no existe.</p>
      <p class="hero-actions"><a class="button button-primary" href="/">Ir al inicio</a>
      <a class="button button-secondary" href="/oposiciones/">Ver oposiciones</a>
      <a class="button button-secondary" href="/oposiciones/policia-local/">Policía Local</a></p>
    </div>
            """,
            noindex=True,
        ),
    )

    urls = [f"{SITE}/", f"{SITE}/calculadoras/"] + hub_urls
    seen_paths = set()
    for o in opos:
        if o.get("is_current") and o.get("family_path"):
            candidates = [o["family_path"]]
        else:
            candidates = [o.get("path")]
        for p in candidates:
            if p and p not in seen_paths:
                seen_paths.add(p)
                urls.append(f"{SITE}/{p}")
    for extra in ("metodologia/", "fuentes/", "aviso-legal/", "privacidad/", "cookies/", "contacto/", ACADEMIAS_PATH):
        urls.append(f"{SITE}/{extra}")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        sitemap.append(
            f"  <url><loc>{url}</loc><lastmod>{LASTMOD}</lastmod><changefreq>monthly</changefreq></url>"
        )
    sitemap.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(ROOT / "robots.txt", robots_txt())
    write(ROOT / "ads.txt", f"google.com, {ADSENSE_PUBLISHER}, DIRECT, f08c47fec0942fa0\n")

    # .htaccess is maintained in the project root. Do not overwrite it from the skill template.


if __name__ == "__main__":
    build()
    print("Generated static pages in", ROOT)
