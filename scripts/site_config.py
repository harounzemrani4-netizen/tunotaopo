"""Constantes del sitio estático. Una sola fuente para marca, CSP y versión de assets."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tunotaopo.es"
BRAND = "TuNotaOpo"
BRAND_ALT = "NotaOpo"
ASSET_V = "20261110aa"
LASTMOD = "2026-11-10"
REVIEWED_ON = "10 de noviembre de 2026"
CONTACT_EMAIL = "contacto@tunotaopo.es"
ADSENSE_PUBLISHER = "pub-3737489302199390"
ADSENSE_CLIENT = f"ca-{ADSENSE_PUBLISHER}"
PROGRESO_PATH = "oposiciones/progreso/"
ACADEMIAS_PATH = "oposiciones/academias/"
DATA_DIR = ROOT / "data" / "oposiciones"
MONTHS_ES = (
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)

FEATURED_FAMILIES = [
    "guardia-civil",
    "policia-nacional",
    "policia-local",
    "ayudantes-iipp",
    "auxilio-judicial",
    "auxiliar-age",
]

PUBLISHER = {
    "name": "Haroun Zemrani El Hadri",
    "email": CONTACT_EMAIL,
    "address": "28981, Parla (Madrid)",
}

CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "frame-ancestors 'none'; "
    "object-src 'none'"
)
CSP_EMBED = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self'; "
    "img-src 'self' data:; "
    "font-src 'self'; "
    "connect-src 'self'; "
    "form-action 'self'; "
    "base-uri 'self'; "
    "frame-ancestors *; "
    "object-src 'none'"
)


def csp_for_meta(policy: str) -> str:
    """El navegador ignora frame-ancestors en <meta> y lo escribe en consola."""
    parts = [part.strip() for part in policy.split(";") if part.strip()]
    return "; ".join(part for part in parts if not part.lower().startswith("frame-ancestors"))


CSP_META = csp_for_meta(CSP)
CSP_EMBED_META = csp_for_meta(CSP_EMBED)

AD_SIZES = {
    "top": "leaderboard",
    "after-hero": "leaderboard",
    "after-result": "rectangle",
    "in-content": "rectangle",
    "after-related": "leaderboard",
    "home-mid": "rectangle",
    "catalog": "leaderboard",
    "bottom": "leaderboard",
}
