# AdSense: contenido de poco valor

Google no rechaza un botón. Un revisor entra en Policía Local y, si existen miles de fichas INE casi iguales (sin boletín, sin calculadora), eso es contenido de poco valor / doorway. El `noindex` no basta: las páginas siguen en el hosting y se enlazan.

## Qué cambia ahora

- **No se publica** ficha, CCAA ni provincia sin boletín. Esas URLs pasan a 404.
- El hub de Policía Local lista solo ciudades con calculadora (hoy Madrid).
- El buscador solo sugiere ciudades publicadas.
- `robots.txt` sigue cerrando el árbol INE viejo por si Google aún lo tiene en caché.

## Qué no hace el código

- No marca «Confirmo que he resuelto los problemas» en AdSense.
- No activa AdSense ni inventa un Publisher ID.
- No inventa tráfico. AdSense también pide interés real de usuarios.

## Después de publicar

1. Subir el estático (GitHub → Cloudflare Pages).
2. Esperar **al menos 7–14 días**. Las ~8.000 URLs viejas tienen que caer del índice.
3. Pedir revisión solo cuando Search Console ya no liste miles de pueblos y Abla/Valencia den 404.
