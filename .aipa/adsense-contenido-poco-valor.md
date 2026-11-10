# AdSense: contenido de poco valor

Rechazo repetido (8 veces). Próxima revisión posible: 16 de noviembre de 2026.

## Diagnóstico (10 de noviembre de 2026)

Auditoría con `python scripts/audit_content.py` sobre las 66 URLs del sitemap:

- ~20 páginas con menos de 200 palabras: requisitos, notas de corte, exámenes y fechas de cada cuerpo. Seis veces la misma plantilla.
- Páginas puente de Madrid (CCAA y provincia) con 59 y 78 palabras, solo navegación.
- Párrafo repetido en las seis páginas de fechas («Las IAs y muchas academias…»).
- Calendarios caducados: Policía Nacional decía «examen aún no celebrado» (fue el 26-9), Guardia Civil «psicofísicas en curso» (cerró el 6-10), Auxilio Judicial «examen por anunciar» (fue el 3-10), IIPP sin el corte del 6-11, AGE sin aprobados del 15-10, Madrid «examen por anunciar» (fue el 21-6).
- `ads.txt` sin Publisher ID: AdSense lo marca «No se encuentra».

## Cambios

1. Requisitos, fechas, notas y exámenes se fusionan en la página de cada oposición (`/oposiciones/<cuerpo>/`). Las URLs viejas hacen 301 a la sección.
2. Se quita el árbol territorial de Policía Local (también Madrid CCAA/provincia/ficha). Policía Local usa la misma página de oposición que el resto. El árbol INE viejo responde 410.
3. Calendarios, cortes y estado de los seis procesos actualizados con fuentes oficiales.
4. `ads.txt` con `pub-3737489302199390` y `<meta name="google-adsense-account">` en todas las páginas.
5. `robots.txt` deja de bloquear Policía Local, para que Google vea los 410 y suelte las URLs.
6. «Mi progreso» pasa a `noindex` y sale del sitemap (es una herramienta local, no contenido).
7. `verify_seo.py` falla si una página indexable del sitemap baja de 250 palabras.

## Qué no arregla el código

- Tráfico real. AdSense pide «interés genuino de los usuarios».
- Mantenimiento: cada vez que un tribunal publique algo, hay que actualizar `scripts/hubs_data.py` y regenerar.

## Después de publicar

1. Search Console: reenviar `sitemap.xml` e inspeccionar la home y dos páginas de oposición.
2. Esperar al 16 de noviembre. Pedir revisión una sola vez.
