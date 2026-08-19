#!/usr/bin/env python3
"""Generate indexable static pages from opposition configs."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from content import DISCLAIMER, PAGES
from examenes_oficiales import EXAMENES
from fisicas_tables import fisicas_tables_html
from hubs_data import HUBS

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tunotaopo.es"
BRAND = "TuNotaOpo"
BRAND_ALT = "NotaOpo"
ASSET_V = "20260819t"
CONTACT_EMAIL = "contacto@tunotaopo.es"
PROGRESO_PATH = "oposiciones/progreso/"
DATA_DIR = ROOT / "data" / "oposiciones"
MONTHS_ES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
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


def rel_prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def seo_title(*parts: str) -> str:
    left = " ".join(str(part) for part in parts if part)
    return f"{left} | {BRAND}"


def extra_paras(texts: list[str] | None) -> str:
    if not texts:
        return ""
    return "".join(f"<p>{escape(text)}</p>" for text in texts)


def process_flow(hub: dict) -> str:
    items = []
    for text, _link in hub.get("pruebas") or []:
        short = text.split(" — ", 1)[0]
        items.append(f"<li>{escape(short)}</li>")
    if not items:
        return ""
    return f'<ol class="process-flow" aria-label="Orden de las pruebas">{"".join(items)}</ol>'


def timeline_html(events: list[dict] | None) -> str:
    if not events:
        return ""
    marks = {"done": "✓", "current": "→", "todo": "○"}
    items = []
    for event in events:
        state = event.get("state") or "todo"
        note = f'<p class="timeline-note">{escape(event["note"])}</p>' if event.get("note") else ""
        items.append(
            f'<li class="is-{escape(state)}">'
            f'<span class="timeline-mark" aria-hidden="true">{marks.get(state, "○")}</span>'
            f'<div><p class="timeline-label">{escape(event["label"])}</p>'
            f'<p class="timeline-date">{escape(event["date"])}</p>{note}</div></li>'
        )
    return f'<ol class="process-timeline">{"".join(items)}</ol>'


def es_date(iso: str) -> str:
    if not iso:
        return ""
    year, month, day = iso.split("-")
    return f"{int(day)} de {MONTHS_ES[int(month) - 1]} de {year}"


def boe_pdf_url(identifier: str, published_date: str) -> str:
    year, month, day = published_date.split("-")
    return f"https://www.boe.es/boe/dias/{year}/{month}/{day}/pdfs/{identifier}.pdf"


def ext_a(url: str, label: str) -> str:
    return f'<a href="{escape(url)}" rel="noopener noreferrer">{escape(label)}</a>'


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n"), encoding="utf-8", newline="\n")


def nav(prefix: str) -> str:
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix}index.html">
      <img src="{prefix}assets/logo.svg" width="36" height="36" alt="">
      <span>{BRAND}</span>
    </a>
    <nav class="nav" aria-label="Principal">
      <a href="{prefix}oposiciones/index.html">Oposiciones</a>
      <a href="{prefix}calculadoras/index.html">Calculadoras</a>
      <a href="{prefix}{PROGRESO_PATH}index.html">Mi progreso</a>
      <a href="{prefix}fuentes/index.html">Fuentes</a>
    </nav>
  </div>
</header>"""


def footer(prefix: str) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <p>{BRAND}</p>
      <p class="footer-tag">Cálculo orientativo. Prevalece la convocatoria oficial.</p>
    </div>
    <div class="footer-links">
      <a href="{prefix}oposiciones/index.html">Oposiciones</a>
      <a href="{prefix}{PROGRESO_PATH}index.html">Mi progreso</a>
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
  <meta property="og:site_name" content="{BRAND}">
  <link rel="icon" href="{prefix}assets/logo.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{prefix}css/app.css?v={ASSET_V}">
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


FEATURED_FAMILIES = [
    "guardia-civil",
    "policia-nacional",
    "ayudantes-iipp",
    "auxilio-judicial",
    "auxiliar-age",
]


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
        if dest == "hub":
            href = f"{href_prefix}oposiciones/{family_id(item)}/index.html"
            cta = "Ver oposición"
        else:
            href = f"{href_prefix}{live_path(item)}index.html"
            cta = "Calcular mi nota"
        cards.append(
            f'<a class="card catalog-card" href="{href}">'
            f'<div class="card-meta"><span class="badge">{escape(badge)}</span>'
            f'<span class="card-org">Fuente: {escape(item.get("source_identifier", ""))}</span></div>'
            f"<h2>{escape(name)}</h2>"
            f'<p class="card-kind">Calcula tu nota de la convocatoria {escape(str(year))}</p>'
            f'<p class="card-source">{escape(card_tests(item))}</p>'
            f'<span class="card-cta">{cta}</span></a>'
        )
    return "".join(cards)


PUBLISHER = {
    "name": "Haroun Zemrani El Hadri",
    "email": CONTACT_EMAIL,
    "address": "28981, Parla (Madrid)",
}


def legal_identity() -> str:
    address = PUBLISHER["address"] or "Pendiente de publicar"
    email = escape(PUBLISHER["email"])
    return (
        '<aside class="legal-pending">'
        '<p class="legal-pending-kicker">Identidad del editor</p>'
        f"<p>{BRAND} es un proyecto personal. El titular es una persona física, no una sociedad.</p>"
        "<dl>"
        f"<div><dt>Titular</dt><dd>{escape(PUBLISHER['name'])}</dd></div>"
        f"<div><dt>Domicilio</dt><dd>{escape(address)}</dd></div>"
        f'<div><dt>Correo</dt><dd><a href="mailto:{email}">{email}</a></dd></div>'
        "</dl>"
        "</aside>"
    )


