# AdSense: contenido de poco valor

Google no rechaza un botón: rastrea el sitio y ve miles de fichas INE casi iguales (sin boletín, sin calculadora) y huecos de «Publicidad». Eso es contenido de poco valor / doorway.

## Qué cambia en el código

- Fichas de municipio sin boletín: `noindex` y **sin** huecos de anuncio.
- CCAA y provincias: `noindex`, fuera del sitemap.
- `robots.txt` cierra el árbol INE a Google y a AdsBot / Mediapartners-Google. Deja pasar el hub, Madrid y las páginas de la convocatoria.
- Aviso legal, privacidad, cookies y contacto: sin anuncios.

## Qué no hace el código

- No marca «Confirmo que he resuelto los problemas» en AdSense.
- No activa AdSense ni inventa un Publisher ID.

## Después de publicar

1. Subir este estático al hosting (GitHub no cambia AdSense si el dominio no se regenera).
2. Esperar a que Google recorra de nuevo. No pedir revisión el mismo día.
3. En AdSense, pedir revisión solo cuando en Search Console / AdSense ya no se vean miles de URLs de pueblos sin bases.
