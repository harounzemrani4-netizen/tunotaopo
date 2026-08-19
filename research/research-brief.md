# Research Brief — NotaOpo

- **Fecha de cierre del brief:** 2026-08-19
- **Hard gate:** APROBADO. BUILD autorizado.
- **Volumen, CPC, RPM, dificultad SEO numérica e ingresos:** desconocidos. No se estiman.
- **Marca de trabajo:** NotaOpo. Dominio previsto (no registrado aquí): `notaopo.es`.

Leyenda:

- **Hecho:** comprobado en fuente oficial o en una SERP visitada el 2026-08-19.
- **Inferencia:** juicio cualitativo. No es un dato de herramienta de keywords.

---

## Fuente de verdad — alcance

### MVP V1 (únicas calculadoras de esta versión)

1. Guardia Civil 2026
2. Ayudantes de Instituciones Penitenciarias 2026
3. Auxilio Judicial 2025/2026
4. Auxiliar Administrativo AGE 2025/2026

Orden de construcción: **Guardia Civil → IIPP → Auxilio Judicial → Auxiliar AGE**.

No hay quinta calculadora en el MVP.

### Tanda 2 (fuera del MVP; sin URL de producción)

- **TAI AGE:** pendiente de cerrar completamente los criterios oficiales aplicables (PDF CPS 19-05-2026).
- **TCAE SAS:** pendiente de un proceso/convocatoria que permita vincular la herramienta al proceso vigente.

---

## 1. User and painful job

**Quién (inferencia + hecho de mercado):** opositoras y opositores en España, sobre todo C2/C1, Justicia y Fuerzas/Cuerpos de Seguridad, que acaban un simulacro o el examen real.

**Trabajo doloroso:** convertir aciertos, errores y blancos en la puntuación que usa el tribunal. El error recurrente es mezclar:

- puntuación directa y calificación transformada;
- mínimo para no ser eliminado y nota de corte de plaza;
- penalización 1/3 (AGE / IIPP / GC) y 1/4 o valores fijos (Justicia);
- una media “sobre 10” que la convocatoria no usa.

**Decisión que mejora:** ¿supero el mínimo de esta prueba? ¿cuántos errores puedo permitirme? ¿dejo en blanco o arriesgo?

---

## 2. Primary intent

> calcular la nota de **esta** convocatoria con **esta** fórmula oficial.

No: “calculadora genérica de test de oposiciones”.

---

## 3. Current SERP / market

Competidores transversales vistos el 2026-08-19:

| Competidor | Qué ofrece | Debilidad |
|---|---|---|
| Opositar y + | Selector de muchos cuerpos | Una URL; no versiona fuente por página |
| OpoRuta | Calculadoras por cuerpo | Mejor nicho; errores de escala AGE reconocidos; marca comercial |
| OpositaTest | Calculadora test genérica | No atada a una convocatoria |
| iOpos | Fallos que anulan un acierto | UX pobre; no cita BOE |
| PreparaOposiciones | Blog + selector | Aplica 1/3 a cuerpos que no lo usan |
| Testea / OpoCalculadora | Transformada AGE por cuerpo | Fuerte en AGE; no cubre GC/Justicia/IIPP con la misma profundidad |

**Hecho:** el nicho no está vacío.  
**Inferencia:** hay espacio para un portal independiente, versionado y por URL.

---

## 4. Differentiation

Cada página calcula **solo** lo que la convocatoria permite, cita el **apartado oficial**, distingue **directa / transformada / mínimo / corte**, y no vende un curso en el primer pantallazo.

---

## 5. Cambios de shortlist (histórico de investigación)

- Se excluyó **Policía Nacional Escala Básica 2026** del MVP: SERP saturada de calculadoras específicas y, en varios casos, correctas.
- En su lugar entra **Ayudantes IIPP 2026**.
- No se fuerza una quinta. TAI y TCAE quedan en tanda 2.

---

## 6. Legal / platform

- Cálculo **orientativo e independiente**. Sin afiliación ni respaldo del organismo.
- Ante discrepancia, prevalece la convocatoria y los criterios del tribunal.
- No se certifica plaza ni se afirma “has superado la oposición” si la fórmula no lo permite.
- Sin AdSense, tracking ni afiliados reales en V1.
- Placeholders legales: `[TITULAR]`, `[NIF]`, `[DOMICILIO]`, `[EMAIL]`.

---

## 7. Monetización (sin cifras, no activada)

1. AdSense (preparado, inactivo)
2. Afiliación academias/material (slots, sin enlaces falsos)
3. Email (captura inactiva)
4. Premium futuro (sin pagos en V1)

---

## 8. MVP boundary

**Dentro:** 4 calculadoras, motor configurable, URLs propias, tests matemáticos, SEO por página, legal base, ads/afiliados/email **preparados e inactivos**.

**Fuera:** quinta calculadora, TAI, TCAE, publicar, AdSense real, pagos, backend, doorway pages, baremo ítem a ítem de méritos GC.