def website_schema() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": BRAND,
        "alternateName": BRAND_ALT,
        "url": f"{SITE}/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE}/oposiciones/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def scripts(prefix: str, tools: tuple[str, ...] = ()) -> str:
    tags = [
        f'<script src="{prefix}js/components/analytics.js" defer></script>',
        f'<script src="{prefix}js/site.js?v={ASSET_V}" defer></script>',
    ]
    extra = {
        "calculator": [
            f'<script src="{prefix}js/engine/scoring.js?v={ASSET_V}" defer></script>',
            f'<script src="{prefix}js/components/calculator.js?v={ASSET_V}" defer></script>',
        ],
        "fisicas": [
            f'<script src="{prefix}js/engine/pn-fisicas.js?v={ASSET_V}" defer></script>',
            f'<script src="{prefix}js/components/fisicas.js?v={ASSET_V}" defer></script>',
        ],
        "gc_fisicas": [
            f'<script src="{prefix}js/engine/gc-fisicas.js?v={ASSET_V}" defer></script>',
            f'<script src="{prefix}js/components/gc-fisicas.js?v={ASSET_V}" defer></script>',
        ],
        "gc_baremo": [
            f'<script src="{prefix}js/engine/gc-baremo.js?v={ASSET_V}" defer></script>',
            f'<script src="{prefix}js/components/gc-baremo.js?v={ASSET_V}" defer></script>',
        ],
        "progreso": [
            f'<script src="{prefix}js/components/progreso.js?v={ASSET_V}" defer></script>',
        ],
    }
    inserted = []
    for tool in tools:
        inserted.extend(extra.get(tool) or [])
    return "\n".join(inserted + tags)


def page_shell(
    title: str,
    description: str,
    path: str,
    depth: int,
    body: str,
    calculator: bool = False,
    noindex: bool = False,
    fisicas: bool = False,
    website: bool = False,
    tools: tuple[str, ...] = (),
) -> str:
    prefix = rel_prefix(depth)
    canonical = f"{SITE}/{path}" if path else f"{SITE}/"
    extras = []
    if noindex:
        extras.append('<meta name="robots" content="noindex">')
    if website:
        extras.append(website_schema())
    extra_head = "\n  ".join(extras)
    resolved = tuple(tools)
    if calculator:
        resolved = ("calculator",) + resolved
    if fisicas:
        resolved = ("fisicas",) + resolved
    return f"""{head(title, description, canonical, prefix, extra_head)}
<body data-root="{prefix}">
  <a class="skip" href="#contenido">Saltar al contenido</a>
  {nav(prefix)}
  <div class="wrap">{ad_slot("top")}</div>
  <main id="contenido" class="wrap">
    {body}
  </main>
  <div class="wrap">{ad_slot("bottom")}</div>
  {footer(prefix)}
  {scripts(prefix, resolved)}
</body>
</html>
"""


def example_count(questions: int | None, kind: str) -> str:
    q = questions or 100
    if kind == "hits":
        if q <= 20:
            return "Ej. 14"
        if q <= 50:
            return "Ej. 34"
        if q <= 80:
            return "Ej. 55"
        return "Ej. 70"
    if q <= 20:
        return "Ej. 3"
    if q <= 50:
        return "Ej. 6"
    return "Ej. 10"


def number_input(
    name: str,
    label: str,
    maximum: int | None = None,
    required: bool = True,
    step: str = "1",
    hint: str | None = None,
    placeholder: str | None = None,
    value: int | float | str | None = None,
) -> str:
    max_attr = f' max="{maximum}"' if maximum is not None else ""
    req = " required" if required else ""
    ph = f' placeholder="{escape(placeholder)}"' if placeholder is not None else ""
    val = f' value="{escape(str(value))}"' if value is not None and value != "" else ""
    hint_html = f'<span class="input-hint">{escape(hint)}</span>' if hint else ""
    return (
        f'<div class="input-group"><label for="{name}">{escape(label)}{hint_html}</label>'
        f'<input class="input" id="{name}" name="{name}" type="number" inputmode="{"numeric" if step == "1" else "decimal"}" min="0"{max_attr} step="{step}"{req}{ph}{val}></div>'
    )


def form_guide(cfg: dict) -> str:
    parts = []
    for stage in cfg.get("stages") or []:
        if stage.get("model") in {"aggregate", "multi_stage", "transform"}:
            continue
        q = stage.get("questions")
        if q:
            extra = ""
            if stage.get("minimum") is not None:
                extra = f", mínimo {stage['minimum']}"
            elif stage.get("fail_if_errors_gte") is not None:
                extra = f", no apto con {stage['fail_if_errors_gte']} errores o más"
            parts.append(f"{stage['label']}: {q} preguntas{extra}")
    summary = "; ".join(parts)
    return (
        '<aside class="form-guide">'
        "<h2>Cómo usarla</h2>"
        "<ol>"
        "<li><strong>Aciertos y errores.</strong> Las correctas van en aciertos y los fallos en errores. "
        "No hace falta apuntar los blancos: salen solos (preguntas válidas menos aciertos menos errores). "
        "En estas convocatorias las blancas no restan.</li>"
        "<li><strong>Preguntas válidas.</strong> Viene relleno con el número del boletín. "
        "Solo cámbialo si el tribunal anuló preguntas y entró alguna de reserva.</li>"
        "<li><strong>Lo opcional.</strong> Concurso, idiomas, umbral del tribunal u objetivo: "
        "si no aplica, déjalo como está. Vacío significa que no se suma ni se usa.</li>"
        "<li><strong>Calcular nota.</strong> Verás la puntuación de cada prueba y si llegas al mínimo de las bases. "
        "Ese mínimo no es la nota de corte ni una plaza.</li>"
        "</ol>"
        f'<p class="form-guide-note"><strong>Esta convocatoria:</strong> {escape(summary)}</p>'
        "</aside>"
    )


