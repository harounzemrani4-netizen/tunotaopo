# FINAL RELEASE CHECK — NotaOpo — 2026-08-19

Check local, sin desplegar, sin AdSense y sin tanda 2. Sin cambios de fórmulas, JSON, sources, canonical, URLs ni motor: no hubo bug real que lo exigiera.

## Identificación

| Campo | Valor |
|---|---|
| Fecha | 2026-08-19 |
| Versión | `notaopo-engine-2.0` / `mvp-4` / `2026-08-19` |
| Commit | **no existe** (el proyecto no es un repositorio git) |
| Entorno | `python -m http.server 8765` sobre `notaopo/` |
| Lighthouse | CLI 12.8.2 (HeadlessChrome 151) |
| Artefactos LH | `release/lh-home-desktop.json`, `lh-home-mobile.json`, `lh-gc-desktop.json`, `lh-gc-mobile.json` |

---

## Checks automáticos

| Check | Resultado |
|---|---|
| Tests motor | **35/35**, 0 fallos (`tests/test_engine.py` + `tests/fixtures.json`) |
| Manifest | **PASS**, 0 avisos (`validate_project_manifest.py` → `project-manifest.json`) |
| `verify_project` | **PASS**, 0 errores, 0 avisos |
| Encoding | **PASS**, 0 errores, 0 avisos (`audit_encoding.py`; UTF-8 strict en disco) |

Referencias de fixtures: GC mix **97,5**; IIPP PD **102**; Auxilio **65**; AGE PD **71**.

---

## Lighthouse

Medido en localhost. No se persiguió 100/100. No se corrigió nada: no había fallos claros y razonables.

Insight `network-dependency-tree-insight` puntúa 0 en las cuatro corridas; no entra en las categorías y no justifica un rediseño. En GC móvil, Speed Index 2,0 s (score 0,99) no baja la categoría.

| Página | Device | Performance | Accessibility | Best Practices | SEO | FCP | LCP | TBT | CLS |
|---|---|---:|---:|---:|---:|---|---|---|---|
| Home `/` | desktop | 100 | 100 | 100 | 100 | 0,2 s | 0,3 s | 0 ms | 0 |
| Home `/` | mobile | 100 | 100 | 100 | 100 | 0,8 s | 0,9 s | 0 ms | 0 |
| Guardia Civil | desktop | 100 | 100 | 100 | 100 | 0,3 s | 0,4 s | 0 ms | 0 |
| Guardia Civil | mobile | 100 | 100 | 100 | 100 | 1,0 s | 1,5 s | 0 ms | 0 |

---

## QA manual — Guardia Civil

UI contra los mismos casos que `tests/fixtures.json`. Viewport móvil 390×844. Canonical siempre `https://notaopo.es/calculadoras/guardia-civil/calculadora-nota-2026/` (sin query).

| Caso | Entrada | Resultado UI | Estado |
|---|---|---|---|
| Válido (mix) | 70/15 + 14/3 + 55/9 + orto 2 + gram 1 | oposición **97,5** / 150; 65, 13, 19,5; aptos | PASS |
| Justo en mínimo | 50 / 8 / 32 | **70**; todos superan mínimo | PASS |
| Justo debajo | cg = 49 | **69**; Conocimientos ✗ no alcanza mínimo | PASS |
| 6 errores ortografía | orto = 6 | Ortografía **No apto** / ✗ no apto | PASS |
| Méritos 0 | mix + merits 0 | oposición 97,5 · total **97,5** | PASS |
| Méritos máximo | mix + merits 45 | oposición 97,5 · total **142,5** | PASS |
| Inputs imposibles | 80 + 40 en conocimientos | error: no pueden superar 100 válidas; resultado oculto | PASS |
| Compartir URL | mix + merits 0 | query compacta; al recargar recalcula **97,5**; canonical limpio | PASS |
| Reset | — | resultado y error ocultos; inputs vacíos; `search=""` | PASS |

Share recargado:

`?orto_errors=2&gram_errors=1&cg_hits=70&cg_errors=15&en_hits=14&en_errors=3&ps_hits=55&ps_errors=9&merits=0`

Sin overflow horizontal, sin imágenes rotas, fuente `BOE-A-2026-9982`.

---

## Spot-check visual compartido

Una pasada por IIPP, Auxilio y AGE para confirmar que el polish no rompe formularios específicos.

| Calculadora | Mix | Overflow | Visual / específico | Estado |
|---|---|---|---|---|
| IIPP | PD **102** / 160; transformada vacía = sin umbral | 100+30 → error 120 válidas | fieldsets PD + transformada; `p1t_cut=36` / `p2t_cut=12` → 14,7619 y 15 / 20 | PASS |
| Auxilio | **65** / 100 (39 + 26) | 80+25 → error 100 válidas | teórico + práctico; `BOE-A-2025-27053` | PASS |
| AGE | PD **71** / 110 (39 + 32) | 50+20 → error 60 válidas | solo PD; lede sin umbral CPS inventado; `BOE-A-2025-26262` | PASS |

TAI y TCAE siguen solo como texto «próximas» en home: sin URL, sin sitemap, sin canonical.

---

## URLs del MVP

Canónicas previstas (`notaopo.es`, dominio no registrado en este repo):

| Pieza | URL |
|---|---|
| Home | `https://notaopo.es/` |
| Índice calculadoras | `https://notaopo.es/calculadoras/` |
| Guardia Civil 2026 | `https://notaopo.es/calculadoras/guardia-civil/calculadora-nota-2026/` |
| Ayudantes IIPP 2026 | `https://notaopo.es/calculadoras/ayudantes-iipp/calculadora-nota-2026/` |
| Auxilio Judicial 2026 | `https://notaopo.es/calculadoras/auxilio-judicial/calculadora-nota-2026/` |
| Auxiliar AGE 2026 | `https://notaopo.es/calculadoras/auxiliar-administrativo-age/calculadora-nota-2026/` |
| Metodología | `https://notaopo.es/metodologia/` |
| Fuentes | `https://notaopo.es/fuentes/` |
| Aviso legal | `https://notaopo.es/aviso-legal/` |
| Privacidad | `https://notaopo.es/privacidad/` |
| Cookies | `https://notaopo.es/cookies/` |
| Contacto | `https://notaopo.es/contacto/` |

Sitemap alineado. Fuera de sitemap: TAI AGE, TCAE SAS.

---

## Source identifiers y formula versions

| Pieza | `formula_version` | Source identifier | Apartado |
|---|---|---|---|
| Motor | `notaopo-engine-2.0` | `js/engine/scoring.js` | — |
| Guardia Civil | `2026.1` | `BOE-A-2026-9982` | 6.1.1–6.1.2 y 7.3–7.9 |
| IIPP | `2026.1` | `BOE-A-2026-13226` | Primer ejercicio, 1.ª y 2.ª parte |
| Auxilio | `2025.1` | `BOE-A-2025-27053` | Anexo V.a) 1.1–1.3 |
| AGE | `2025.1-pd` | `BOE-A-2025-26262` | Anexo I 2.1–2.3 |

---

## Correcciones aplicadas en este check

Ninguna. No había fallos técnicos claros. No se tocó motor, JSON, sources, canonical ni URLs.

---

## Blockers pendientes

Estos **no** son fallos técnicos:

1. Datos legales del titular: `[TITULAR]`, `[NIF]`, `[DOMICILIO]`, `[EMAIL]` en aviso legal, privacidad y contacto.
2. Dominio `notaopo.es` previsto, no registrado en este repositorio.
3. AdSense, afiliados y email preparados e inactivos a propósito. Sin Publisher ID ni CMP.

---

## Estado final

```
READY_FOR_TECHNICAL_DEPLOYMENT: YES
READY_FOR_PUBLIC_PRODUCTION: NO
```

La falta de datos reales del titular bloquea producción pública. No se clasifica como fallo técnico.

No desplegado. AdSense no activado. Tanda 2 no iniciada.