---

## 9. Kill / scale signals

Impresiones por URL, `calculator_completed`, repetición, clics a fuente oficial. Si una URL no se usa en 2–3 meses tras indexar, no escalar esa familia.

---

## 10. Criterio de puntuación 0–10

Juicio interno (demanda aparente, fórmula cerrada, hueco de tool, diferenciación, monetización causal). **No incluye volumen ni CPC.**

---

# TABLA COMPARATIVA DEL MVP (4)

## 1 — Guardia Civil, Cabos y Guardias 2026

| # | Campo | Contenido | Tipo |
|---|---|---|---|
| 1 | Nombre exacto | Pruebas selectivas para ingreso en los centros docentes de formación para la incorporación a la **Escala de Cabos y Guardias del Cuerpo de la Guardia Civil** | Hecho |
| 2 | Administración | Dirección General de la Guardia Civil, Ministerio del Interior | Hecho |
| 3 | Convocatoria y año | Resolución 160/38243/2026, de 5 de mayo (BOE 8 de mayo de 2026). 3.240 plazas | Hecho |
| 4 | Fuente oficial | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-9982 | Hecho |
| 5 | Apartado | **6.1.1–6.1.2** (estructura); **7.3** (fórmula y tabla Y/T/N); **7.4–7.5** (orto/gramática); **7.6–7.8** (mínimos); **7.1 y 7.9** (concurso 0–45 y suma) | Hecho |
| 6 | Fórmula | \(P_x = Y \cdot (A - E/(N-1)) / T\), \(N=4\). \(P_{cg}: Y=100,T=100\); \(P_{li}: Y=20,T=20\); \(P_{ps}: Y=30,T=80\). Blancos no restan. Orto/gramática: no apto si \(E \ge 6\). Mínimos: \(P_{cg}\ge 50\), \(P_{li}\ge 8\), \(P_{ps}\ge 12\). Oposición = suma (máx. 150). Proceso = oposición + concurso (máx. 45) | Hecho |
| 7 | Inputs | Errores ortografía (20 ítems + 4 reserva); errores gramática (20 + 4 reserva); A/E conocimientos (100 + 5 reserva); A/E inglés (20 + 1 reserva); A/E psicotécnico (80); concurso opcional 0–45; preguntas válidas si hay anulaciones | Hecho |
| 8 | Outputs | Puntuación por prueba; blancos; penalización \(E/3\); apto/no apto; suma oposición; total con concurso; si se superan **mínimos oficiales**; escenarios inversos solo si son resolubles | Diseño sobre hechos |
| 9 | Edge cases | Cero; máximo; bruto negativo → 0; 5 vs 6 errores; T variable por anulación | Hecho |
| 10 | Sistema | **Concurso-oposición** | Hecho |
| 11–13 | Competidores | ATLAS, Gesinpol, Campus Training, OpoRuta, Red Opositor, Patrio. Suelen usar 0,33, pesos inventados o “corte” sin fuente | Hecho + inferencia |
| 14–16 | SEO | Long-tail de fórmula, mínimos y 6 errores. Tools de academia mejorables | Inferencia |
| 17 | Monetización | Ads, academias GC, email de plantilla | Inferencia |
| 18–20 | Riesgo / update / complejidad | Medio / anual / media-alta (`multi_stage`) | Inferencia |
| 21–22 | Legal / diferenciación | No afirmar corte de plaza. Desglose completo oficial, no solo E/3 | Hecho / diseño |
| 23 | Score | **8,5 / 10** | Inferencia |

## 2 — Ayudantes de Instituciones Penitenciarias 2026

| # | Campo | Contenido | Tipo |
|---|---|---|---|
| 1 | Nombre exacto | Ingreso, acceso libre, **Cuerpo de Ayudantes de Instituciones Penitenciarias** | Hecho |
| 2 | Administración | Ministerio del Interior — Secretaría General de IIPP | Hecho |
| 3 | Convocatoria | Resolución 14-06-2026, BOE 18-06-2026 (BOE-A-2026-13226). 1.050 plazas | Hecho |
| 4–5 | Fuente / apartado | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-13226 — primer ejercicio, dos partes | Hecho |
| 6 | Fórmula | **PD cerrada:** \(PD = A - E/3\). Parte 1: 120 preg. Parte 2: 40 preg. **Transformada 0–20:** abierta en BOE; V1 solo si el usuario aporta umbral de **esta** convocatoria | Hecho + límite |
| 7–10 | Inputs / sistema | A/E por parte; umbral opcional. **Oposición** + médico (no se calcula) | Hecho |
| 11–16 | SERP | Pocas calculadoras dedicadas; OpoRuta y academias de prisiones | Hecho / inferencia |
| 23 | Score | **8,0 / 10** | Inferencia |

## 3 — Auxilio Judicial, turno libre 2025/2026