def calculator_form(cfg: dict, prefix: str = "") -> str:
    blocks = [
        '<p class="calc-hint">Escribe aciertos y errores. Los blancos se calculan solos y, en estas convocatorias, no restan.</p>'
    ]
    editable = set(cfg.get("valid_questions_editable") or [])
    for stage in cfg.get("stages") or []:
        fields = []
        model = stage.get("model")
        if model in {"pass_fail_errors"}:
            fail_at = stage.get("fail_if_errors_gte")
            hint = (
                f"Solo los fallos. Con {fail_at} o más quedas no apto. Esta prueba no suma puntos"
                if fail_at
                else "Solo los fallos. Esta prueba no suma puntos"
            )
            fields.append(
                number_input(
                    f"{stage['id']}_errors",
                    "Errores",
                    stage.get("questions"),
                    hint=hint,
                    placeholder="Ej. 2",
                )
            )
        elif model == "transform":
            fields.append(
                number_input(
                    f"{stage['id']}_cut",
                    "Umbral directo publicado",
                    None,
                    required=False,
                    step="0.01",
                    hint="Solo si el tribunal de esta convocatoria ya lo ha publicado. Si no, déjalo vacío",
                    placeholder="Ej. 76,50",
                )
            )
        elif model in {"aggregate", "multi_stage"}:
            continue
        else:
            fields.append(
                number_input(
                    f"{stage['id']}_hits",
                    "Aciertos",
                    stage.get("questions"),
                    hint="Preguntas que has acertado",
                    placeholder=example_count(stage.get("questions"), "hits"),
                )
            )
            fields.append(
                number_input(
                    f"{stage['id']}_errors",
                    "Errores",
                    stage.get("questions"),
                    hint="Fallos. Las blancas no restan y no las pongas aquí",
                    placeholder=example_count(stage.get("questions"), "errors"),
                )
            )
            if stage["id"] in editable:
                default_valid = stage.get("valid_questions", stage.get("questions"))
                fields.append(
                    number_input(
                        f"{stage['id']}_valid",
                        "Preguntas válidas",
                        (stage.get("questions") or 0) + (stage.get("reserve_questions") or 0),
                        required=False,
                        hint="Cámbialo solo si el tribunal anuló preguntas",
                        placeholder=str(default_valid),
                        value=default_valid,
                    )
                )
        if stage.get("help"):
            help_t = stage["help"]
        elif model == "transform":
            help_t = (
                "Opcional. El BOE no cierra este número: es el umbral directo que publica el tribunal "
                "de esta convocatoria. Si aún no ha salido, déjalo vacío y verás solo la puntuación directa."
            )
        else:
            q = stage.get("questions", "")
            help_t = (
                f"Cuestionario de {q} preguntas. Escribe aciertos y errores; los blancos se calculan solos "
                "y en esta convocatoria no restan."
            )
        n = len(fields)
        blocks.append(
            f'<fieldset class="stage"><legend>{escape(stage["label"])}</legend>'
            f'<p class="help">{escape(help_t)}</p>'
            f'<div class="fields fields-{n}">{"".join(fields)}</div></fieldset>'
        )
    if cfg.get("merits"):
        m = cfg["merits"]
        mmax = m.get("maximum")
        mph = "Ej. 1,00" if mmax is not None and mmax <= 2 else "Ej. 12,500"
        merit_help = m.get("help", "Si no tienes este apartado o no quieres sumarlo, déjalo vacío.")
        extra_link = ""
        if family_id(cfg) == "guardia-civil":
            extra_link = (
                f'<p class="help">Para sumar cada mérito del apéndice I usa la '
                f'<a href="{prefix}oposiciones/guardia-civil/baremo/index.html">calculadora de baremo</a> '
                "y pega aquí el total.</p>"
            )
        blocks.append(
            f'<fieldset class="stage"><legend>{escape(m["label"])}</legend>'
            f'<p class="help">{escape(merit_help)}</p>{extra_link}'
            f'<div class="fields fields-1">{number_input(m["id"], m.get("input_label", "Puntos ya baremados"), mmax, required=False, step="0.001", hint="Opcional. Vacío = no se suma nada", placeholder=mph)}</div>'
            "</fieldset>"
        )
    if cfg.get("merit_note"):
        blocks.append(
            f'<aside class="merit-note" role="note"><p>{escape(cfg["merit_note"])}</p></aside>'
        )
    if cfg.get("aggregate"):
        tmax = cfg["aggregate"].get("maximum")
        if tmax is not None and tmax <= 10:
            tph = "Ej. 6"
        elif tmax is not None and tmax <= 60:
            tph = "Ej. 30"
        else:
            tph = "Ej. 50"
        blocks.append(
            '<fieldset class="stage"><legend>Objetivo (opcional)</legend>'
            '<p class="help">Si escribes un número, la calculadora te dice cuántos aciertos te faltarían para llegar a él, dejando los errores como los has puesto. No es la nota de corte ni un pronóstico de plaza.</p>'
            f'<div class="fields fields-1">{number_input("target_score", "Nota que te gustaría sacar", tmax, required=False, step="0.0001", hint="Opcional. Ejemplo: el mínimo de una prueba o una meta tuya", placeholder=tph)}</div>'
            "</fieldset>"
        )
    return f"""<form id="calc-form" class="calculator" novalidate autocomplete="off">
  {''.join(blocks)}
  <div class="actions actions-primary">
    <button type="submit" class="button button-primary">Calcular nota</button>
    <button type="reset" class="button button-secondary">Borrar datos</button>
  </div>
</form>
<div class="result-slot">
<div id="result-placeholder" class="result-placeholder">
  <p class="result-placeholder-kicker">Aún no hay nota</p>
  <p class="result-placeholder-title">Cuando pulses Calcular nota verás</p>
  <ul>
    <li>La puntuación de cada prueba y el total de la oposición.</li>
    <li>Los blancos, calculados solos a partir de aciertos y errores.</li>
    <li>Si llegas al mínimo de las bases. Eso no es el corte de plaza.</li>
  </ul>
</div>
<section id="calc-result" class="result-card" hidden>
  <div class="result-main">
    <p id="result-kicker" class="result-kicker">Puntuación de la oposición</p>
    <p id="result-value" class="result-value"></p>
    <p id="result-scale" class="result-scale"></p>
    <p id="result-note" class="result-note"></p>
  </div>
  <div id="result-breakdown" class="score-list"></div>
  <div id="result-scenarios" class="result-scenarios"></div>
  <div id="result-historical" class="result-historical"></div>
  <div class="actions result-actions">
    <button type="button" class="button button-secondary" id="copy-result">Copiar resultado</button>
    <button type="button" class="button button-secondary" id="share-result">Copiar enlace</button>
    <button type="button" class="button button-ghost" id="print-result">Imprimir</button>
  </div>
</section>
</div>
<div id="calc-toast" class="toast" hidden>
  <div class="toast-card" role="alert" aria-live="assertive">
    <p class="toast-kicker">Revisa el formulario</p>
    <p id="calc-toast-message" class="toast-message"></p>
    <button type="button" class="toast-close" id="calc-toast-close">Cerrar</button>
  </div>
</div>
<aside id="progress-panel" class="progress-panel" hidden></aside>"""


