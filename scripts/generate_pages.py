#!/usr/bin/env python3
"""Generate indexable static pages from opposition configs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from content import DISCLAIMER, PAGES, UPCOMING

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tunotaopo.es"
DATA_DIR = ROOT / "data" / "oposiciones"


def load_oposiciones() -> list[dict]:
    items = []
    for path in sorted(DATA_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("status", "published") == "published":
            items.append(data)
    return items


def rel_prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def nav(prefix: str) -> str:
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}assets/logo.svg" width="36" height="36" alt="">
      <span>NotaOpo</span>
    </a>
    <nav class="nav" aria-label="Principal">
      <a href="{prefix}calculadoras/index.html">Calculadoras</a>
      <a href="{prefix}metodologia/index.html">Metodología</a>
      <a href="{prefix}fuentes/index.html">Fuentes</a>
    </nav>
  </div>
</header>"""


def footer(prefix: str) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <p>NotaOpo</p>
      <p class="footer-tag">Cálculo orientativo. Prevalece la convocatoria oficial.</p>
    </div>
    <div class="footer-links">
      <a href="{prefix}metodologia/index.html">Metodología</a>
      <a href="{prefix}fuentes/index.html">Fuentes</a>
      <a href="{prefix}privacidad/index.html">Privacidad</a>
      <a href="{prefix}cookies/index.html">Cookies</a>
      <a href="{prefix}aviso-legal/index.html">Aviso legal</a>
      <a href="{prefix}contacto/index.html">Contacto</a>
    </div>
  </div>
</footer>"""


CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'"
)


def head(title: str, description: str, canonical: str, prefix: str, extra: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta http-equiv="Content-Security-Policy" content="{CSP}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="theme-color" content="#0c1924">
  <meta name="color-scheme" content="light">
  {extra}
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="es_ES">
  <meta property="og:site_name" content="NotaOpo">
  <link rel="icon" href="{prefix}assets/logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}css/app.css?v=20260819c">
</head>"""


def crumbs(items: list[tuple[str, str]]) -> str:
    lis = []
    schema = []
    for i, (name, href) in enumerate(items, start=1):
        if href:
            lis.append(f'<li><a href="{href}">{escape(name)}</a></li>')
        else:
            lis.append(f"<li>{escape(name)}</li>")
        item = {"@type": "ListItem", "position": i, "name": name}
        if href and href.startswith("http"):
            item["item"] = href
        schema.append(item)
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": schema}
    return (
        '<nav class="crumbs" aria-label="Migas de pan"><ol>'
        + "".join(lis)
        + "</ol></nav>"
        + f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    )


AD_SIZES = {
    "top": "leaderboard",
    "after-hero": "leaderboard",
    "after-result": "rectangle",
    "in-content": "rectangle",
    "after-related": "leaderboard",
    "home-mid": "rectangle",
    "catalog": "leaderboard",
    "bottom": "leaderboard",
}


def ad_slot(place: str, size: str | None = None) -> str:
    box = size or AD_SIZES.get(place, "rectangle")
    return (
        f'<aside class="ad-slot is-reserved is-inactive" data-place="{escape(place)}" data-size="{box}" '
        f'hidden aria-hidden="true">'
        f'<p class="ad-kicker">Publicidad</p>'
        f'<div class="ad-box ad-box-{box}"></div>'
        f"</aside>"
    )


def catalog_cards(items: list[dict], href_prefix: str = "") -> str:
    featured = ["guardia-civil-2026", "ayudantes-iipp-2026", "auxilio-judicial-2026", "auxiliar-age-2026"]
    order = {slug: i for i, slug in enumerate(featured)}
    cards = []
    for item in sorted(items, key=lambda x: order.get(x["slug"], 99)):
        org = item["administracion"].split(",")[0].split(" / ")[0]
        cards.append(
            f'<a class="card catalog-card" href="{href_prefix}{item["path"]}index.html">'
            f'<div class="card-meta"><span class="badge">{escape(str(item["anio"]))}</span>'
            f'<span class="card-org">{escape(org)}</span></div>'
            f"<h2>{escape(item['short_name'])}</h2>"
            f'<p class="card-kind">{escape(calc_kind(item))}</p>'
            f'<p class="card-source">{escape(item.get("source_identifier", ""))}</p>'
            f'<span class="card-cta">Calcular nota</span></a>'
        )
    return "".join(cards)


