# Pre-deploy — 2026-08-19

Tests ejecutados en local. **No se ha desplegado.**

## Resultados

| Check | Resultado |
|---|---|
| Motor | 35/35 |
| Seguridad estática | PASS (12 páginas, 42 huecos reservados, CSP en todas) |
| Encoding | PASS |
| Manifest | ver ejecución posterior |
| verify_project | ver ejecución posterior |

## Seguridad aplicada

- CSP (`default-src 'self'`) en meta y `.htaccess`
- `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Permissions-Policy`, `COOP`
- Sin listado de directorios
- `research/`, `tests/`, `scripts/`, `release/`, `data/` bloqueados en Apache
- Sin AdSense, GTM ni analítica de terceros
- `ads.txt` sin Publisher ID inventado
- Share URL sigue validado; desglose escapa HTML
- Sin handlers `onclick` inline

Cuando haya SSL: descomentar redirect HTTPS y HSTS en `.htaccess`.

## Anuncios

Huecos **visibles y reservados**. AdSense **no está activo**.

Calculadora: top, after-hero, after-result, in-content, after-related, bottom.  
Home: top, home-mid, bottom.  
Resto: top + bottom.

Para activar falta: Publisher ID real, `ads.txt`, CMP (EEE) y ampliar CSP a los dominios de Google.

## Producción pública

```
READY_FOR_TECHNICAL_DEPLOYMENT: YES
READY_FOR_PUBLIC_PRODUCTION: NO
```

Siguen pendientes `[TITULAR]`, `[NIF]`, `[DOMICILIO]`, `[EMAIL]` y el dominio.