def related_cards(current: dict, all_items: list[dict], prefix: str) -> str:
    cards = []
    current_family = family_id(current)
    for item in current_by_family(all_items):
        if family_id(item) == current_family:
            continue
        href = prefix + live_path(item) + "index.html"
        name = item.get("family_name") or item["short_name"]
        cards.append(
            f'<a class="card" href="{href}"><span class="badge">En vigor</span>'
            f'<h3>{escape(name)}</h3><p>{escape(card_tests(item))}</p>'
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
        merit_label = (item["merits"].get("label") or "").lower()
        if "idioma" in merit_label:
            parts.append("Idiomas opcionales")
        else:
            parts.append("Concurso opcional")
    return " · ".join(parts) or (item.get("formula_human") or "")


def source_link(cfg: dict) -> str:
    src = cfg.get("fuente_oficial") or {}
    url = cfg.get("source_url") or src.get("url", "")
    return f'<a class="source-link" data-track="official-source" href="{escape(url)}">Ver fuente oficial</a>'


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
        extra_hub += f'<a href="{prefix}{hub}examenes-oficiales/index.html">Exámenes</a>'
    hub_links = (
        f'<nav class="opp-links" aria-label="Esta oposición">'
        f'<a href="{prefix}{hub}index.html">Oposición</a>'
        f'<a href="{prefix}{live_path(cfg)}index.html">Calcular nota</a>'
        + extra_hub
        + f'<a href="{prefix}fuentes/index.html">Fuentes</a></nav>'
    )
    body = f"""
    {crumbs(crumb_items)}
    <div class="hero hero-calc">
      <h1>{escape(heading)}</h1>
      {banner}
      {hub_links}
    </div>
    <div class="layout">
      <article class="tool">
        {calculator_form(cfg, prefix)}
        {ad_slot("after-result")}
        <section class="source-card">
          <p class="source-kicker">De dónde sale la fórmula</p>
          <p class="source-id">{escape(cfg.get("source_identifier", ""))}</p>
          <p>Convocatoria: {escape(cfg["convocatoria"])}.</p>
          <p>Organismo: {escape(cfg["administracion"])}.</p>
          <p>Apartado usado: {escape(cfg.get("source_section", ""))}.</p>
          <p>Última revisión: {escape(str(cfg.get("last_verified") or src.get("reviewed_at", "")))}.</p>
          <p>{source_link(cfg)} <span aria-hidden="true">→</span></p>
        </section>
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
      {ad_slot("in-content")}
      {list_block("Un ejemplo con números", copy["example"])}
      {list_block("Errores frecuentes al calcular", copy["mistakes"])}
      <h2>Fuente oficial</h2>
      <p>El enlace abre el boletín. Consultado el {escape(str(src.get("accessed_at", cfg.get("last_verified", ""))))}.</p>
      <p>{source_link(cfg)}.</p>
      {list_block("Qué no calcula esta página", copy["limits"])}
      {faq_block(faqs)}
      {related_cards(cfg, all_items, prefix)}
    </section>
    <script type="application/json" id="oposicion-config">{json.dumps(with_historical(cfg), ensure_ascii=False)}</script>
    """
    title = heading if heading == cfg["title"] else heading
    return page_shell(f"{title} | {BRAND}", cfg["meta_description"], canonical_path, depth, body, calculator=True)


def home(all_items: list[dict]) -> str:
    body = f"""
    <div class="hero hero-home">
      <p class="eyebrow">{BRAND}</p>
      <h1>Calculadoras de nota para oposiciones</h1>
      <p class="lede">Tu nota, con la fórmula de la convocatoria oficial. Elige el cuerpo, escribe aciertos y errores, y calcula con el boletín en vigor.</p>
      <form class="home-search" role="search" action="oposiciones/index.html" method="get">
        <label for="opo-search">¿Qué oposición preparas?</label>
        <input class="input" id="opo-search" name="q" type="search" placeholder="Policía Nacional" autocomplete="off">
      </form>
      <ul class="proof">
        <li>Convocatoria en vigor</li>
        <li>Sin cuenta ni servidor</li>
        <li>Fuente oficial enlazada</li>
      </ul>
    </div>
    <section>
      <h2 class="section-title">Oposiciones</h2>
      <div class="catalog" id="opo-catalog">{catalog_cards(all_items, dest="hub")}</div>
    </section>
    {ad_slot("home-mid")}
    <section class="content">
      <h2>Cómo funciona</h2>
      <ol class="how-steps">
        <li><strong>Entra en tu oposición.</strong> Ahí está la calculadora, el proceso y lo que dice el boletín. No es una media genérica para todos los cuerpos.</li>
        <li><strong>Escribe aciertos y errores.</strong> Los blancos se calculan solos. Si el tribunal anuló preguntas, cambia el número de preguntas válidas.</li>
        <li><strong>Lee el resultado con calma.</strong> Verás la puntuación y si llegas al mínimo oficial. Eso no es la nota de corte ni una plaza.</li>
      </ol>
      <p>No hay cuenta. El cálculo se hace en tu navegador. Los simulacros se quedan en este dispositivo: <a href="{PROGRESO_PATH}index.html">Mi progreso</a>. <a href="fuentes/index.html">Fuentes oficiales</a>.</p>
      <p>{escape(DISCLAIMER)}</p>
    </section>
    """
    return page_shell(
        f"{BRAND} — calculadoras de nota para oposiciones",
        "Calcula la nota de Guardia Civil, Policía Nacional, IIPP, Auxilio Judicial y Auxiliar AGE con la fórmula de la convocatoria en vigor. En el navegador, con fuente oficial.",
        "",
        0,
        body,
        website=True,
    )


def calculadoras_index(all_items: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Calculadoras", "")])}
    <div class="hero">
      <h1>Calculadoras de nota</h1>
      <p class="lede">Una calculadora por cuerpo, atada al boletín en vigor. Si cambia la fórmula, se actualiza aquí.</p>
    </div>
    <div class="catalog">{catalog_cards(all_items, "../")}</div>
    {ad_slot("catalog")}
    """
    return page_shell(
        seo_title("Calculadoras de nota oposiciones"),
        "Calculadoras de Guardia Civil, Policía Nacional, Ayudantes IIPP, Auxilio Judicial y Auxiliar AGE. Siempre con la convocatoria en vigor.",
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
    links = [(html_url, "Texto en el BOE")]
    if identifier and published:
        links.append((boe_pdf_url(identifier, published), "PDF del BOE"))
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
    {crumbs([("Inicio", prefix + "index.html"), ("Fuentes oficiales", "")])}
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
      <p>Estas cinco normas controlan el cálculo publicado. El enlace HTML y el PDF son del BOE; la calculadora es la URL estable de cada oposición.</p>
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
    {crumbs([("Inicio", prefix + "index.html"), ("Metodología", "")])}
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


def hub_nav(family: str, prefix: str, current: str) -> str:
    calc_folder = "auxiliar-administrativo-age" if family == "auxiliar-age" else family
    items = [
        ("Resumen", f"{prefix}oposiciones/{family}/index.html", "hub"),
        ("Calcular nota", f"{prefix}calculadoras/{calc_folder}/index.html", "calc"),
    ]
    for key in (HUBS.get(family) or {}).get("pages") or []:
        items.append(
            (NAV_LABELS[key], f"{prefix}oposiciones/{family}/{HUB_SLUGS[key]}/index.html", key)
        )
    bits = []
    for label, href, key in items:
        cls = ' class="is-current"' if key == current else ""
        bits.append(f'<a href="{href}"{cls}>{escape(label)}</a>')
    return f'<nav class="opp-links" aria-label="Secciones">{"".join(bits)}</nav>'


def oposiciones_index(opos: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Oposiciones", "")])}
    <div class="hero">
      <h1>Oposiciones</h1>
      <p class="lede">Tu convocatoria, tus pruebas y tu calculadora. Cinco cuerpos, cada uno con su boletín. Sin temario de academia ni cortes inventados.</p>
      <form class="home-search" role="search" action="index.html" method="get">
        <label for="opo-search">¿Qué oposición preparas?</label>
        <input class="input" id="opo-search" name="q" type="search" placeholder="Policía Nacional" autocomplete="off">
      </form>
    </div>
    <div class="catalog" id="opo-catalog">{catalog_cards(opos, "../", dest="hub")}</div>
    """
    return page_shell(
        seo_title("Oposiciones"),
        "Policía Nacional, Guardia Civil, Auxiliar AGE, Auxilio Judicial y Ayudantes IIPP: calculadora, proceso y fuente oficial de cada convocatoria.",
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
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), (name, "")])}
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
    ])}
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
    for text, link in hub["pruebas"]:
        if link == "calc":
            href = prefix + live_path(item) + "index.html"
            steps.append(f'<li>{escape(text)} <a href="{href}">Calcular</a></li>')
        elif link == "fisicas":
            href = f"{prefix}oposiciones/{family}/pruebas-fisicas/index.html"
            steps.append(f'<li>{escape(text)} <a href="{href}">Calcular físicas</a></li>')
        elif link == "baremo":
            href = f"{prefix}oposiciones/{family}/baremo/index.html"
            steps.append(f'<li>{escape(text)} <a href="{href}">Calcular baremo</a></li>')
        else:
            steps.append(f"<li>{escape(text)}</li>")
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
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), (name, "")])}
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
    {crumbs([("Inicio", prefix + "index.html"), ("Oposiciones", prefix + "oposiciones/index.html"), ("Policía Nacional", "")])}
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
    ])}
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