| # | Campo | Contenido | Tipo |
|---|---|---|---|
| 1 | Nombre exacto | Ingreso, acceso libre, **Cuerpo de Auxilio Judicial** | Hecho |
| 2 | Administración | Ministerio de la Presidencia, Justicia y Relaciones con las Cortes | Hecho |
| 3 | Convocatoria | Orden PJC/1549/2025, de 22 de diciembre (BOE 30-12-2025). 425 plazas | Hecho |
| 4–5 | Fuente / apartado | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-27053 — **Anexo V.a)** 1.1–1.3 | Hecho |
| 6 | Fórmula | Ej. 1: \(0{,}60A - 0{,}15E\), máx. 60, mín. 30. Ej. 2: \(1{,}00A - 0{,}25E\), máx. 40, mín. 20. Blancos = 0 | Hecho |
| 7–10 | Inputs / sistema | A/E por ejercicio. **Oposición** | Hecho |
| 11–13 | Competidores | **OpoRuta** es el rival específico fuerte; ADJ, OpositaTest | Hecho |
| 22 | Diferenciación | URL solo Auxilio; escenarios y UX, no solo la fórmula | Diseño |
| 23 | Score | **7,5 / 10** | Inferencia |

## 4 — Auxiliar Administrativo del Estado (C2), ingreso libre 2025/2026

| # | Campo | Contenido | Tipo |
|---|---|---|---|
| 1 | Nombre exacto | Ingreso libre en el **Cuerpo General Auxiliar de la Administración del Estado** | Hecho |
| 2 | Administración | SEFP / INAP — Comisión Permanente de Selección | Hecho |
| 3 | Convocatoria | Resolución 18-12-2025 (BOE 22-12-2025). 1.700 plazas libres | Hecho |
| 4–5 | Fuente / apartado | https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-26262 — **Anexo I** 2.1–2.3 | Hecho |
| 6 | Fórmula | \(PD = A - E/3\) por parte (máx. 60 y 50). Transformada 0–50: **solo** si se vincula a criterios CPS aplicables a **esta** convocatoria (p. ej. 20-05-2026). Sin ese vínculo, V1 muestra únicamente PD | Hecho + hard gate |
| 7–10 | Inputs / sistema | A/E parte 1 (60) y parte 2 (50). **Oposición** | Hecho |
| 11–13 | Competidores | Testea (fuerte), OpoRuta, Opositan | Hecho |
| 23 | Score | **8,5 / 10** | Inferencia |

---

# DESCARTADAS / FUERA DEL MVP

| Oportunidad | Por qué | Estado |
|---|---|---|
| Policía Nacional Escala Básica 2026 | SERP saturada de tools específicas correctas | Fuera del MVP |
| Correos 2026 | Sin convocatoria/fórmula verificada | Fuera |
| Administrativo C1 AGE | Misma familia que Auxiliar | Tanda posterior |
| Tramitación / Gestión Procesal | Thin content si se clona Auxilio | Tanda posterior |
| Baremo ítem a ítem GC | Otro producto | Tanda 2 |
| Educación / Policía Local | Fórmulas no cerradas o doorway | Fuera ahora |
| Calculadora genérica | Choca con el briefing | Fuera |
| **TAI AGE** | Criterios CPS 2026 no cerrados del todo; no fuerza quinta | **Tanda 2** |
| **TCAE SAS** | Fuente específica febrero 2025; no etiquetar proceso vigente | **Tanda 2** |

---

# RECOMENDACIÓN FINAL

Si solo se pudiera publicar una: **Guardia Civil 2026**.

---

# ARQUITECTURA APROBADA

**Modo:** STATIC. Cálculo en navegador. Sin backend.

**Principio:** motor declarativo + JSON por convocatoria + HTML generado. Sin `if (opposition === ...)`.

**Modelos:** `net_score`, `scaled_score`, `fixed_value`, `pass_fail`, `pass_fail_errors`, `transform`, `multi_stage`, `aggregate`.

Una convocatoria combina modelos. Campos de stage solo cuando hacen falta: `id`, `label`, `questions`, `valid_questions`, `reserve_questions`, `correct_value`, `incorrect_penalty`, `blank_value`, `maximum`, `minimum`, `rounding`, `eliminatory`, `source_reference`.

La oposición puede definir `stages`, `aggregate`, `merits`, máximo global y `requirements`.

**URLs del MVP:**

- `/calculadoras/guardia-civil/calculadora-nota-2026/`
- `/calculadoras/ayudantes-iipp/calculadora-nota-2026/`
- `/calculadoras/auxilio-judicial/calculadora-nota-2026/`
- `/calculadoras/auxiliar-administrativo-age/calculadora-nota-2026/`

**SEO:** herramienta above the fold; explicación en HTML; sin `FAQPage` automático.

**Monetización:** slots y eventos preparados (`calculator_started`, `calculator_completed`, `result_shared`, `official_source_clicked`). Sin IDs reales.
