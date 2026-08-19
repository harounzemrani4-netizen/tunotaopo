"""Tablas oficiales de físicas para HTML. Literal del BOE, no estimaciones."""

from __future__ import annotations

from xml.sax.saxutils import escape


def _range_label(min_v, max_v, *, kind: str, unit: str = "") -> str:
    def n(value) -> str:
        if isinstance(value, float) and not value.is_integer():
            return str(value).replace(".", ",")
        if isinstance(value, float) and value.is_integer():
            return str(int(value))
        return str(value)

    u = f" {unit}" if unit else ""
    if kind == "run":
        def clock(sec: int) -> str:
            minutes, seconds = divmod(int(sec), 60)
            return f"{minutes}:{seconds:02d}"

        if min_v is None:
            return clock(int(max_v)) + " o menos"
        if max_v is None:
            return clock(int(min_v)) + " o más"
        return clock(int(min_v)) + " – " + clock(int(max_v))
    if min_v is None:
        return n(max_v) + u + " o menos"
    if max_v is None:
        return n(min_v) + u + " o más"
    if min_v == max_v:
        return n(min_v) + u
    return n(min_v) + " – " + n(max_v) + u


def _score_table(title: str, headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{escape(cell)}</td>" for cell in row) + "</tr>" for row in rows
    )
    return (
        f"<h3>{escape(title)}</h3>"
        '<div class="table-wrap"><table class="plain-table">'
        f"<thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"
    )


PN_CIRCUIT = {
    "hombres": [
        (11.7, None, 0),
        (11.5, 11.6, 1),
        (11.3, 11.4, 2),
        (11.0, 11.2, 3),
        (10.6, 10.9, 4),
        (10.2, 10.5, 5),
        (9.8, 10.1, 6),
        (9.4, 9.7, 7),
        (8.9, 9.3, 8),
        (8.3, 8.8, 9),
        (None, 8.2, 10),
    ],
    "mujeres": [
        (12.8, None, 0),
        (12.6, 12.7, 1),
        (12.4, 12.5, 2),
        (12.1, 12.3, 3),
        (11.7, 12.0, 4),
        (11.3, 11.6, 5),
        (10.9, 11.2, 6),
        (10.4, 10.8, 7),
        (9.9, 10.3, 8),
        (9.4, 9.8, 9),
        (None, 9.3, 10),
    ],
}

PN_PULLUPS = [
    (0, 4, 0),
    (5, 5, 1),
    (6, 6, 2),
    (7, 7, 3),
    (8, 9, 4),
    (10, 11, 5),
    (12, 13, 6),
    (14, 14, 7),
    (15, 15, 8),
    (16, 16, 9),
    (17, None, 10),
]

PN_HANG = [
    (None, 35, 0),
    (36, 40, 1),
    (41, 45, 2),
    (46, 51, 3),
    (52, 56, 4),
    (57, 62, 5),
    (63, 69, 6),
    (70, 77, 7),
    (78, 85, 8),
    (86, 94, 9),
    (95, None, 10),
]

PN_RUN = {
    "hombres": [
        (229, None, 0),
        (223, 228, 1),
        (217, 222, 2),
        (211, 216, 3),
        (205, 210, 4),
        (199, 204, 5),
        (193, 198, 6),
        (187, 192, 7),
        (181, 186, 8),
        (175, 180, 9),
        (None, 174, 10),
    ],
    "mujeres": [
        (286, None, 0),
        (277, 285, 1),
        (268, 276, 2),
        (259, 267, 3),
        (250, 258, 4),
        (241, 249, 5),
        (232, 240, 6),
        (223, 231, 7),
        (214, 222, 8),
        (205, 213, 9),
        (None, 204, 10),
    ],
}


def pn_fisicas_tables() -> str:
    circuit_rows = []
    for score in range(10, -1, -1):
        h = next(r for r in PN_CIRCUIT["hombres"] if r[2] == score)
        m = next(r for r in PN_CIRCUIT["mujeres"] if r[2] == score)
        circuit_rows.append(
            [
                str(score),
                _range_label(h[0], h[1], kind="sec", unit="s"),
                _range_label(m[0], m[1], kind="sec", unit="s"),
            ]
        )
    pull_rows = [
        [str(s), _range_label(a, b, kind="int")]
        for a, b, s in reversed(PN_PULLUPS)
    ]
    hang_rows = [
        [str(s), _range_label(a, b, kind="int", unit="s")]
        for a, b, s in reversed(PN_HANG)
    ]
    run_rows = []
    for score in range(10, -1, -1):
        h = next(r for r in PN_RUN["hombres"] if r[2] == score)
        m = next(r for r in PN_RUN["mujeres"] if r[2] == score)
        run_rows.append(
            [
                str(score),
                _range_label(h[0], h[1], kind="run"),
                _range_label(m[0], m[1], kind="run"),
            ]
        )
    return (
        "<h2 id=\"tablas-fisicas\">Tablas de las físicas (anexo II)</h2>"
        "<p>Cada ejercicio vale de 0 a 10. Un 0 elimina. La media tiene que ser 5 o más. "
        "El 10 no es plaza: es el techo de esa tabla. Hombres y mujeres no usan la misma marca.</p>"
        + _score_table(
            "Circuito de agilidad (segundos). Menos tiempo, más puntos.",
            ["Puntos", "Hombres", "Mujeres"],
            circuit_rows,
        )
        + _score_table("Dominadas (hombres)", ["Puntos", "Repeticiones"], pull_rows)
        + _score_table("Suspensión en barra (mujeres)", ["Puntos", "Tiempo"], hang_rows)
        + _score_table(
            "1.000 metros (min:s). Menos tiempo, más puntos.",
            ["Puntos", "Hombres", "Mujeres"],
            run_rows,
        )
    )


def gc_fisicas_tables() -> str:
    rows = [
        ["2.000 m (máx.)", "Hombres", "9:25", "9:48", "10:33"],
        ["2.000 m (máx.)", "Mujeres", "11:14", "11:35", "12:49"],
        ["Circuito (máx. s)", "Hombres", "14,00", "14,40", "15,10"],
        ["Circuito (máx. s)", "Mujeres", "16,00", "16,40", "17,90"],
        ["Extensiones (mín.)", "Hombres", "16", "16", "14"],
        ["Extensiones (mín.)", "Mujeres", "11", "11", "9"],
        ["50 m natación (máx. s)", "Hombres", "70,00", "71,00", "73,00"],
        ["50 m natación (máx. s)", "Mujeres", "81,00", "83,00", "88,00"],
    ]
    return (
        "<h2 id=\"tablas-fisicas\">Mínimos de las físicas (apéndice II)</h2>"
        "<p>Guardia Civil <strong>no puntúa de 0 a 10</strong> las físicas, a diferencia de Policía Nacional. "
        "Las cuatro pruebas son eliminatorias: apto o no apto. El tiempo no puede ser superior al de tu sexo y tramo; "
        "las extensiones no pueden ser inferiores. Igualar la marca es apto.</p>"
        + _score_table(
            "Marcas máximas o mínimas según edad",
            ["Prueba", "Sexo", "Menor de 35", "35 a 39", "40 o más"],
            rows,
        )
    )


def fisicas_tables_html(family: str) -> str:
    if family == "policia-nacional":
        return pn_fisicas_tables()
    if family == "guardia-civil":
        return gc_fisicas_tables()
    return ""