def pn_fisicas_page(item: dict) -> str:
    prefix = rel_prefix(3)
    family = "policia-nacional"
    inner_form = f"""
    <p class="calc-hint">Tablas del anexo II. 0 en un ejercicio elimina. Hace falta media de 5. No es plaza.</p>
    <form id="fisicas-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Categoría de la tabla</legend>
        <div class="fields">
          <label class="choice"><input type="radio" name="sex" value="hombres" checked> Hombres</label>
          <label class="choice"><input type="radio" name="sex" value="mujeres"> Mujeres</label>
        </div>
      </fieldset>
      <fieldset class="stage">
        <legend>Circuito de agilidad</legend>
        <p class="help">Tiempo en segundos y décimas. 11,7 s o más (hombres) y 12,8 s o más (mujeres) son 0 puntos.</p>
        <div class="fields fields-1">{number_input("circuit", "Tiempo (s)", None, step="0.1", placeholder="Ej. 10,2")}</div>
      </fieldset>
      <fieldset class="stage" id="force-hombres">
        <legend>Dominadas</legend>
        <p class="help">Hombres: repeticiones. 0 a 4 valen 0. 17 o más valen 10.</p>
        <div class="fields fields-1">{number_input("pullups", "Dominadas", None, required=False, placeholder="Ej. 10")}</div>
      </fieldset>
      <fieldset class="stage" id="force-mujeres" hidden>
        <legend>Suspensión en barra</legend>
        <p class="help">Mujeres: segundos manteniendo la posición. 35 s o menos valen 0. 95 s o más valen 10.</p>
        <div class="fields fields-1">{number_input("hang", "Segundos", None, required=False, placeholder="Ej. 62")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>1.000 metros</legend>
        <p class="help">Minutos y segundos. 3 min 49 s o más (hombres) y 4 min 46 s o más (mujeres) son 0.</p>
        <div class="fields">{number_input("run_min", "Minutos", None, placeholder="Ej. 3")}{number_input("run_sec", "Segundos", 59, placeholder="Ej. 18")}</div>
      </fieldset>
      <div class="actions actions-primary">
        <button type="submit" class="button button-primary">Calcular físicas</button>
      </div>
    </form>
    <div class="result-slot">
      <div id="fisicas-placeholder" class="result-placeholder">
        <p class="result-placeholder-kicker">Aún no hay nota</p>
        <p class="result-placeholder-title">Cuando pulses Calcular físicas verás</p>
        <ul>
          <li>Puntos de circuito, fuerza y carrera (0 a 10).</li>
          <li>La media aritmética.</li>
          <li>Si un 0 te elimina o si llegas al 5.</li>
        </ul>
      </div>
      <section id="fisicas-result" class="result-card" hidden>
        <div class="result-main">
          <p class="result-kicker">Media de las físicas</p>
          <p id="fisicas-avg" class="result-value"></p>
          <p id="fisicas-verdict" class="result-note"></p>
        </div>
        <div class="score-list">
          <div><span>Circuito</span><strong id="fisicas-circuit"></strong></div>
          <div><span id="fisicas-force-label">Fuerza</span><strong id="fisicas-force"></strong></div>
          <div><span>1.000 m</span><strong id="fisicas-run"></strong></div>
        </div>
      </section>
    </div>
    <div id="calc-toast" class="toast" hidden>
      <div class="toast-card" role="alert" aria-live="assertive">
        <p class="toast-kicker">Revisa el formulario</p>
        <p id="calc-toast-message" class="toast-message"></p>
        <button type="button" class="toast-close" id="calc-toast-close">Cerrar</button>
      </div>
    </div>
    <aside id="progress-panel" class="progress-panel" hidden></aside>
    <section class="content">
      <h2>Qué dice el anexo II</h2>
      <p>Tres ejercicios. Cada uno se puntúa de 0 a 10. Un 0 en cualquiera elimina. La nota de la prueba es la media, y hay que llegar a 5. La calificación final de la oposición es conocimientos más esta media (base 6.11).</p>
      <p>Hace falta certificado médico el día de la prueba. {BRAND} no sustituye al tribunal ni al certificado.</p>
      {fisicas_tables_html("policia-nacional")}
      <p>Fuente: {ext_a(item["source_url"], "BOE-A-2026-15055, anexo II")}.</p>
    </section>
    """
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Nacional", prefix + "oposiciones/policia-nacional/index.html"),
        ("Pruebas físicas", ""),
    ])}
    <div class="hero hero-calc">
      <h1>Calculadora de pruebas físicas Policía Nacional 2026</h1>
      <p class="calc-badge">Anexo II · BOE-A-2026-15055 · BOE oficial</p>
      {hub_nav(family, prefix, "fisicas")}
    </div>
    <div class="layout">
      <article class="tool">{inner_form}</article>
    </div>
    """
    return page_shell(
        seo_title("Pruebas físicas Policía Nacional", "2026"),
        "Puntúa circuito, dominadas o suspensión y 1.000 metros de Policía Nacional con las tablas del anexo II de BOE-A-2026-15055.",
        "oposiciones/policia-nacional/pruebas-fisicas/",
        3,
        body,
        fisicas=True,
    )


GC_LANGS = [
    ("aleman", "Alemán"),
    ("arabe", "Árabe"),
    ("frances", "Francés"),
    ("ingles", "Inglés"),
    ("italiano", "Italiano"),
    ("portugues", "Portugués"),
    ("ruso", "Ruso"),
]


def gc_fisicas_page(item: dict) -> str:
    prefix = rel_prefix(3)
    family = "guardia-civil"
    inner_form = f"""
    <p class="calc-hint">Mínimos del apéndice II. Cuatro pruebas eliminatorias. Apto o no apto. No es la tabla de Policía Nacional ni una plaza.</p>
    <form id="gc-fisicas-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Tabla oficial</legend>
        <div class="fields">
          <label class="choice"><input type="radio" name="sex" value="hombres" checked> Hombres</label>
          <label class="choice"><input type="radio" name="sex" value="mujeres"> Mujeres</label>
        </div>
        <div class="fields">
          <label class="choice"><input type="radio" name="band" value="lt35" checked> Menor de 35 años</label>
          <label class="choice"><input type="radio" name="band" value="a35"> 35 a 39 años</label>
          <label class="choice"><input type="radio" name="band" value="ge40"> 40 años o más</label>
        </div>
      </fieldset>
      <fieldset class="stage">
        <legend>2.000 metros (R2)</legend>
        <p class="help">Un intento. Hay que cubrir la distancia en un tiempo no superior al de tu tabla. Hombres menores de 35: 9 min 25 s o menos.</p>
        <div class="fields">{number_input("run_min", "Minutos", None, placeholder="Ej. 9")}{number_input("run_sec", "Segundos", 59, placeholder="Ej. 10")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Circuito de agilidad (C1)</legend>
        <p class="help">Tiempo en segundos. Dos intentos. Hombres menores de 35: 14,00 s o menos.</p>
        <div class="fields fields-1">{number_input("circuit", "Tiempo (s)", None, step="0.01", placeholder="Ej. 13,80")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Extensiones de brazos (P3)</legend>
        <p class="help">Repeticiones válidas. Dos intentos. Hombres menores de 35: 16 o más. Mujeres menores de 35: 11 o más.</p>
        <div class="fields fields-1">{number_input("pushups", "Extensiones", None, placeholder="Ej. 16")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>50 metros de natación (O1)</legend>
        <p class="help">Estilo libre. Un intento. Tiempo no superior al de la tabla. Hombres menores de 35: 70 s o menos.</p>
        <div class="fields fields-1">{number_input("swim", "Tiempo (s)", None, step="0.01", placeholder="Ej. 68")}</div>
      </fieldset>
      <div class="actions actions-primary">
        <button type="submit" class="button button-primary">Calcular físicas</button>
      </div>
    </form>
    <div class="result-slot">
      <div id="gc-fisicas-placeholder" class="result-placeholder">
        <p class="result-placeholder-kicker">Aún no hay resultado</p>
        <p class="result-placeholder-title">Cuando pulses Calcular físicas verás</p>
        <ul>
          <li>Si cada prueba es apto o no apto según tu sexo y tramo.</li>
          <li>El máximo o mínimo oficial que te aplica.</li>
          <li>Que las cuatro son eliminatorias: falla una y no sigues.</li>
        </ul>
      </div>
      <section id="gc-fisicas-result" class="result-card" hidden>
        <div class="result-main">
          <p class="result-kicker">Pruebas físicas Guardia Civil</p>
          <p id="gc-fisicas-verdict" class="result-note"></p>
        </div>
        <div class="score-list" id="gc-fisicas-list"></div>
      </section>
    </div>
    <div id="calc-toast" class="toast" hidden>
      <div class="toast-card" role="alert" aria-live="assertive">
        <p class="toast-kicker">Revisa el formulario</p>
        <p id="calc-toast-message" class="toast-message"></p>
        <button type="button" class="toast-close" id="calc-toast-close">Cerrar</button>
      </div>
    </div>
    <aside id="progress-panel" class="progress-panel" hidden></aside>
    <section class="content">
      <h2>Qué dice el apéndice II</h2>
      <p>Cuatro ejercicios, en el orden que fije el tribunal: resistencia 2.000 m, circuito, extensiones de brazos y 50 m de natación. Todas son eliminatorias. No hay media de 0 a 10, a diferencia de Policía Nacional.</p>
      <p>Los tramos son menor de 35 años; igual o mayor de 35 y menor de 40; e igual o mayor de 40. Carrera y natación: un intento. Circuito y extensiones: dos intentos. El día de la prueba hay que entregar certificado médico expedido en los 20 días anteriores, o la ficha médica válida de Defensa.</p>
      {fisicas_tables_html("guardia-civil")}
      <p>Fuente: {ext_a(item["source_url"], "BOE-A-2026-9982, apéndice II")}.</p>
    </section>
    """
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Guardia Civil", prefix + "oposiciones/guardia-civil/index.html"),
        ("Pruebas físicas", ""),
    ])}
    <div class="hero hero-calc">
      <h1>Calculadora de pruebas físicas Guardia Civil 2026</h1>
      <p class="calc-badge">Apéndice II · BOE-A-2026-9982 · BOE oficial</p>
      {hub_nav(family, prefix, "fisicas")}
    </div>
    <div class="layout">
      <article class="tool">{inner_form}</article>
    </div>
    """
    return page_shell(
        seo_title("Pruebas físicas Guardia Civil", "2026"),
        "Comprueba si eres apto en 2.000 m, circuito, extensiones y 50 m de natación de Guardia Civil 2026 con los mínimos del apéndice II de BOE-A-2026-9982.",
        "oposiciones/guardia-civil/pruebas-fisicas/",
        3,
        body,
        tools=("gc_fisicas",),
    )


def gc_baremo_page(item: dict) -> str:
    prefix = rel_prefix(3)
    family = "guardia-civil"
    lang_opts = "".join(f'<option value="{code}">{escape(label)}</option>' for code, label in GC_LANGS)
    lang_rows = []
    for code, label in GC_LANGS:
        lang_rows.append(
            f'<div class="fields" data-lang="{code}">'
            f"<p><strong>{escape(label)}</strong></p>"
            f'<div class="input-group"><label for="{code}_level">Nivel</label>'
            f'<select class="input" id="{code}_level" name="{code}_level">'
            '<option value="none">Sin acreditar</option>'
            '<option value="b2">B2 (5 puntos)</option>'
            '<option value="c1">C1 (7 puntos)</option>'
            '<option value="c2">C2 (9 puntos)</option>'
            "</select></div>"
            f'<div class="input-group"><label for="{code}_via">Vía</label>'
            f'<select class="input" id="{code}_via" name="{code}_via">'
            '<option value="eoi">Escuela Oficial de Idiomas</option>'
            '<option value="otro">Título del apéndice (Cambridge, Goethe, DELF…)</option>'
            '<option value="slp">Perfil SLP (solo FAS)</option>'
            "</select></div></div>"
        )
    inner_form = f"""
    <p class="calc-hint">Solo méritos del apéndice I. Topes: 13,5 profesionales, 27 académicos, 4,5 otros, 45 en total. Si un título no está en el boletín, no suma.</p>
    <form id="gc-baremo-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Turno</legend>
        <p class="help">El apartado A de méritos profesionales es exclusivo de tropa y marinería. Libre y Colegio usan el apartado B.</p>
        <div class="fields">
          <label class="choice"><input type="radio" name="turno" value="libre" checked> Acceso libre</label>
          <label class="choice"><input type="radio" name="turno" value="tropa"> Tropa y marinería</label>
          <label class="choice"><input type="radio" name="turno" value="colegio"> Colegio de Guardias Jóvenes</label>
        </div>
      </fieldset>
      <fieldset class="stage" id="baremo-tropa" hidden>
        <legend>Méritos profesionales (tropa)</legend>
        <p class="help">0,90 puntos por año completo como tropa y marinería, hasta 9. El empleo máximo: cabo 2,40 o cabo 1.º 3,60. Tope del bloque: 13,5.</p>
        <div class="fields">{number_input("tropa_years", "Años completos de tropa", 40, required=False, placeholder="Ej. 5")}</div>
        <div class="fields">
          <label class="choice"><input type="radio" name="tropa_rank" value="none" checked> Sin empleo de cabo</label>
          <label class="choice"><input type="radio" name="tropa_rank" value="cabo"> Cabo (2,40)</label>
          <label class="choice"><input type="radio" name="tropa_rank" value="cabo1"> Cabo 1.º (3,60)</label>
        </div>
      </fieldset>
      <fieldset class="stage" id="baremo-libre">
        <legend>Méritos profesionales (libre / Colegio)</legend>
        <p class="help">0,90 por año completo en la AGE, incluido el tiempo militar. Reservista voluntario: 0,025 por mes desde que se adquiere la condición.</p>
        <div class="fields">{number_input("age_years", "Años completos en la AGE", 40, required=False, placeholder="Ej. 2")}{number_input("reservist_months", "Meses como reservista", 120, required=False, placeholder="Ej. 12")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Nivel académico</legend>
        <p class="help">Solo una titulación en el punto 2.1: Bachiller o superior vale 2. Filología o Traducción e Interpretación en un idioma de interés vale 9 y no se suma el 2.1.</p>
        <div class="fields">
          <label class="choice"><input type="radio" name="academic" value="none" checked> Sin este mérito</label>
          <label class="choice"><input type="radio" name="academic" value="bachiller"> Bachiller o titulación superior (2)</label>
          <label class="choice"><input type="radio" name="academic" value="filologia"> Filología / Traducción (9)</label>
        </div>
        <div class="fields" id="baremo-degree-lang" hidden>
          <div class="input-group"><label for="degree_lang">Idioma de esa titulación</label>
          <select class="input" id="degree_lang" name="degree_lang">{lang_opts}</select></div>
        </div>
      </fieldset>
      <fieldset class="stage">
        <legend>Idiomas</legend>
        <p class="help">Por cada idioma solo cuenta la acreditación de mayor puntuación (B2 5, C1 7, C2 9). Idiomas del apéndice: alemán, árabe, francés, inglés, italiano, portugués y ruso. El SLP exige haber pertenecido a las FAS.</p>
        <label class="choice"><input type="checkbox" name="fas" value="1"> He pertenecido o pertenezco a las Fuerzas Armadas (necesario para SLP)</label>
        {''.join(lang_rows)}
      </fieldset>
      <fieldset class="stage">
        <legend>Permisos y deportista</legend>
        <p class="help">En cada grupo de permiso solo se barema uno. Deportista de alto nivel: últimos cinco años, un solo grupo, el de mayor puntuación.</p>
        <label class="choice"><input type="checkbox" name="perm_a" value="1"> Permiso A o A2 (3)</label>
        <label class="choice"><input type="checkbox" name="perm_ce" value="1"> Permiso C+E o D+E (3)</label>
        <label class="choice"><input type="checkbox" name="perm_c" value="1"> Permiso C1, C, C1+E, D1, D o D1+E (2)</label>
        <div class="fields">
          <div class="input-group"><label for="dan_group">Deportista de alto nivel</label>
          <select class="input" id="dan_group" name="dan_group">
            <option value="none">No</option>
            <option value="A">Grupo A (0,35 / año)</option>
            <option value="B">Grupo B (0,25 / año)</option>
            <option value="C">Grupo C (0,20 / año)</option>
          </select></div>
          {number_input("dan_years", "Años completos (máx. 5)", 5, required=False, placeholder="Ej. 2")}
        </div>
      </fieldset>
      <div class="actions actions-primary">
        <button type="submit" class="button button-primary">Calcular baremo</button>
      </div>
    </form>
    <div class="result-slot">
      <div id="gc-baremo-placeholder" class="result-placeholder">
        <p class="result-placeholder-kicker">Aún no hay total</p>
        <p class="result-placeholder-title">Cuando pulses Calcular baremo verás</p>
        <ul>
          <li>Puntos de profesionales, académicos y otros, con sus topes.</li>
          <li>El total hasta 45.</li>
          <li>Un desglose para copiarlo en la calculadora de nota.</li>
        </ul>
      </div>
      <section id="gc-baremo-result" class="result-card" hidden>
        <div class="result-main">
          <p class="result-kicker">Total del concurso</p>
          <p id="gc-baremo-total" class="result-value"></p>
          <p id="gc-baremo-note" class="result-note"></p>
        </div>
        <div id="gc-baremo-breakdown"></div>
      </section>
    </div>
    <div id="calc-toast" class="toast" hidden>
      <div class="toast-card" role="alert" aria-live="assertive">
        <p class="toast-kicker">Revisa el formulario</p>
        <p id="calc-toast-message" class="toast-message"></p>
        <button type="button" class="toast-close" id="calc-toast-close">Cerrar</button>
      </div>
    </div>
    <section class="content">
      <h2>Qué cubre (y qué no)</h2>
      <p>Reproduce el apéndice I de BOE-A-2026-9982: méritos alegados en la inscripción y poseídos al cierre de instancias. No suma diplomas propios, equivalencias solo profesionales ni idiomas fuera de esa lista.</p>
      <p>El total se puede pegar en la <a href="{prefix}calculadoras/guardia-civil/index.html">calculadora de nota</a> como concurso ya baremado. Prevalece el tribunal si hay duda sobre un documento.</p>
      <p>Fuente: {ext_a(item["source_url"], "BOE-A-2026-9982, apéndice I")}.</p>
    </section>
    """
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Guardia Civil", prefix + "oposiciones/guardia-civil/index.html"),
        ("Baremo", ""),
    ])}
    <div class="hero hero-calc">
      <h1>Calculadora de baremo Guardia Civil 2026</h1>
      <p class="calc-badge">Apéndice I · BOE-A-2026-9982 · BOE oficial</p>
      {hub_nav(family, prefix, "baremo")}
    </div>
    <div class="layout">
      <article class="tool">{inner_form}</article>
    </div>
    """
    return page_shell(
        seo_title("Baremo Guardia Civil", "2026"),
        "Calcula el concurso de Guardia Civil 2026 ítem a ítem con el apéndice I de BOE-A-2026-9982: tropa, AGE, idiomas, permisos y deportista de alto nivel.",
        "oposiciones/guardia-civil/baremo/",
        3,
        body,
        tools=("gc_baremo",),
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
        write(ROOT / "oposiciones" / family / "index.html", hub_home(item, hub))
        urls.append(f"{SITE}/oposiciones/{family}/")
        for key in hub.get("pages") or []:
            if key == "fisicas":
                if family == "policia-nacional":
                    page = pn_fisicas_page(item)
                elif family == "guardia-civil":
                    page = gc_fisicas_page(item)
                else:
                    continue
            elif key == "baremo":
                page = gc_baremo_page(item)
            else:
                page = writers[key](item, hub)
            write(ROOT / "oposiciones" / family / HUB_SLUGS[key] / "index.html", page)
            urls.append(f"{SITE}/oposiciones/{family}/{HUB_SLUGS[key]}/")
    return urls


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
        if family == "guardia-civil":
            trackers.append(
                {
                    "key": "tunotaopo:progress:guardia-civil-fisicas-2026",
                    "name": "Guardia Civil · físicas",
                    "href": "oposiciones/guardia-civil/pruebas-fisicas/",
                    "kind": "fisicas",
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
    ])}
    <div class="hero">
      <h1>Mi progreso</h1>
      <p class="lede">Los simulacros se quedan en este navegador. No hay cuenta ni servidor. Si cambias de dispositivo o borras los datos del sitio, se pierde el historial.</p>
    </div>
    <script type="application/json" id="progreso-config">{config}</script>
    <div id="progreso-root" class="progress-board"></div>
    <section class="content">
      <p>Para guardar un simulacro, calcula la nota o las físicas y pulsa Calcular. El resultado se añade aquí solo en este dispositivo.</p>
    </section>
    """
    return page_shell(
        seo_title("Mi progreso"),
        "Historial de simulacros de nota y físicas guardado en este navegador. Sin cuenta ni servidor.",
        PROGRESO_PATH,
        2,
        body,
        tools=("progreso",),
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


def build() -> None:
    opos = load_oposiciones()
    remove_retired_urls(opos)
    write(ROOT / "index.html", home(opos))
    write(ROOT / "calculadoras" / "index.html", calculadoras_index(opos))
    write(ROOT / "oposiciones" / "progreso" / "index.html", progreso_page(opos))
    stale = ROOT / "progreso"
    if stale.exists():
        shutil.rmtree(stale)
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
                "El cálculo se ejecuta en el navegador. El historial de simulacros, si lo usas, se guarda solo en este dispositivo (almacenamiento local) y no se envía a un servidor. Puedes verlo en Mi progreso.",
                "No hay cookies de analítica, AdSense ni redes publicitarias activas. Cuando exista un Publisher ID y un consentimiento válido, esta página se actualizará y se activará un CMP antes de cargar esos scripts.",
            ],
            extra=f'<p><a href="{rel_prefix(1)}{PROGRESO_PATH}index.html">Abrir Mi progreso</a>.</p>',
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
      <p class="lede">Comprueba la dirección o entra por el índice. No hay calculadoras ocultas ni URLs por provincia.</p>
      <p class="hero-actions"><a class="button button-primary" href="index.html">Ir al inicio</a>
      <a class="button button-secondary" href="oposiciones/index.html">Ver oposiciones</a></p>
    </div>
            """,
            noindex=True,
        ),
    )

    urls = [f"{SITE}/", f"{SITE}/calculadoras/"] + hub_urls
    seen_paths = set()
    for o in opos:
        for p in (o.get("family_path"), o["path"]):
            if p and p not in seen_paths:
                seen_paths.add(p)
                urls.append(f"{SITE}/{p}")
    for extra in ("metodologia/", "fuentes/", "aviso-legal/", "privacidad/", "cookies/", "contacto/", PROGRESO_PATH):
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
