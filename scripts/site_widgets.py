"""Formularios, avisos y bloques reutilizables de las páginas."""

from __future__ import annotations

from urllib.parse import quote
from xml.sax.saxutils import escape

from site_catalog import family_id
from site_config import CONTACT_EMAIL, MONTHS_ES


def unpack_prueba(entry) -> tuple:
    text = entry[0]
    link = entry[1] if len(entry) > 1 else None
    tags = list(entry[2]) if len(entry) > 2 else []
    return text, link, tags


def process_flow(hub: dict) -> str:
    items = []
    for entry in hub.get("pruebas") or []:
        text, link, tags = unpack_prueba(entry)
        short = text.split(" — ", 1)[0]
        badges = "".join(f'<span class="flow-tag">{escape(tag)}</span>' for tag in tags)
        calc = ""
        if link == "calc":
            calc = '<span class="flow-calc">Calcular esta prueba →</span>'
        elif link == "fisicas":
            calc = '<span class="flow-calc">Calcular esta prueba →</span>'
        elif link == "baremo":
            calc = '<span class="flow-calc">Calcular esta prueba →</span>'
        items.append(f"<li><strong>{escape(short)}</strong>{badges}{calc}</li>")
    if not items:
        return ""
    return f'<ol class="process-flow" aria-label="Orden de las pruebas">{"".join(items)}</ol>'


def timeline_html(events: list[dict] | None) -> str:
    if not events:
        return ""
    marks = {"done": "✓", "current": "→", "next": "○", "todo": "○"}
    items = []
    for event in events:
        state = event.get("state") or "todo"
        note = f'<p class="timeline-note">{escape(event["note"])}</p>' if event.get("note") else ""
        source = ""
        if event.get("source_url"):
            label = event.get("source_label") or "Fuente oficial"
            source = f'<p class="timeline-note"><a href="{escape(event["source_url"])}" rel="noopener noreferrer">{escape(label)}</a></p>'
        items.append(
            f'<li class="is-{escape(state)}">'
            f'<span class="timeline-mark" aria-hidden="true">{marks.get(state, "○")}</span>'
            f'<div><p class="timeline-label">{escape(event["label"])}</p>'
            f'<p class="timeline-date">{escape(event["date"])}</p>{note}{source}</div></li>'
        )
    return f'<ol class="process-timeline">{"".join(items)}</ol>'


def changelog_html(hub: dict) -> str:
    updates = hub.get("updates") or []
    if not updates:
        return ""
    items = []
    for row in updates:
        src = ""
        if row.get("source_url"):
            label = row.get("source_label") or "Fuente"
            src = f' <a href="{escape(row["source_url"])}" rel="noopener noreferrer">{escape(label)} →</a>'
        items.append(
            f"<li><time datetime=\"{escape(row['date'])}\">{escape(es_date(row['date']))}</time>"
            f"<p>{escape(row['text'])}{src}</p></li>"
        )
    return (
        '<section class="changelog" aria-labelledby="changelog-title">'
        '<h2 id="changelog-title">Últimas actualizaciones</h2>'
        f"<ol>{''.join(items)}</ol>"
        "</section>"
    )

def report_error_href(name: str, convocatoria: str, page_url: str, kind: str) -> str:
    subject = f"Error en {kind}: {name}"
    body = (
        f"Oposición: {name}\n"
        f"Convocatoria: {convocatoria}\n"
        f"Página: {page_url}\n"
        f"Tipo de calculadora: {kind}\n\n"
        "Describe el error (sin pegar tu nota, aciertos ni datos personales):\n"
    )
    return f"mailto:{CONTACT_EMAIL}?subject={quote(subject)}&body={quote(body)}"


def report_error_link(name: str, convocatoria: str, page_url: str, kind: str) -> str:
    href = report_error_href(name, convocatoria, page_url, kind)
    return (
        f'<p class="report-error"><a href="{href}">¿Has detectado un error? Avísanos</a></p>'
    )


def tool_toolbar(report_href: str = "") -> str:
    report = ""
    if report_href:
        report = (
            f'<a class="button button-ghost" href="{escape(report_href)}">Reportar error</a>'
        )
    return (
        '<div class="actions tool-toolbar" aria-label="Herramientas de aula">'
        '<button type="button" class="button button-secondary" id="classroom-enter">Modo aula</button>'
        '<button type="button" class="button button-secondary" id="classroom-exit" hidden>Salir del modo aula</button>'
        '<button type="button" class="button button-secondary" id="share-native">Compartir</button>'
        '<button type="button" class="button button-secondary" id="show-qr">Mostrar QR</button>'
        f"{report}"
        "</div>"
        '<div id="qr-box" class="qr-box" hidden></div>'
    )


def result_persist_actions(*, copy_result: bool = False) -> str:
    copy_btns = ""
    if copy_result:
        copy_btns = (
            '<button type="button" class="button button-secondary" id="copy-result">Copiar resultado</button>'
            '<button type="button" class="button button-secondary" id="share-result">Copiar enlace</button>'
        )
    return (
        '<div class="actions result-actions">'
        f"{copy_btns}"
        '<button type="button" class="button button-secondary" id="save-progress" hidden>Guardar en Mi progreso</button>'
        '<button type="button" class="button button-ghost" id="print-result">Imprimir</button>'
        "</div>"
    )


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

def source_link(cfg: dict) -> str:
    src = cfg.get("fuente_oficial") or {}
    url = cfg.get("source_url") or src.get("url", "")
    return f'<a class="source-link" data-track="official-source" href="{escape(url)}">Ver fuente oficial</a>'

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


def segmented(
    name: str,
    options: list[tuple[str, str]],
    *,
    legend: str = "",
    checked: str | None = None,
) -> str:
    selected = options[0][0] if checked is None else checked
    bits = []
    for value, label in options:
        on = " checked" if value == selected else ""
        bits.append(
            f'<label class="segment">'
            f'<input type="radio" name="{escape(name)}" value="{escape(value)}"{on}>'
            f"<span>{escape(label)}</span></label>"
        )
    heading = f'<p class="choice-group-label" id="label-{escape(name)}">{escape(legend)}</p>' if legend else ""
    labelled = f' aria-labelledby="label-{escape(name)}"' if legend else f' aria-label="{escape(name)}"'
    return (
        f'<div class="choice-group">{heading}'
        f'<div class="segmented" role="radiogroup"{labelled}>{"".join(bits)}</div></div>'
    )


def choice_chips(items: list[tuple[str, str, str]]) -> str:
    bits = []
    for name, value, label in items:
        bits.append(
            f'<label class="segment">'
            f'<input type="checkbox" name="{escape(name)}" value="{escape(value)}">'
            f"<span>{escape(label)}</span></label>"
        )
    return f'<div class="segmented segmented-wrap">{"".join(bits)}</div>'


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


def calculator_form(cfg: dict, prefix: str = "", page_url: str = "") -> str:
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
    family_name = cfg.get("family_name") or cfg["short_name"]
    report_href = (
        report_error_href(family_name, cfg["convocatoria"], page_url, "nota")
        if page_url
        else ""
    )
    return f"""<form id="calc-form" class="calculator" novalidate autocomplete="off">
  {''.join(blocks)}
  <div class="actions actions-primary">
    <button type="submit" class="button button-primary">Calcular nota</button>
    <button type="reset" class="button button-secondary">Borrar datos</button>
  </div>
  {tool_toolbar(report_href)}
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
  {result_persist_actions(copy_result=True)}
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
