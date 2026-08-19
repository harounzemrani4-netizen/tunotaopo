# Checklist para añadir una oposición

No publiques una oposición nueva si falta un dato crítico. No clones una página cambiando solo el nombre.

Correo único: `CONTACT_EMAIL` en `scripts/generate_pages.py` (hoy `contacto@tunotaopo.es`).

## Antes de tocar código

- [ ] Fuente oficial localizada (BOE o boletín del organismo)
- [ ] Convocatoria identificada (identificador BOE, fecha de publicación)
- [ ] Año/proceso
- [ ] Organismo convocante
- [ ] `call_status`: `active` (la calculadora principal) o `historic` (archivo)
- [ ] No inventar plazas, fechas, cortes, fórmulas ni temarios

## Datos (`data/oposiciones/{slug}.json`)

- [ ] `slug`, `family`, `family_path`, `path`, `is_current`, `call_status`
- [ ] `aliases` (pn, gc, age, iipp, auxilio…)
- [ ] Requisitos (en `scripts/hubs_data.py`, con cita de base)
- [ ] Pruebas reales, en orden, con etiquetas (eliminatoria / puntuable / apto-no apto / baremo)
- [ ] Temario: índice oficial, no el tema desarrollado
- [ ] Fechas: solo BOE o portal oficial; si no hay fecha: `Pendiente de publicación oficial`
- [ ] Fórmula en `stages` + `formula_human` + `formula_version`
- [ ] Baremo solo si el boletín lo define ítem a ítem
- [ ] Físicas solo con tabla oficial
- [ ] `fuente_oficial` (url, identifier, apartado, `reviewed_at`)
- [ ] Changelog (`updates` en el hub): solo cambios de la oposición, con fuente

## Producto

- [ ] Calculadora de nota con el motor `js/engine/scoring.js` (no duplicar fórmulas)
- [ ] Calculadora extra (físicas/baremo) solo si hay norma
- [ ] Tests independientes en `tests/fixtures.json` o `tests/test_*.py`
- [ ] Title, meta description y H1 únicos
- [ ] Canonical de la calculadora en vigor en `family_path` (no crear otra URL de nota)
- [ ] Interlinking al hub, fuentes y calculadoras hermanas
- [ ] Sitemap (el generador lo añade si `status=published`)
- [ ] Embed `/embed/{family}/` con `noindex,nofollow` y el mismo motor
- [ ] Revisión final: móvil 360–430 px, contraste APTO/NO APTO no solo por color

## Al llegar una convocatoria nueva

1. No borres el JSON anterior.
2. Marca el viejo `call_status: historic`, `is_current: false`.
3. El nuevo queda `active` y ocupa `family_path`.
4. La URL `calculadoras/{familia}/calculadora-nota-{año}/` queda como archivo con aviso de año.
5. Actualiza tests y `last_verified`.
