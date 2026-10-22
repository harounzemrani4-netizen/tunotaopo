DISCLAIMER = (
    "Herramienta independiente de cálculo orientativo basada en la convocatoria indicada. "
    "No está afiliada ni respaldada por el organismo convocante. "
    "Ante cualquier discrepancia prevalece siempre la convocatoria oficial."
)

PAGES = {
    "guardia-civil-2026": {
        "how": [
            "La base 7.3 fija la puntuación de cada prueba que suma como Px = Y × (A − E/(N−1)) / T. En esta convocatoria, N = 4, así que cada error resta un tercio de acierto. Las preguntas en blanco no restan.",
            "Conocimientos: Y = 100 y T = 100 (mínimo 50). Inglés: Y = 20 y T = 20 (mínimo 8). Psicotécnico de aptitudes intelectuales: Y = 30 y T = 80 (mínimo 12). T es el número de preguntas válidas del cuestionario: si el tribunal anula alguna y entra reserva, T cambia.",
            "Ortografía y gramática no puntúan. La base 7.4 y 7.5 las califica como apto o no apto: seis o más errores excluyen del proceso. Superar el mínimo de una prueba no equivale a obtener plaza ni a un corte publicado después.",
            "La fase de oposición es la suma de las tres pruebas que puntúan (máximo 150). El concurso, si lo introduces, es un total ya baremado entre 0 y 45 (base 7.1). El total del proceso es la suma de ambas fases (base 7.9)."
        ],
        "example": [
            "70 aciertos y 15 errores en conocimientos: 100 × (70 − 15/3) / 100 = 65 puntos.",
            "14 aciertos y 3 errores en inglés: 20 × (14 − 1) / 20 = 13 puntos.",
            "55 aciertos y 9 errores en psicotécnico: 30 × (55 − 3) / 80 = 19,5 puntos.",
            "Suma de oposición: 97,5. Con 45 de concurso el total del proceso sería 142,5. Eso no dice si hay plaza."
        ],
        "mistakes": [
            "Usar 0,33 en lugar de E/3. No es lo mismo en todos los redondeos.",
            "Poner el psicotécnico sobre 80 puntos: el máximo oficial es 30.",
            "Tratar 5 errores de ortografía como no apto. El umbral es 6 o más.",
            "Llamar «nota de corte» al mínimo 50/8/12. Esos son mínimos de la prueba, no el corte para plaza."
        ],
        "limits": [
            "No calcula el baremo ítem a ítem del apéndice I.",
            "No evalúa físicas, entrevista ni reconocimiento médico.",
            "No inventa el número de convocados a psicofísicas ni un corte de plaza.",
            "Si hay anulaciones, debes indicar las preguntas válidas. El valor por defecto es el T de la tabla 7.3."
        ],
        "faqs": [
            ("¿Qué significa superar el mínimo?", "Que la puntuación de esa prueba alcanza el umbral de las bases 7.6, 7.7 o 7.8, o que ortografía/gramática no llegan a 6 errores. No significa que hayas superado la oposición completa ni que tengas plaza."),
            ("¿Las preguntas de reserva suman siempre?", "No. Solo sustituyen, por su orden, a las anuladas. Por eso T puede dejar de ser 100, 20 u 80."),
            ("¿Puedo estimar el corte de plaza?", "El corte de esta convocatoria lo marca el resto de aspirantes y se publica después. Lo que sí se puede es colocar tu total en la lista oficial de quienes sacaron plaza el año pasado (BOE-A-2025-21403, turno libre). Eso no es tu puesto de este año."),
        ]
    },
    "ayudantes-iipp-2026": {
        "how": [
            "El primer ejercicio tiene dos partes. Todas las preguntas valen igual. Cada error resta un tercio de un acierto. Las preguntas en blanco no restan.",
            "La primera parte tiene 120 preguntas y 3 de reserva. La segunda, 8 supuestos de 5 preguntas (40) y solo se corrige si se superó la primera. Eso se decide sobre la calificación transformada de 0 a 20, no sobre la puntuación directa.",
            "Esta calculadora muestra siempre la puntuación directa (aciertos − errores/3), que sí está cerrada en el BOE. La transformada 0–20 depende de un umbral que debe publicar el órgano de selección de esta convocatoria. Sin ese dato no se afirma el mínimo de 10 puntos ni se corrige o no la segunda parte."
        ],
        "example": [
            "80 aciertos y 12 errores en la primera parte: 80 − 12/3 = 76 de puntuación directa.",
            "28 aciertos y 6 errores en la segunda: 28 − 2 = 26 de puntuación directa.",
            "Esas cifras no son 10 ni 20. Convertirlas exige el umbral directo que fije el tribunal de 2026."
        ],
        "mistakes": [
            "Tratar 76 directos como si fueran 76 sobre 20.",
            "Usar el umbral de la convocatoria anterior como si ya valiera para junio de 2026.",
            "Decir que la segunda parte «se corrige» sin haber superado los 10 transformados de la primera."
        ],
        "limits": [
            "No calcula el reconocimiento médico.",
            "No inventa la interpolación transformada ni un corte de plaza.",
            "Si indicas un umbral, debe ser el publicado para esta Resolución, no un recuerdo de 2025."
        ],
        "faqs": [
            ("¿Por qué no me dice si llego al 10?", "Porque el 10 es de la escala transformada. El BOE de junio de 2026 no publica el umbral directo. Cuando el tribunal lo publique, puedes introducirlo."),
            ("¿Qué es T si anulan preguntas?", "El número de preguntas válidas. Por defecto 120 y 40. Si entra reserva, cámbialo.")
        ]
    },
    "auxilio-judicial-2026": {
        "how": [
            "El Anexo V.a) no usa la penalización 1/3 de la AGE. El primer ejercicio vale 0,60 por acierto y resta 0,15 por error, sobre 100 preguntas (máximo 60, mínimo 30). Hay 4 de reserva.",
            "El segundo ejercicio vale 1 punto por acierto y resta 0,25 por error, sobre 40 preguntas (máximo 40, mínimo 20). Hay 2 de reserva.",
            "La puntuación final de quien supera ambos es la suma. Superar 30 y 20 no es lo mismo que entrar en la lista limitada al número de plazas."
        ],
        "example": [
            "70 aciertos y 20 errores en el teórico: 70×0,60 − 20×0,15 = 39. Blancos: 10.",
            "28 aciertos y 8 errores en el práctico: 28 − 8×0,25 = 26.",
            "Total: 65. Ambos ejercicios superan su mínimo."
        ],
        "mistakes": [
            "Aplicar −1/3 como en la AGE.",
            "Contar las 4 de reserva como si siempre sumaran a las 100.",
            "Sumar lengua oficial o Derecho Civil Vasco a esta nota estatal: van en otro anexo y otro efecto."
        ],
        "limits": [
            "No calcula destinos autonómicos ni lengua cooficial.",
            "No afirma plaza por superar 30+20.",
            "Si hay anulaciones, indica las preguntas válidas."
        ],
        "faqs": [
            ("¿Cuántos errores puedo tener con 70 aciertos en el primero?", "0,60×70 − 0,15×E ≥ 30 → E ≤ 80. El tope real es el número de preguntas que te queden. La calculadora lo resuelve con tus aciertos."),
        ]
    },
    "auxiliar-age-2026": {
        "how": [
            "El Anexo I distingue puntuación directa y calificación transformada. La directa de cada parte es A − E/3. Los blancos no restan. Primera parte: hasta 60 preguntas y 5 de reserva. Segunda: hasta 50 y 5 de reserva.",
            "La CPS transforma cada parte a 0–50 y fija el umbral directo, que no puede ser inferior al 30 % del máximo directo. Esa interpolación solo se aplicaría con los criterios publicados para esta convocatoria.",
            "En esta versión no se implementa la transformada: el PDF de criterios de mayo de 2026 no se ha podido vincular aquí como fuente recuperable. Se muestra únicamente la puntuación directa, que sí está en el BOE."
        ],
        "example": [
            "42 aciertos y 9 errores en la primera parte: 42 − 3 = 39 de puntuación directa.",
            "34 aciertos y 6 errores en ofimática: 34 − 2 = 32 de puntuación directa.",
            "Suma directa: 71. Eso no es una calificación sobre 100 ni un 25 sobre 50."
        ],
        "mistakes": [
            "Leer 30 directos como 30 sobre 50.",
            "Usar los umbrales 30 y 26,33 de 2025 como si fueran los de 2026.",
            "Hablar de concurso 60/40 en el turno libre de Auxiliar C2."
        ],
        "limits": [
            "No muestra calificación transformada ni mínimo 25 hasta que exista fuente CPS aplicable recuperada.",
            "No afirma que una parte se haya superado en la escala 0–50.",
            "No es una nota de corte de plaza."
        ],
        "faqs": [
            ("¿Cuándo veré la transformada?", "Cuando podamos citar el documento de criterios de esta convocatoria y su interpolación, no un resumen de academia."),
            ("¿Las 5 de reserva cuentan?", "Solo si sustituyen preguntas anuladas. Entonces cambia el número de preguntas válidas.")
        ]
    },
    "policia-local-madrid-2026": {
        "how": [
            "Esta calculadora es de Policía Municipal del Ayuntamiento de Madrid. En la mayoría de España el cuerpo se llama Policía Local, pero cada ayuntamiento publica su propia convocatoria. La fórmula de Barcelona, Valencia o un pueblo no es esta.",
            "La base 5.2.a) del BOAM núm. 9829 califica el temario y el idioma, cada uno de 0 a 10. Hay que llegar a 5 en las dos partes. El error resta un tercio del valor del acierto. Las blancas no restan. Tres alternativas.",
            "Escala de cada parte: 10 × (A − E/3) / T. Temario T = 80 (3 de reserva). Idioma T = 10 (2 de reserva). El cuestionario completo son 95 preguntas en 95 minutos.",
            "La nota cultural es 90 % temario + 10 % idioma. Superar el 5 no es plaza: solo siguen quienes, habiendo llegado a 5 en ambas partes, tienen las mejores notas hasta 3,5 aspirantes por plaza. El tribunal puede bajar ese 50 % si caben menos de esa ratio."
        ],
        "example": [
            "56 aciertos y 8 errores en temario: 10 × (56 − 8/3) / 80 = 6,6667 puntos.",
            "7 aciertos y 1 error en idioma: 10 × (7 − 1/3) / 10 = 6,6667 puntos.",
            "Nota cultural: 0,90 × 6,6667 + 0,10 × 6,6667 = 6,6667. Eso no dice si entras en el 3,5 por plaza."
        ],
        "mistakes": [
            "Usar la fórmula de Policía Nacional (error = E/2). Aquí el boletín dice un tercio, no la mitad.",
            "Aplicar esta nota a otra Policía Local. Cada municipio tiene su boletín.",
            "Tratar el 5 como corte de plaza. Es el suelo de cada parte; el recorte es 3,5 aspirantes por plaza.",
            "Sumar el psicotécnico o las físicas a esta cifra. El psicotécnico es apto o no apto. Las físicas van en el anexo II, de 5 a 10.",
            "Meter el concurso (máximo 2 puntos) como si ya formara parte de esta nota cultural."
        ],
        "limits": [
            "No calcula el concurso ítem a ítem (tope 2 puntos, fase posterior).",
            "No califica inteligencia ni personalidad: el tribunal fija el umbral y el perfil.",
            "No inventa quién entra en el 3,5 por plaza ni un corte de esta convocatoria.",
            "No sirve para Policía Local de otra ciudad.",
            "Si hay anulaciones, debes indicar las preguntas válidas."
        ],
        "faqs": [
            ("¿Es lo mismo Policía Local y Policía Municipal?", "En Madrid el cuerpo se llama Policía Municipal. En casi el resto de España, Policía Local. Esta herramienta cubre solo Madrid. Otra ciudad necesita su propio boletín."),
            ("¿Con un 5 paso?", "Alcanzas el mínimo de esa parte. Seguir depende de tener 5 en las dos y de estar entre las mejores notas, hasta 3,5 aspirantes por plaza. Eso se publica después."),
            ("¿Cada error cuánto resta?", "Un tercio de acierto. No es E/2 como en Policía Nacional."),
            ("¿Y si anulan preguntas?", "T deja de ser 80 o 10. Indica las preguntas válidas. Las de reserva solo entran si sustituyen a una anulada."),
            ("¿Cuándo es el examen?", "El día no está en el BOE de la convocatoria. Aparece cuando el Ayuntamiento de Madrid lo publique. Aquí no se estima.")
        ]
    },
    "policia-nacional-2026": {
        "how": [
            "La base 6.1.1 corrige el cuestionario de conocimientos con [A − E/(n−1)] × 10/P. Hay 100 preguntas y 3 alternativas, así que n = 3 y cada error resta medio acierto. Las preguntas en blanco no restan. El resultado va de 0 a 10.",
            "Hace falta un mínimo de 3 puntos. Eso no basta para seguir: solo continúan quienes, habiendo llegado a 3, obtienen las mejores notas hasta 1,75 aspirantes por cada una de las 2.163 plazas de turno libre. Esa nota de corte la marca el resto de opositores, no esta calculadora.",
            "La calificación final de la oposición es conocimientos más la media de las físicas (base 6.11). Aquí se calcula el test. Si acreditas un idioma prioritario o de interés policial superior a A2, puedes sumar hasta 2 puntos (B1 0,50; B2 1; C1 1,50; C2 2). Eso se suma a quienes ya son aptos, no al test suelto.",
        ],
        "example": [
            "70 aciertos y 20 errores: [70 − 20/2] × 10 / 100 = 6 puntos.",
            "30 aciertos y 0 errores: 3 puntos, el mínimo oficial. No implica pasar el corte del 1,75.",
            "80 aciertos y 4 errores: [80 − 2] × 10 / 100 = 7,8 puntos. Con un B2 (1 punto) el total orientativo sería 8,8 si superas la fase."
        ],
        "mistakes": [
            "Aplicar −1/3 como en Guardia Civil. Aquí hay 3 opciones: se resta E/2.",
            "Tratar el 3 como nota de corte de plaza. Es el suelo legal, no el corte real.",
            "Sumar el psicotécnico a esta nota. Se califica apto/no apto y el tribunal fija su mínimo después.",
            "Meter físicas como si fueran aciertos de test. Van en el anexo II, de 0 a 10 por ejercicio.",
            "Meter una carrera o un grado superior como si subieran la nota. En Escala Básica el título exigido es Bachiller; esos estudios no puntúan.",
        ],
        "limits": [
            "No convierte marcas de circuito, dominadas o carrera en puntos del anexo II.",
            "No califica el psicotécnico: P y el mínimo los fija el tribunal.",
            "No convierte una carrera, un máster o un grado superior en puntos: no están en el baremo de esta Escala Básica.",
            "No evalúa entrevista, reconocimiento médico ni méritos de Fuerzas Armadas o deportista de alto nivel ítem a ítem.",
            "No inventa cuántos aspirantes caben en el 1,75 por plaza."
        ],
        "faqs": [
            ("¿Con un 3 paso?", "Alcanzas el mínimo de la prueba. Seguir depende de estar entre las mejores notas, hasta 1,75 por plaza de turno libre. Eso se publica después."),
            ("¿Cada error cuánto resta?", "Medio acierto. n = 3, así que E/(n−1) = E/2."),
            ("¿Y si anulan preguntas?", "P deja de ser 100. Indica las preguntas válidas."),
            ("¿Suma una carrera o un grado superior?", "No en Escala Básica. El título para presentarte es Bachiller o equivalente. Tener más estudios no añade puntos al test. Lo que sí suma, si ya eres apto, son idiomas por encima del A2 (hasta 2 puntos), servicios en las Fuerzas Armadas y deportista de alto nivel (bases 6.12 a 6.14)."),
            ("¿Qué puesto habría tenido el año pasado?", "No se publica la lista de todos los que se examinaron, así que no hay un número de orden real. Sí se compara tu nota de conocimientos con el corte aproximado que el Portal del Aspirante dio el 3 de noviembre de 2025 (7,17). Eso no es el corte de este año."),
        ]
    }
}

UPCOMING = [
    {
        "name": "Calculadoras de más Policías Locales",
        "reason": "Solo se publica ficha si hay boletín. Madrid está; el resto espera bases oficiales, no se clona la fórmula."
    },
    {
        "name": "TAI — Técnicos Auxiliares de Informática AGE",
        "reason": "Pendiente de cerrar por completo los criterios oficiales aplicables a la convocatoria en curso."
    },
    {
        "name": "TCAE SAS",
        "reason": "Pendiente de un proceso o convocatoria que permita vincular la herramienta al procedimiento vigente."
    }
]