PUBLISHER = {
    "name": "Haroun Zemrani El Hadri",
    "email": "harounzemrani4@gmail.com",
    "address": "28981, Parla (Madrid)",
}


def legal_identity() -> str:
    address = PUBLISHER["address"] or "Pendiente de publicar"
    email = escape(PUBLISHER["email"])
    return (
        '<aside class="legal-pending">'
        '<p class="legal-pending-kicker">Identidad del editor</p>'
        "<p>NotaOpo es un proyecto personal. El titular es una persona física, no una sociedad.</p>"
        "<dl>"
        f"<div><dt>Titular</dt><dd>{escape(PUBLISHER['name'])}</dd></div>"
        f"<div><dt>Domicilio</dt><dd>{escape(address)}</dd></div>"
        f'<div><dt>Correo</dt><dd><a href="mailto:{email}">{email}</a></dd></div>'
        "</dl>"
        "</aside>"
    )


def affiliate_slot() -> str:
    return (
        '<section class="card" data-affiliate-slot="inactive">'
        "<h2>Academias y material</h2>"
        "<p>Cuando exista un programa de afiliación real se mostrará aquí, identificado como contenido comercial. "
        "Esta versión no incluye enlaces de afiliado.</p>"
        "</section>"
    )


def scripts(prefix: str, calculator: bool) -> str:
    tags = [
        f'<script src="{prefix}js/components/analytics.js" defer></script>',
        f'<script src="{prefix}js/site.js" defer></script>',
    ]
    if calculator:
        tags.insert(1, f'<script src="{prefix}js/engine/scoring.js" defer></script>')
        tags.insert(2, f'<script src="{prefix}js/components/calculator.js" defer></script>')
    return "\n".join(tags)


def page_shell(
    title: str,
    description: str,
    path: str,
    depth: int,
    body: str,
    calculator: bool = False,
    noindex: bool = False,
) -> str:
    prefix = rel_prefix(depth)
    canonical = f"{SITE}/{path}" if path else f"{SITE}/"
    extra_head = '<meta name="robots" content="noindex">' if noindex else ""
    return f"""{head(title, description, canonical, prefix, extra_head)}
<body>
  <a class="skip" href="#contenido">Saltar al contenido</a>
  {nav(prefix)}
  <div class="wrap">{ad_slot("top")}</div>
  <main id="contenido" class="wrap">
    {body}
  </main>
  <div class="wrap">{ad_slot("bottom")}</div>
  {footer(prefix)}
  {scripts(prefix, calculator)}
</body>
</html>
"""


def number_input(
    name: str,
    label: str,
    maximum: int | None = None,
    required: bool = True,
    step: str = "1",
    hint: str | None = None,
    placeholder: str | None = None,
) -> str:
    max_attr = f' max="{maximum}"' if maximum is not None else ""
    req = " required" if required else ""
    ph = f' placeholder="{escape(placeholder)}"' if placeholder is not None else ""
    hint_html = f'<span class="input-hint">{escape(hint)}</span>' if hint else ""
    return (
        f'<div class="input-group"><label for="{name}">{escape(label)}{hint_html}</label>'
        f'<input class="input" id="{name}" name="{name}" type="number" inputmode="{"numeric" if step == "1" else "decimal"}" min="0"{max_attr} step="{step}"{req}{ph}></div>'
    )


