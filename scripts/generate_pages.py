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
  <link rel="stylesheet" href="{prefix}css/app.css?v=20260819k">
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


def catalog_cards(items: list[dict], href_prefix: str = "") -> str:
    cards = []
    for item in current_by_family(items):
        org = item["administracion"].split(",")[0].split(" / ")[0]
        name = item.get("family_name") or item["short_name"]
        badge = "En vigor" if item.get("is_current") else str(item.get("anio", ""))
        cards.append(
            f'<a class="card catalog-card" href="{href_prefix}{live_path(item)}index.html">'
            f'<div class="card-meta"><span class="badge">{escape(badge)}</span>'
            f'<span class="card-org">{escape(org)}</span></div>'
            f"<h2>{escape(name)}</h2>"
            f'<p class="card-kind">{escape(item.get("formula_human") or calc_kind(item))}</p>'
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
        tags.insert(1, f'<script src="{prefix}js/engine/scoring.js?v=20260819k" defer></script>')
        tags.insert(2, f'<script src="{prefix}js/components/calculator.js?v=20260819k" defer></script>')
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


def calculator_form(cfg: dict) -> str:
    blocks = [form_guide(cfg)]
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
        blocks.append(
            f'<fieldset class="stage"><legend>{escape(m["label"])}</legend>'
            f'<p class="help">{escape(m.get("help", "Si no tienes este apartado o no quieres sumarlo, déjalo vacío."))}</p>'
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
  <aside class="glossary" role="note">
    <h2>Tres ideas que no son lo mismo</h2>
    <dl>
      <div><dt>Mínimo oficial</dt><dd>El suelo que marcan las bases para esa prueba. Si no lo alcanzas, sueles quedar fuera de esa prueba.</dd></div>
      <div><dt>Nota de corte</dt><dd>La marca el resto de aspirantes cuando el tribunal publica la lista. Esta página no la inventa.</dd></div>
      <div><dt>Plaza</dt><dd>Depende de la lista final. Superar un mínimo no es obtener plaza.</dd></div>
    </dl>
  </aside>
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
</div>"""


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
            f'<h3>{escape(name)}</h3><p>{escape(calc_kind(item))}</p>'
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
    crumb_items = [
        ("Inicio", prefix + "index.html"),
        ("Calculadoras", prefix + "calculadoras/index.html"),
    ]
    if variant == "archive":
        crumb_items.append((family_name, prefix + family_path + "index.html"))
        crumb_items.append((f"Convocatoria {cfg['anio']}", ""))
        banner = (
            f'<p class="archive-note">Esta URL guarda la convocatoria de {escape(str(cfg["anio"]))} '
            f"({escape(cfg.get('source_identifier', ''))}). La calculadora estable de {escape(family_name)}, "
            f"la que se actualiza cuando sale el siguiente boletín, está en "
            f'<a href="{prefix}{family_path}index.html">{escape(family_name)}</a>.</p>'
        )
    else:
        crumb_items.append((family_name, ""))
        banner = (
            f'<p class="convocatoria-line"><strong>Convocatoria en vigor:</strong> {escape(cfg["convocatoria"])} '
            f'({escape(cfg.get("source_identifier", ""))}). Esta página no caduca el 1 de enero: cuando salga el '
            "siguiente boletín, actualizamos la fórmula aquí y dejamos la anterior en archivo.</p>"
        )
    faqs = [
        (
            "¿Sirve el año que viene?",
            "Sí. Esta es la calculadora de la oposición, no de un único año. Usas siempre la convocatoria en vigor. "
            "Si el próximo boletín cambia la fórmula, se actualiza esta página y la anterior queda en una URL de archivo.",
        )
    ] + list(copy["faqs"])
    body = f"""
    {crumbs(crumb_items)}
    <div class="hero">
      <h1>{escape(cfg["h1"])}</h1>
      <p class="lede">{escape(cfg["lede"])}</p>
      {banner}
      <div class="formula-note">
        <h2>Fórmula de esta convocatoria</h2>
        <p>{escape(cfg["formula_human"])}</p>
        <p class="formula-note-help">Abajo escribes aciertos y errores. Los blancos se calculan solos. Cada casilla indica qué va en ella.</p>
      </div>
    </div>
    {ad_slot("after-hero")}
    <div class="layout">
      <article class="tool">
        {calculator_form(cfg)}
        {ad_slot("after-result")}
        <section class="source-card">
          <p class="source-kicker">De dónde sale la fórmula</p>
          <p class="source-id">{escape(cfg.get("source_identifier", ""))}</p>
          <p>Convocatoria: {escape(cfg["convocatoria"])}.</p>
          <p>Organismo: {escape(cfg["administracion"])}.</p>
          <p>Apartado usado: {escape(cfg.get("source_section", ""))}.</p>
          <p>Última revisión de esta página: {escape(str(cfg.get("last_verified") or src.get("reviewed_at", "")))}.</p>
          <p>{source_link(cfg)} <span aria-hidden="true">→</span></p>
        </section>
        <p class="notice">{escape(DISCLAIMER)}</p>
      </article>
    </div>
    <section class="content">
      <h2>Cómo se calcula en esta convocatoria</h2>
      {''.join(f'<p>{escape(p)}</p>' for p in copy["how"])}
      {ad_slot("in-content")}
      {list_block("Un ejemplo con números", copy["example"])}
      {list_block("Errores frecuentes al calcular", copy["mistakes"])}
      <h2>Fuente oficial</h2>
      <p>El enlace abre el boletín. Consultado el {escape(str(src.get("accessed_at", cfg.get("last_verified", ""))))}.</p>
      <p>{source_link(cfg)}.</p>
      {list_block("Qué no calcula esta página", copy["limits"])}
      {faq_block(faqs)}
      {affiliate_slot()}
      {related_cards(cfg, all_items, prefix)}
    </section>
    <script type="application/json" id="oposicion-config">{json.dumps(with_historical(cfg), ensure_ascii=False)}</script>
    """
    return page_shell(cfg["title"], cfg["meta_description"], canonical_path, depth, body, calculator=True)


def home(all_items: list[dict]) -> str:
    upcoming = "".join(
        f"<li><strong>{escape(item['name'])}</strong> — {escape(item['reason'])}</li>"
        for item in UPCOMING
    )
    body = f"""
    <div class="hero hero-home">
      <p class="eyebrow">Calculadoras por oposición</p>
      <h1>Tu nota, con la fórmula del BOE</h1>
      <p class="lede">Elige la oposición, escribe aciertos y errores, y obtienes la nota con la convocatoria que está en vigor. El año que viene esta página sigue valiendo: si cambia el boletín, se actualiza la fórmula.</p>
      <ul class="proof">
        <li>Convocatoria en vigor</li>
        <li>Sin cuenta ni servidor</li>
        <li>Fuente oficial enlazada</li>
      </ul>
    </div>
    <section>
      <h2 class="section-title">Calculadoras listas</h2>
      <div class="catalog">{catalog_cards(all_items)}</div>
    </section>
    {ad_slot("home-mid")}
    <section class="content">
      <h2>Cómo funciona</h2>
      <ol class="how-steps">
        <li><strong>Elige la oposición.</strong> Guardia Civil, Policía Nacional, IIPP… cada una usa su boletín. No es una media genérica para todos los años mezclados.</li>
        <li><strong>Escribe aciertos y errores.</strong> Los blancos se calculan solos. Si el tribunal anuló preguntas, cambia el número de preguntas válidas.</li>
        <li><strong>Lee el resultado con calma.</strong> Verás la puntuación y si llegas al <em>mínimo oficial</em>. Eso no es la nota de corte ni una plaza.</li>
      </ol>
      <p>No hay cuenta ni se envían tus números a un servidor. El cálculo se hace en tu navegador. Consulta la <a href="metodologia/index.html">metodología</a> y las <a href="fuentes/index.html">fuentes oficiales</a>.</p>
      <p>{escape(DISCLAIMER)}</p>
      <aside class="note-quiet">
        <h2>Aún no publicadas</h2>
        <p>Investigadas, sin URL propia hasta que la fuente aplicable esté cerrada.</p>
        <ul>{upcoming}</ul>
      </aside>
    </section>
    """
    return page_shell(
        "NotaOpo — calculadoras de oposiciones por convocatoria",
        "Calcula la nota de Guardia Civil, Policía Nacional, IIPP, Auxilio Judicial y Auxiliar AGE con la fórmula de la convocatoria en vigor. En el navegador, con fuente oficial.",
        "",
        0,
        body,
    )


def calculadoras_index(all_items: list[dict]) -> str:
    body = f"""
    {crumbs([("Inicio", "../index.html"), ("Calculadoras", "")])}
    <div class="hero">
      <h1>Calculadoras por oposición</h1>
      <p class="lede">Una página estable por cuerpo. Hoy usa el boletín en vigor. El año que viene sigue siendo la misma dirección: si cambia la fórmula, se actualiza aquí y la convocatoria anterior queda en archivo.</p>
    </div>
    <section class="content">
      <h2>Cómo usar una calculadora</h2>
      <ol class="how-steps">
        <li><strong>Abre la de tu oposición.</strong> Guardia Civil no usa la misma fórmula que Policía Nacional ni que Auxilio Judicial.</li>
        <li><strong>Escribe aciertos y errores.</strong> Los blancos se calculan solos. Las casillas opcionales se pueden dejar como están.</li>
        <li><strong>Lee el resultado con calma.</strong> Verás si llegas al mínimo de las bases. Eso no es plaza ni la nota de corte.</li>
      </ol>
    </section>
    <div class="catalog">{catalog_cards(all_items, "../")}</div>
    {ad_slot("catalog")}
    """
    return page_shell(
        "Calculadoras NotaOpo",
        "Índice de calculadoras NotaOpo: Guardia Civil, Policía Nacional, Ayudantes IIPP, Auxilio Judicial y Auxiliar AGE. Siempre con la convocatoria en vigor.",
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
      <p>Blogs de academias, resúmenes de YouTube, foros o calculadoras genéricas no mandan sobre el BOE. Si una cifra no está en las normas o portales de esta página, NotaOpo no la usa.</p>
    </section>
    """
    return page_shell(
        "Fuentes oficiales de las calculadoras",
        "Boletines del BOE, PDFs, listas históricas y portales oficiales que controlan las fórmulas de NotaOpo. Verificado el 19 de agosto de 2026.",
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
    upcoming = "".join(
        f"<li><strong>{escape(item['name'])}</strong> — {escape(item['reason'])}</li>"
        for item in UPCOMING
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
            "Pasa de puntuación directa a una escala (por ejemplo 0–20) con un umbral que publica el tribunal. Sin ese umbral de esta convocatoria, NotaOpo no interpola ni afirma el 10. En IIPP el recuadro es opcional y vacío significa «sin umbral».",
        ),
        (
            "Suma y concurso",
            "Las pruebas que puntúan se suman. El concurso o los idiomas, si los escribes, son un total ya baremado: la casilla no calcula ítem a ítem.",
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
      <p>Ante cualquier discrepancia prevalece la convocatoria oficial. NotaOpo es independiente: no está afiliada ni respaldada por el organismo convocante.</p>

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
        <li><strong>Lo opcional.</strong> Concurso, idiomas, umbral del tribunal u objetivo: vacío significa que no se suma ni se usa. El concurso de Guardia Civil es un total ya baremado (0 a 45), no el apéndice ítem a ítem.</li>
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
        <li>Físicas sin la tabla de esa convocatoria, entrevista, reconocimiento médico o psicotécnico de Policía Nacional calificado por el tribunal.</li>
        <li>Baremo ítem a ítem de méritos (apéndice I de Guardia Civil, Fuerzas Armadas o deportista de alto nivel en Policía Nacional).</li>
        <li>Una carrera o un grado superior como puntos extra en Escala Básica: el título exigido es Bachiller.</li>
        <li>La transformada de Auxiliar AGE 0–50 sin el PDF de criterios CPS de esta convocatoria.</li>
        <li>El umbral directo de IIPP tomado de 2025 como si ya valiera para 2026.</li>
        <li>Un corte de plaza de esta convocatoria, el número de convocados a psicofísicas o cuántos caben en el 1,75 por plaza de Policía Nacional.</li>
        <li>Policía Local / Municipal: no hay una fórmula única de España. Hace falta ciudad y boletín.</li>
      </ul>

      <h2 id="pruebas">Cómo se comprueba</h2>
      <p>Antes de publicar una calculadora se ejecutan casos independientes: todo correcto, todo a cero, mezcla, justo el mínimo, justo por debajo, apto/no apto, desbordes (más aciertos que preguntas) y valores no enteros donde toca entero. Si el BOE y el motor no coinciden, prevalece el BOE y no se publica esa cuenta.</p>
      <p>Última revisión de estas reglas: 19 de agosto de 2026. Las normas concretas están en <a href="{prefix}fuentes/index.html">Fuentes oficiales</a>.</p>

      <h2>Próximas calculadoras</h2>
      <p>No se abre una URL de cálculo hasta que hay convocatoria y fórmula cerradas.</p>
      <ul>{upcoming}</ul>

      <p class="notice">{escape(DISCLAIMER)}</p>
    </section>
    """
    return page_shell(
        "Metodología de cálculo NotaOpo",
        "Cómo NotaOpo calcula la nota: modelos del motor, mínimo frente a corte, blancos y reserva, y la fórmula de cada oposición según su BOE.",
        "metodologia/",
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
    seen_paths = set()
    for o in opos:
        for p in (o.get("family_path"), o["path"]):
            if p and p not in seen_paths:
                seen_paths.add(p)
                urls.append(f"{SITE}/{p}")
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
