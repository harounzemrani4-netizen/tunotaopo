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
  <link rel="stylesheet" href="{prefix}css/app.css?v=20260819i">
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
        tags.insert(1, f'<script src="{prefix}js/engine/scoring.js?v=20260819i" defer></script>')
        tags.insert(2, f'<script src="{prefix}js/components/calculator.js?v=20260819i" defer></script>')
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

    write(
        ROOT / "metodologia" / "index.html",
        simple_page(
            "Metodología de cálculo NotaOpo",
            "Metodología",
            "Cómo NotaOpo calcula la nota de cada oposición: fórmula del BOE, qué significa cada casilla y qué queda fuera.",
            "metodologia/",
            [
                "Cada oposición tiene una página estable. Hoy calcula con el boletín en vigor. Cuando salga el siguiente, actualizamos esa misma página y dejamos la convocatoria anterior en una URL de archivo. No se mezcla la fórmula de un año con la de otro.",
                "Escribes aciertos y errores. Los blancos se calculan solos (preguntas válidas menos aciertos menos errores). En las convocatorias publicadas aquí, las blancas no restan.",
                "La fórmula sale del boletín oficial enlazado en cada página, no de un blog ni de una academia. Un resumen de YouTube no manda sobre el BOE.",
                "Tres ideas que no son lo mismo: la puntuación que sacas con tus aciertos; el mínimo oficial de esa prueba en las bases; y la nota de corte, que depende del resto de aspirantes y se publica después. Superar un mínimo no es plaza.",
                "Si el tribunal anula preguntas y entra reserva, cambia el recuadro de preguntas válidas. El valor que viene relleno es el del boletín.",
                "Lo que no está en la norma de esa URL no se inventa: físicas sin tabla, baremo ítem a ítem, entrevista, reconocimiento médico o un corte de plaza.",
                "Antes de publicar una calculadora se prueban casos: todo correcto, todo a cero, mezcla, justo el mínimo, justo por debajo, apto/no apto y números imposibles.",
                DISCLAIMER,
            ],
        ),
    )

    fuente_items = "".join(
        f'<li><a href="{escape(o.get("source_url") or o["fuente_oficial"]["url"])}">{escape(o.get("source_identifier", o["short_name"]))}</a> — {escape(o.get("family_name") or o["short_name"])} ({escape(o.get("source_section", ""))})</li>'
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
                "Listado de las normas que controlan el cálculo. Cada calculadora enlaza el boletín y el apartado concreto. Verificado el 19 de agosto de 2026.",
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