def calculator_form(cfg: dict) -> str:
    blocks = []
    editable = set(cfg.get("valid_questions_editable") or [])
    for stage in cfg.get("stages") or []:
        fields = []
        model = stage.get("model")
        if model in {"pass_fail_errors"}:
            fields.append(number_input(f"{stage['id']}_errors", "Errores", stage.get("questions")))
        elif model == "transform":
            fields.append(
                number_input(
                    f"{stage['id']}_cut",
                    "Umbral directo oficial",
                    None,
                    required=False,
                    step="0.01",
                    hint="Solo el publicado para esta convocatoria",
                )
            )
        elif model in {"aggregate", "multi_stage"}:
            continue
        else:
            fields.append(number_input(f"{stage['id']}_hits", "Aciertos", stage.get("questions")))
            fields.append(number_input(f"{stage['id']}_errors", "Errores", stage.get("questions")))
            if stage["id"] in editable:
                default_valid = stage.get("valid_questions", stage.get("questions"))
                fields.append(
                    number_input(
                        f"{stage['id']}_valid",
                        "Preguntas válidas",
                        (stage.get("questions") or 0) + (stage.get("reserve_questions") or 0),
                        required=False,
                        hint="Si hay anulaciones",
                        placeholder=str(default_valid),
                    )
                )
        if stage.get("help"):
            help_t = stage["help"]
        elif model == "transform":
            help_t = "Opcional. Introduce solo el umbral directo publicado para esta convocatoria."
        else:
            help_t = f"Preguntas: {stage.get('questions', '')}."
        n = len(fields)
        blocks.append(
            f'<fieldset class="stage"><legend>{escape(stage["label"])}</legend>'
            f'<p class="help">{escape(help_t)}</p>'
            f'<div class="fields fields-{n}">{"".join(fields)}</div></fieldset>'
        )
    if cfg.get("merits"):
        m = cfg["merits"]
        blocks.append(
            f'<fieldset class="stage"><legend>{escape(m["label"])}</legend>'
            f'<p class="help">{escape(m.get("help", ""))}</p>'
            f'<div class="fields fields-1">{number_input(m["id"], "Puntos de concurso", m.get("maximum"), required=False, step="0.001", hint="Total ya baremado")}</div>'
            "</fieldset>"
        )
    if cfg.get("aggregate"):
        blocks.append(
            '<fieldset class="stage"><legend>Objetivo (opcional)</legend>'
            '<p class="help">Solo se calcula el inverso si se puede resolver con los errores que ya has indicado, sin inventar un corte de plaza.</p>'
            f'<div class="fields fields-1">{number_input("target_score", "Objetivo de oposición", cfg["aggregate"].get("maximum"), required=False, step="0.0001", hint="Puntos que quieres alcanzar")}</div>'
            "</fieldset>"
        )
    return f"""<form id="calc-form" class="calculator" novalidate autocomplete="off">
  {''.join(blocks)}
  <p class="alert" role="note">Mínimo oficial ≠ nota de corte ≠ plaza.</p>
  <div class="actions actions-primary">
    <button type="submit" class="button button-primary">Calcular</button>
    <button type="reset" class="button button-secondary">Reset</button>
  </div>
</form>
<div class="result-slot">
<p id="calc-error" class="alert alert-danger" hidden role="alert"></p>
<section id="calc-result" class="result-card" hidden>
  <div class="result-main">
    <p id="result-kicker" class="result-kicker">Puntuación de la oposición</p>
    <p id="result-value" class="result-value"></p>
    <p id="result-scale" class="result-scale"></p>
    <p id="result-note" class="result-note"></p>
  </div>
  <div id="result-breakdown" class="score-list"></div>
  <div id="result-scenarios" class="result-scenarios"></div>
  <div class="actions result-actions">
    <button type="button" class="button button-secondary" id="copy-result">Copiar resultado</button>
    <button type="button" class="button button-secondary" id="share-result">Compartir URL</button>
    <button type="button" class="button button-ghost" id="print-result">Imprimir</button>
  </div>
</section>
</div>"""


