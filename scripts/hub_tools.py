"""Calculadoras de físicas y baremo de los hubs."""

from __future__ import annotations

from xml.sax.saxutils import escape

from fisicas_tables import fisicas_tables_html
from html_shell import crumbs, page_shell, rel_prefix, seo_title
from hub_nav import hub_nav
from site_config import BRAND, SITE
from site_widgets import (
    choice_chips,
    ext_a,
    number_input,
    report_error_href,
    report_error_link,
    result_persist_actions,
    segmented,
    source_link,
    tool_toolbar,
)


def pn_fisicas_page(item: dict) -> str:
    prefix = rel_prefix(3)
    family = "policia-nacional"
    sex = segmented(
        "sex",
        [("hombres", "Hombres"), ("mujeres", "Mujeres")],
        legend="Sexo",
        checked="hombres",
    )
    inner_form = f"""
    <p class="calc-hint">Tablas del anexo II. 0 en un ejercicio elimina. Hace falta media de 5. No es plaza.</p>
    <form id="fisicas-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Categoría de la tabla</legend>
        {sex}
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
      {tool_toolbar(report_error_href("Policía Nacional", item["convocatoria"], f"{SITE}/oposiciones/policia-nacional/pruebas-fisicas/", "físicas"))}
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
        {result_persist_actions()}
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
    {report_error_link("Policía Nacional", item["convocatoria"], f"{SITE}/oposiciones/policia-nacional/pruebas-fisicas/", "físicas")}
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
    ], "oposiciones/policia-nacional/pruebas-fisicas/")}
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


def pl_fisicas_page(item: dict) -> str:
    prefix = rel_prefix(3)
    family = "policia-local"
    sex = segmented(
        "sex",
        [("hombres", "Hombres"), ("mujeres", "Mujeres")],
        legend="Sexo",
        checked="hombres",
    )
    inner_form = f"""
    <p class="calc-hint">Tablas del anexo II de Madrid. Mínimo 5 en cada prueba. Las marcas intermedias se interpolan. No vale para otra ciudad.</p>
    <form id="pl-fisicas-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Categoría de la tabla</legend>
        {sex}
      </fieldset>
      <fieldset class="stage">
        <legend>800 metros</legend>
        <p class="help">Minutos y segundos. Hombres: 2:50 vale 5; 1:55 o menos vale 10. Mujeres: 3:30 vale 5; 2:35 o menos vale 10.</p>
        <div class="fields">{number_input("run800_min", "Minutos", None, placeholder="Ej. 2")}{number_input("run800_sec", "Segundos", 59, placeholder="Ej. 39")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>60 metros</legend>
        <p class="help">Segundos y centésimas. Hombres: 9,10 vale 5; 7,00 o menos vale 10. Mujeres: 10,40 vale 5; 8,30 o menos vale 10.</p>
        <div class="fields fields-1">{number_input("run60", "Tiempo (s)", None, step="0.01", placeholder="Ej. 8,68")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Balón medicinal</legend>
        <p class="help">Metros. Misma tabla para ambos sexos (5,50 m = 5; 10,50 m o más = 10). Hombres con balón de 5 kg; mujeres, 3 kg.</p>
        <div class="fields fields-1">{number_input("ball", "Distancia (m)", None, step="0.01", placeholder="Ej. 6,50")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Salto de longitud parado</legend>
        <p class="help">Metros. Hombres: 2,15 m vale 5; 3,15 m o más vale 10. Mujeres: 1,85 m vale 5; 2,85 m o más vale 10.</p>
        <div class="fields fields-1">{number_input("jump", "Distancia (m)", None, step="0.01", placeholder="Ej. 2,35")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Natación 25 metros</legend>
        <p class="help">Segundos y décimas. Hombres: 24,0 vale 5; 10,0 o menos vale 10. Mujeres: 26,0 vale 5; 12,0 o menos vale 10.</p>
        <div class="fields fields-1">{number_input("swim", "Tiempo (s)", None, step="0.1", placeholder="Ej. 21,2")}</div>
      </fieldset>
      <div class="actions actions-primary">
        <button type="submit" class="button button-primary">Calcular físicas</button>
      </div>
      {tool_toolbar(report_error_href("Policía Local Madrid", item["convocatoria"], f"{SITE}/oposiciones/policia-local/pruebas-fisicas/", "físicas"))}
    </form>
    <div class="result-slot">
      <div id="pl-fisicas-placeholder" class="result-placeholder">
        <p class="result-placeholder-kicker">Aún no hay nota</p>
        <p class="result-placeholder-title">Cuando pulses Calcular físicas verás</p>
        <ul>
          <li>Puntos de cada prueba (5 a 10, o menos de 5).</li>
          <li>La media solo si las cinco llegan a 5.</li>
          <li>Que eso no es plaza.</li>
        </ul>
      </div>
      <section id="pl-fisicas-result" class="result-card" hidden>
        <div class="result-main">
          <p class="result-kicker">Media de las físicas</p>
          <p id="pl-fisicas-avg" class="result-value"></p>
          <p id="pl-fisicas-verdict" class="result-note"></p>
        </div>
        <div class="score-list">
          <div><span>800 m</span><strong id="pl-fisicas-800"></strong></div>
          <div><span>60 m</span><strong id="pl-fisicas-60"></strong></div>
          <div><span>Balón</span><strong id="pl-fisicas-ball"></strong></div>
          <div><span>Salto</span><strong id="pl-fisicas-jump"></strong></div>
          <div><span>25 m natación</span><strong id="pl-fisicas-swim"></strong></div>
        </div>
        {result_persist_actions()}
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
    {report_error_link("Policía Local Madrid", item["convocatoria"], f"{SITE}/oposiciones/policia-local/pruebas-fisicas/", "físicas")}
    <section class="content">
      <h2>Qué dice el anexo II</h2>
      <p>Cinco pruebas, en el orden que fije el tribunal. Cada una se puntúa de 5 a 10. Hay que sacar 5 en una para hacer la siguiente. La nota es la media aritmética. Las marcas que no están en la tabla se interpolan con la anterior y la posterior.</p>
      <p>Hace falta certificado médico el día de la prueba. {BRAND} no sustituye al tribunal ni al certificado. Esta tabla es de Madrid, no de otra Policía Local.</p>
      {fisicas_tables_html("policia-local")}
      <p>Fuente: {ext_a("https://www.madrid.es/UnidadWeb/Contenidos/Oposiciones/2025/PoliciaTL2025/Ficheros/BasesPoliciaMunicipalboam9829.pdf", "BOAM núm. 9829, anexo II")}.</p>
    </section>
    """
    body = f"""
    {crumbs([
        ("Inicio", prefix + "index.html"),
        ("Oposiciones", prefix + "oposiciones/index.html"),
        ("Policía Local (Madrid)", prefix + "oposiciones/policia-local/index.html"),
        ("Pruebas físicas", ""),
    ], "oposiciones/policia-local/pruebas-fisicas/")}
    <div class="hero hero-calc">
      <h1>Calculadora de pruebas físicas Policía Local de Madrid</h1>
      <p class="calc-badge">Anexo II · BOAM núm. 9829 · Ayuntamiento de Madrid</p>
      {hub_nav(family, prefix, "fisicas")}
    </div>
    <div class="layout">
      <article class="tool">{inner_form}</article>
    </div>
    """
    return page_shell(
        seo_title("Pruebas físicas Policía Local Madrid", "2026"),
        "Puntúa 800 m, 60 m, balón, salto y 25 m de Policía Municipal de Madrid con las tablas del anexo II del BOAM 9829. Interpolación oficial. No vale para otra ciudad.",
        "oposiciones/policia-local/pruebas-fisicas/",
        3,
        body,
        tools=("pl_fisicas",),
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
    sex = segmented(
        "sex",
        [("hombres", "Hombres"), ("mujeres", "Mujeres")],
        legend="Sexo",
        checked="hombres",
    )
    band = segmented(
        "band",
        [
            ("lt35", "Menor de 35 años"),
            ("a35", "35 a 39 años"),
            ("ge40", "40 años o más"),
        ],
        legend="Tramo de edad",
        checked="lt35",
    )
    inner_form = f"""
    <p class="calc-hint">Mínimos del apéndice II. Cuatro pruebas eliminatorias. Apto o no apto. No es la tabla de Policía Nacional ni una plaza.</p>
    <form id="gc-fisicas-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Tabla oficial</legend>
        {sex}
        {band}
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
      {tool_toolbar(report_error_href("Guardia Civil", item["convocatoria"], f"{SITE}/oposiciones/guardia-civil/pruebas-fisicas/", "físicas"))}
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
        {result_persist_actions()}
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
    {report_error_link("Guardia Civil", item["convocatoria"], f"{SITE}/oposiciones/guardia-civil/pruebas-fisicas/", "físicas")}
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
    ], "oposiciones/guardia-civil/pruebas-fisicas/")}
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
    turno = segmented(
        "turno",
        [
            ("libre", "Acceso libre"),
            ("tropa", "Tropa y marinería"),
            ("colegio", "Colegio de Guardias Jóvenes"),
        ],
        legend="Turno de acceso",
        checked="libre",
    )
    tropa_rank = segmented(
        "tropa_rank",
        [
            ("none", "Sin empleo de cabo"),
            ("cabo", "Cabo (2,40)"),
            ("cabo1", "Cabo 1.º (3,60)"),
        ],
        legend="Empleo",
        checked="none",
    )
    academic = segmented(
        "academic",
        [
            ("none", "Sin este mérito"),
            ("bachiller", "Bachiller o titulación superior (2)"),
            ("filologia", "Filología / Traducción (9)"),
        ],
        legend="Titulación",
        checked="none",
    )
    fas = choice_chips(
        [("fas", "1", "He pertenecido o pertenezco a las Fuerzas Armadas (necesario para SLP)")]
    )
    permisos = choice_chips(
        [
            ("perm_a", "1", "Permiso A o A2 (3)"),
            ("perm_ce", "1", "Permiso C+E o D+E (3)"),
            ("perm_c", "1", "Permiso C1, C, C1+E, D1, D o D1+E (2)"),
        ]
    )
    inner_form = f"""
    <p class="calc-hint">Solo méritos del apéndice I. Topes: 13,5 profesionales, 27 académicos, 4,5 otros, 45 en total. Si un título no está en el boletín, no suma.</p>
    <form id="gc-baremo-form" class="calculator" novalidate autocomplete="off">
      <fieldset class="stage">
        <legend>Turno</legend>
        <p class="help">El apartado A de méritos profesionales es exclusivo de tropa y marinería. Libre y Colegio usan el apartado B.</p>
        {turno}
      </fieldset>
      <fieldset class="stage" id="baremo-tropa" hidden>
        <legend>Méritos profesionales (tropa)</legend>
        <p class="help">0,90 puntos por año completo como tropa y marinería, hasta 9. El empleo máximo: cabo 2,40 o cabo 1.º 3,60. Tope del bloque: 13,5.</p>
        <div class="fields">{number_input("tropa_years", "Años completos de tropa", 40, required=False, placeholder="Ej. 5")}</div>
        {tropa_rank}
      </fieldset>
      <fieldset class="stage" id="baremo-libre">
        <legend>Méritos profesionales (libre / Colegio)</legend>
        <p class="help">0,90 por año completo en la AGE, incluido el tiempo militar. Reservista voluntario: 0,025 por mes desde que se adquiere la condición.</p>
        <div class="fields">{number_input("age_years", "Años completos en la AGE", 40, required=False, placeholder="Ej. 2")}{number_input("reservist_months", "Meses como reservista", 120, required=False, placeholder="Ej. 12")}</div>
      </fieldset>
      <fieldset class="stage">
        <legend>Nivel académico</legend>
        <p class="help">Solo una titulación en el punto 2.1: Bachiller o superior vale 2. Filología o Traducción e Interpretación en un idioma de interés vale 9 y no se suma el 2.1.</p>
        {academic}
        <div class="fields" id="baremo-degree-lang" hidden>
          <div class="input-group"><label for="degree_lang">Idioma de esa titulación</label>
          <select class="input" id="degree_lang" name="degree_lang">{lang_opts}</select></div>
        </div>
      </fieldset>
      <fieldset class="stage">
        <legend>Idiomas</legend>
        <p class="help">Por cada idioma solo cuenta la acreditación de mayor puntuación (B2 5, C1 7, C2 9). Idiomas del apéndice: alemán, árabe, francés, inglés, italiano, portugués y ruso. El SLP exige haber pertenecido a las FAS.</p>
        {fas}
        {''.join(lang_rows)}
      </fieldset>
      <fieldset class="stage">
        <legend>Permisos y deportista</legend>
        <p class="help">En cada grupo de permiso solo se barema uno. Deportista de alto nivel: últimos cinco años, un solo grupo, el de mayor puntuación.</p>
        {permisos}
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
      {tool_toolbar(report_error_href("Guardia Civil", item["convocatoria"], f"{SITE}/oposiciones/guardia-civil/baremo/", "baremo"))}
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
        {result_persist_actions()}
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
    {report_error_link("Guardia Civil", item["convocatoria"], f"{SITE}/oposiciones/guardia-civil/baremo/", "baremo")}
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
    ], "oposiciones/guardia-civil/baremo/")}
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
