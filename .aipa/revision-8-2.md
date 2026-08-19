# Revisión 8,2 → 9: títulos, Guardia Civil y recurrencia

Fecha: 19 de agosto de 2026.

## Hecho en código

1. Títulos HTML específicos (`Requisitos Policía Nacional 2026 | TuNotaOpo`, equivalentes por cuerpo y sección). Índice de calculadoras: `Calculadoras de nota oposiciones | TuNotaOpo` (sin NotaOpo).
2. Calculadora de físicas Guardia Civil 2026: apéndice II, apto/no apto por sexo y tramo de edad. URL nueva `/oposiciones/guardia-civil/pruebas-fisicas/`. No cambia `/calculadoras/guardia-civil/`.
3. Calculadora de baremo Guardia Civil 2026 ítem a ítem: apéndice I, topes 13,5 / 27 / 4,5 / 45. URL `/oposiciones/guardia-civil/baremo/`.
4. Páginas de pruebas, fechas, notas y exámenes con texto útil, diagrama de proceso y timeline visual. Hubs AGE, Auxilio e IIPP al mismo molde de contenido (sin clonar físicas/baremo que el BOE no define).
5. Mi progreso: `localStorage` en calculadoras y página `/progreso/` que agrupa nota y físicas de este navegador.
6. Etiqueta «Proceso 2026 · convocatoria publicada el …».
7. Correo público `contacto@tunotaopo.es`.

## Search Console y correo (manual; no se inventa meta de verificación)

No hay token de Google Search Console en el repo. Hay que hacerlo en la cuenta del dominio:

1. Verificar `https://tunotaopo.es` (DNS o archivo HTML; no commitear un token inventado).
2. Enviar `https://tunotaopo.es/sitemap.xml`.
3. Pedir indexación de, como mínimo:
   - `/`
   - `/oposiciones/policia-nacional/`
   - `/calculadoras/policia-nacional/`
   - `/oposiciones/policia-nacional/pruebas-fisicas/`
   - `/oposiciones/guardia-civil/`
   - `/calculadoras/guardia-civil/`
   - `/oposiciones/guardia-civil/pruebas-fisicas/`
   - `/oposiciones/guardia-civil/baremo/`
   - `/progreso/`
4. Crear el buzón o alias `contacto@tunotaopo.es` en el proveedor del dominio (IONOS).

## No hacer todavía

Más oposiciones. Solo después de asentar estas cinco.