def related_cards(current: dict, all_items: list[dict], prefix: str) -> str:
    cards = []
    for item in all_items:
        if item["slug"] == current["slug"]:
            continue
        href = prefix + item["path"] + "index.html"
        cards.append(
            f'<a class="card" href="{href}"><span class="badge">{escape(str(item["anio"]))}</span>'
            f'<h3>{escape(item["short_name"])}</h3><p>{escape(calc_kind(item))}</p>'
            f'<span class="card-cta">Calcular nota</span></a>'
        )
    if not cards:
        return ""
    return (
        '<section class="related-block"><h2>Calculadoras relacionadas</h2><div class="related">'
        + "".join(cards)
        + "</div></section>"
        + ad_slot("after-related")
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
        parts.append("Concurso opcional")
    return " · ".join(parts) or (item.get("formula_human") or "")


def source_link(cfg: dict) -> str:
    src = cfg.get("fuente_oficial") or {}
    url = cfg.get("source_url") or src.get("url", "")
    return f'<a class="source-link" data-track="official-source" href="{escape(url)}">Ver fuente oficial</a>'


def calculator_page(cfg: dict, all_items: list[dict]) -> str:
    copy = PAGES[cfg["slug"]]
    depth = 3
    prefix = rel_prefix(depth)
    src = cfg.get("fuente_oficial") or {}
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Calculadoras", prefix + "calculadoras/index.html"),
        (cfg["short_name"], ""),
    ])}
    <div class="hero">
      <h1>{escape(cfg["h1"])}</h1>
      <p class="lede">{escape(cfg["lede"])}</p>
      <div class="formula-note">
        <h2>Qué se calcula</h2>
        <p>{escape(cfg["formula_human"])}</p>
      </div>
    </div>
    {ad_slot("after-hero")}
    <div class="layout">
      <article class="tool">
        {calculator_form(cfg)}
        {ad_slot("after-result")}
        <section class="source-card">
          <p class="source-kicker">Fuente oficial</p>
          <p class="source-id">{escape(cfg.get("source_identifier", ""))}</p>
          <p>Apartado: {escape(cfg.get("source_section", ""))}</p>
          <p>Última revisión: {escape(str(cfg.get("last_verified") or src.get("reviewed_at", "")))}</p>
          <p>Convocatoria: {escape(cfg["convocatoria"])}. Organismo: {escape(cfg["administracion"])}.</p>
          <p>{source_link(cfg)} <span aria-hidden="true">→</span></p>
        </section>
        <p class="notice">{escape(DISCLAIMER)}</p>
      </article>
    </div>
    <section class="content">
      <h2>Cómo se calcula en esta convocatoria</h2>
      {''.join(f'<p>{escape(p)}</p>' for p in copy["how"])}
      {ad_slot("in-content")}
      {list_block("Ejemplo realista", copy["example"])}
      {list_block("Errores frecuentes", copy["mistakes"])}
      <h2>Fuente oficial</h2>
      <p>{source_link(cfg)}. Consultado el {escape(str(src.get("accessed_at", cfg.get("last_verified", ""))))}.</p>
      {list_block("Limitaciones", copy["limits"])}
      {faq_block(copy["faqs"])}
      {affiliate_slot()}
      {related_cards(cfg, all_items, prefix)}
    </section>
    <script type="application/json" id="oposicion-config">{json.dumps(cfg, ensure_ascii=False)}</script>
    """
    return page_shell(cfg["title"], cfg["meta_description"], cfg["path"], depth, body, calculator=True)


def home(all_items: list[dict]) -> str:
    upcoming = "".join(
        f"<li><strong>{escape(item['name'])}</strong> — {escape(item['reason'])}</li>"
        for item in UPCOMING
    )
    body = f"""
    <div class="hero hero-home">
      <p class="eyebrow">Calculadoras por convocatoria</p>
      <h1>Tu nota, con la fórmula del BOE</h1>
      <p class="lede">Aciertos, errores y blancos convertidos en la puntuación de <em>esta</em> convocatoria. No es una media genérica ni un corte inventado.</p>
      <ul class="proof">
        <li>Fórmula versionada</li>
        <li>Cálculo en tu navegador</li>
        <li>Fuente oficial enlazada</li>
      </ul>
    </div>
    <section>
      <h2 class="section-title">Calculadoras listas</h2>
      <div class="catalog">{catalog_cards(all_items)}</div>
    </section>
    {ad_slot("home-mid")}
    <section class="content">
      <h2>Qué hace NotaOpo</h2>
      <p>Cada URL está atada a un boletín, un apartado y una versión de fórmula. El motor interpreta esos datos en el navegador. No hay cuenta, no se envían tus aciertos a un servidor.</p>
      <p>Lee la <a href="metodologia/index.html">metodología</a> y las <a href="fuentes/index.html">fuentes oficiales</a>. {escape(DISCLAIMER)}</p>
      <aside class="note-quiet">
        <h2>Aún no publicadas</h2>
        <p>Investigadas, sin URL propia hasta que la fuente aplicable esté cerrada.</p>
        <ul>{upcoming}</ul>
      </aside>
    </section>
    """
    return page_shell(
        "NotaOpo — calculadoras de oposiciones por convocatoria",
        "Calcula la nota de Guardia Civil, IIPP, Auxilio Judicial y Auxiliar AGE 2026 con la fórmula del BOE. En el navegador, con fuente oficial.",
        "",
        0,
        body,
    )


def calculadoras_index(all_items: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Calculadoras", "")])}
    <div class="hero">
      <h1>Calculadoras por convocatoria</h1>
      <p class="lede">Una URL por fórmula oficial. Si cambia el boletín, cambia la página. No hay clones por provincia ni fichas vacías.</p>
    </div>
    <div class="catalog">{catalog_cards(all_items, "../")}</div>
    {ad_slot("catalog")}
    """
    return page_shell(
        "Calculadoras NotaOpo 2026",
        "Índice de calculadoras NotaOpo: Guardia Civil, Ayudantes IIPP, Auxilio Judicial y Auxiliar AGE 2026.",
        "calculadoras/",
        1,
        body,
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
    {crumbs([("Inicio", prefix + "index.html"), (h1, "")])}
    <div class="hero"><h1>{escape(h1)}</h1></div>
    <section class="content">
      {lead}
      {''.join(f"<p>{escape(p)}</p>" for p in paragraphs)}
      {extra}
    </section>
    """
    return page_shell(slug_title, description, path, depth, body)


def remove_retired_urls(published: list[dict]) -> None:
    keep = {item["path"].rstrip("/") for item in published}
    calc_root = ROOT / "calculadoras"
    if not calc_root.exists():
        return
    for child in calc_root.iterdir():
        if not child.is_dir():
            continue
        rel = f"calculadoras/{child.name}"
        if not any(path.startswith(rel) for path in keep):
            shutil.rmtree(child)


def build() -> None:
    opos = load_oposiciones()
    remove_retired_urls(opos)
    write(ROOT / "index.html", home(opos))
    write(ROOT / "calculadoras" / "index.html", calculadoras_index(opos))
    for cfg in opos:
        write(ROOT / cfg["path"] / "index.html", calculator_page(cfg, opos))

    write(
        ROOT / "metodologia" / "index.html",
        simple_page(
            "Metodología de cálculo NotaOpo",
            "Metodología",
            "Cómo NotaOpo versiona fórmulas oficiales de oposiciones y qué queda fuera de cada calculadora.",
            "metodologia/",
            [
                "Cada calculadora parte de un archivo de datos con la convocatoria, la fórmula, la fuente y la fecha de verificación. El motor interpreta modelos (puntuación neta, escala, valor fijo, transformación, apto/no apto, agregación). No hay código del tipo «si la oposición es Guardia Civil».",
                "Las fórmulas se leen en el boletín oficial. Un blog o una academia nunca es la fuente de la operación.",
                "Se distinguen tres ideas que el mercado mezcla: puntuación obtenida, mínimo oficial para superar una prueba y corte de plaza publicado después. Solo se muestra lo que la norma permite calcular.",
                "Antes de dar una calculadora por cerrada se ejecutan casos independientes: perfecto, cero, mezcla, mínimo exacto, justo por debajo, apto/no apto y entradas inválidas.",
                DISCLAIMER,
            ],
        ),
    )

    fuente_items = "".join(
        f'<li><a href="{escape(o.get("source_url") or o["fuente_oficial"]["url"])}">{escape(o.get("source_identifier", o["short_name"]))}</a> — {escape(o["short_name"])} ({escape(o.get("source_section", ""))})</li>'
        for o in opos
    )
    write(
        ROOT / "fuentes" / "index.html",
        simple_page(
            "Fuentes oficiales de las calculadoras",
            "Fuentes oficiales",
            "Boletines oficiales usados como fuente de las fórmulas de NotaOpo, con fecha de verificación.",
            "fuentes/",
            [
                "Listado de las normas que controlan el cálculo de las calculadoras publicadas. Verificado el 19 de agosto de 2026.",
            ],
            extra=f"<ul>{fuente_items}</ul>",
        ),
    )

    write(
        ROOT / "aviso-legal" / "index.html",
        simple_page(
            "Aviso legal",
            "Aviso legal",
            "Aviso legal de NotaOpo. Titular: Haroun Zemrani El Hadri.",
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
            "Política de privacidad",
            "Privacidad",
            "Política de privacidad de NotaOpo. En esta versión no hay analítica ni publicidad de terceros activa.",
            "privacidad/",
            [
                "El cálculo se ejecuta en el navegador. Al cambiar de página los datos del formulario se descartan. No se envían a un servidor.",
                "No hay cookies de analítica, AdSense ni redes publicitarias activas. Cuando exista un Publisher ID y un consentimiento válido, esta página se actualizará y se activará un CMP antes de cargar esos scripts.",
            ],
            lead=legal_identity(),
        ),
    )
    write(
        ROOT / "cookies" / "index.html",
        simple_page(
            "Política de cookies",
            "Cookies",
            "Política de cookies de NotaOpo. No hay cookies no esenciales activas en esta versión.",
            "cookies/",
            [
                "Esta versión no instala cookies de analítica ni publicidad.",
                "El último cálculo no se guarda al salir de la página. Si usas Compartir URL, los datos van en la dirección, no en una cookie.",
                "Si más adelante se activa AdSense o una medición, se incorporará un banner de consentimiento válido para el EEE antes de cargar esos scripts.",
            ],
        ),
    )
    write(
        ROOT / "contacto" / "index.html",
        simple_page(
            "Contacto",
            "Contacto",
            "Contacto de NotaOpo. Correo del titular para correcciones de fórmula.",
            "contacto/",
            [
                "Para correcciones de fórmula o avisos de nueva convocatoria: harounzemrani4@gmail.com.",
                "Indica la oposición, el identificador del boletín y el apartado concreto. No envíes datos personales innecesarios.",
            ],
            lead=legal_identity(),
        ),
    )

    write(
        ROOT / "404.html",
        page_shell(
            "Página no encontrada — NotaOpo",
            "Esa URL no existe en NotaOpo. Vuelve al inicio o al índice de calculadoras.",
            "404.html",
            0,
            """
    <div class="hero hero-home">
      <p class="eyebrow">Error 404</p>
      <h1>Esta página no existe</h1>
      <p class="lede">Comprueba la dirección o entra por el índice. No hay calculadoras ocultas ni URLs por provincia.</p>
      <p class="hero-actions"><a class="button button-primary" href="index.html">Ir al inicio</a>
      <a class="button button-secondary" href="calculadoras/index.html">Ver calculadoras</a></p>
    </div>
            """,
            noindex=True,
        ),
    )

    urls = [f"{SITE}/", f"{SITE}/calculadoras/"]
    urls.extend(f"{SITE}/{o['path']}" for o in opos)
    for extra in ("metodologia/", "fuentes/", "aviso-legal/", "privacidad/", "cookies/", "contacto/"):
        urls.append(f"{SITE}/{extra}")
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        sitemap.append(f"  <url><loc>{url}</loc><changefreq>monthly</changefreq></url>")
    sitemap.append("</urlset>")
    write(ROOT / "sitemap.xml", "\n".join(sitemap) + "\n")
    write(
        ROOT / "robots.txt",
        "User-agent: *\nAllow: /\n"
        "Disallow: /research/\nDisallow: /tests/\nDisallow: /scripts/\n"
        "Disallow: /release/\nDisallow: /data/\n"
        f"Sitemap: {SITE}/sitemap.xml\n",
    )
    write(
        ROOT / "ads.txt",
        "# ads.txt pendiente de Publisher ID real.\n"
        "# No hay anuncios activos y no se publica ningún identificador inventado.\n",
    )

    # .htaccess is maintained in the project root. Do not overwrite it from the skill template.


if __name__ == "__main__":
    build()
    print("Generated static pages in", ROOT)
