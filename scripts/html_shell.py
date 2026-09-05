"""Chrome HTML compartido: cabecera, pie, migas, envoltorio de página."""

from __future__ import annotations

import json
from urllib.parse import urljoin
from xml.sax.saxutils import escape

from site_config import (
    ACADEMIAS_PATH,
    AD_SIZES,
    ASSET_V,
    BRAND,
    BRAND_ALT,
    CSP,
    CSP_EMBED,
    PROGRESO_PATH,
    PUBLISHER,
    SITE,
)
from site_io import write as write_file


def rel_prefix(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def seo_title(*parts: str) -> str:
    left = " ".join(str(part) for part in parts if part)
    return f"{left} | {BRAND}"


def extra_paras(texts: list[str] | None) -> str:
    if not texts:
        return ""
    return "".join(f"<p>{escape(text)}</p>" for text in texts)


def write(path, text: str) -> None:
    write_file(path, text)


def pretty_href(path: str) -> str:
    clean = (path or "").replace("index.html", "").strip("/")
    return "/" if not clean else f"/{clean}/"


def nav_item_current(href: str, path: str) -> bool:
    cur = (path or "").strip("/")
    key = href.strip("/")
    if key == "oposiciones":
        if not cur.startswith("oposiciones"):
            return False
        if cur.startswith("oposiciones/progreso") or cur.startswith("oposiciones/academias"):
            return False
        return True
    if key == "calculadoras":
        return cur.startswith("calculadoras")
    if key == "oposiciones/progreso":
        return cur.startswith("oposiciones/progreso")
    if key == "fuentes":
        return cur.startswith("fuentes")
    return False


def nav_link(label: str, href: str, path: str, short: str | None = None) -> str:
    extra = ' class="is-current" aria-current="page"' if nav_item_current(href, path) else ""
    if short and short != label:
        inner = (
            f'<span class="nav-long">{escape(label)}</span>'
            f'<span class="nav-short">{escape(short)}</span>'
        )
    else:
        inner = escape(label)
    return f'<a href="{href}"{extra}>{inner}</a>'


def nav(prefix: str, path: str = "") -> str:
    return f"""<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="/">
      <img src="{prefix}assets/logo.svg" width="36" height="36" alt="">
      <span>{BRAND}</span>
    </a>
    <div class="header-tools">
      <nav class="nav" aria-label="Principal">
        {nav_link("Oposiciones", "/oposiciones/", path)}
        {nav_link("Calculadoras", "/calculadoras/", path, "Calcular")}
        {nav_link("Mi progreso", pretty_href(PROGRESO_PATH), path, "Progreso")}
        {nav_link("Fuentes", "/fuentes/", path)}
      </nav>
      <button type="button" class="theme-toggle" id="theme-toggle" aria-label="Cambiar tema">
        <svg class="theme-icon theme-icon-moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M21 14.5A8.8 8.8 0 0 1 9.5 3 7 7 0 1 0 21 14.5z"/></svg>
        <svg class="theme-icon theme-icon-sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4" fill="currentColor"/><g fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"><path d="M12 2.8v2M12 19.2v2M2.8 12h2M19.2 12h2M5.4 5.4l1.4 1.4M17.2 17.2l1.4 1.4M18.6 5.4l-1.4 1.4M6.8 17.2l-1.4 1.4"/></g></svg>
      </button>
    </div>
  </div>
</header>"""


def footer(prefix: str) -> str:
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <p>{BRAND}</p>
      <p class="footer-tag">Cálculo orientativo. Prevalece la convocatoria oficial.</p>
    </div>
    <div class="footer-links">
      <a href="/oposiciones/">Oposiciones</a>
      <a href="/calculadoras/">Calculadoras</a>
      <a href="{pretty_href(PROGRESO_PATH)}">Mi progreso</a>
      <a href="/metodologia/">Metodología</a>
      <a href="/fuentes/">Fuentes</a>
      <a href="/privacidad/">Privacidad</a>
      <a href="/cookies/">Cookies</a>
      <a href="/aviso-legal/">Aviso legal</a>
      <a href="{pretty_href(ACADEMIAS_PATH)}">Academias</a>
      <a href="/contacto/">Contacto</a>
    </div>
  </div>
</footer>"""


def asset_query(pin_assets: bool) -> str:
    return "" if pin_assets else f"?v={ASSET_V}"


def head(
    title: str,
    description: str,
    canonical: str,
    prefix: str,
    extra: str = "",
    csp: str | None = None,
    pin_assets: bool = False,
) -> str:
    policy = csp or CSP
    q = asset_query(pin_assets)
    css = f"{prefix}css/app.css{q}"
    boot = f"{prefix}js/theme-boot.js{q}"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta http-equiv="Content-Security-Policy" content="{policy}">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="theme-color" content="#0c1924">
  <meta name="color-scheme" content="light dark">
  <meta name="asset-v" content="{ASSET_V}">
  {extra}
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:type" content="{escape("website")}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:locale" content="es_ES">
  <meta property="og:site_name" content="{BRAND}">
  <meta property="og:image" content="{SITE}/assets/og.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{BRAND}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{SITE}/assets/og.png">
  <link rel="icon" href="{prefix}assets/logo.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{prefix}assets/logo.svg">
  <link rel="manifest" href="{prefix}manifest.webmanifest">
  <link rel="stylesheet" href="{css}">
  <script src="{boot}"></script>
</head>"""


def canonical_url(path: str) -> str:
    clean = (path or "").strip("/")
    return f"{SITE}/" if not clean else f"{SITE}/{clean}/"


def crumb_abs_url(href: str, page_path: str) -> str:
    current = canonical_url(page_path)
    if not href:
        return current
    if href.startswith(("http://", "https://")):
        raw = href
    elif href.startswith("/"):
        raw = urljoin(f"{SITE}/", href.lstrip("/"))
    else:
        raw = urljoin(current, href)
    if raw.endswith("/index.html"):
        raw = raw[: -len("index.html")]
    elif raw.endswith("index.html"):
        raw = raw[: -len("index.html")]
    if raw in {SITE, f"{SITE}/"}:
        return f"{SITE}/"
    if raw.endswith(".html"):
        return raw
    if not raw.endswith("/"):
        raw += "/"
    return raw


def crumbs(items: list[tuple[str, str]], page_path: str = "") -> str:
    lis = []
    schema = []
    for i, (name, href) in enumerate(items, start=1):
        abs_url = crumb_abs_url(href, page_path)
        if href:
            pretty = abs_url[len(SITE):] if abs_url.startswith(SITE) else href
            lis.append(f'<li><a href="{pretty}">{escape(name)}</a></li>')
        else:
            lis.append(f"<li>{escape(name)}</li>")
        schema.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": abs_url,
            }
        )
    data = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": schema}
    return (
        '<nav class="crumbs" aria-label="Migas de pan"><ol>'
        + "".join(lis)
        + "</ol></nav>"
        + f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    )


def ad_slot(place: str, size: str | None = None) -> str:
    box = size or AD_SIZES.get(place, "rectangle")
    return (
        f'<aside class="ad-slot is-reserved is-inactive" data-place="{escape(place)}" data-size="{box}" '
        f'hidden aria-hidden="true">'
        f'<p class="ad-kicker">Publicidad</p>'
        f'<div class="ad-box ad-box-{box}"></div>'
        f"</aside>"
    )


def legal_identity() -> str:
    address = PUBLISHER["address"] or "Pendiente de publicar"
    email = escape(PUBLISHER["email"])
    return (
        '<aside class="legal-pending">'
        '<p class="legal-pending-kicker">Identidad del editor</p>'
        f"<p>{BRAND} es un proyecto personal. El titular es una persona física, no una sociedad.</p>"
        "<dl>"
        f"<div><dt>Titular</dt><dd>{escape(PUBLISHER['name'])}</dd></div>"
        f"<div><dt>Domicilio</dt><dd>{escape(address)}</dd></div>"
        f'<div><dt>Correo</dt><dd><a href="mailto:{email}">{email}</a></dd></div>'
        "</dl>"
        "</aside>"
    )


def website_schema() -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": BRAND,
        "alternateName": BRAND_ALT,
        "url": f"{SITE}/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE}/oposiciones/?q={{search_term_string}}",
            "query-input": "required name=search_term_string",
        },
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


def scripts(prefix: str, tools: tuple[str, ...] = (), pin_assets: bool = False) -> str:
    q = asset_query(pin_assets)
    tags = [
        f'<script src="{prefix}js/components/analytics.js{q}" defer></script>',
        f'<script src="{prefix}js/components/tools.js{q}" defer></script>',
        f'<script src="{prefix}js/site.js{q}" defer></script>',
    ]
    extra = {
        "calculator": [
            f'<script src="{prefix}js/engine/scoring.js{q}" defer></script>',
            f'<script src="{prefix}js/lib/qr.js{q}" defer></script>',
            f'<script src="{prefix}js/components/calculator.js{q}" defer></script>',
        ],
        "fisicas": [
            f'<script src="{prefix}js/engine/pn-fisicas.js{q}" defer></script>',
            f'<script src="{prefix}js/lib/qr.js{q}" defer></script>',
            f'<script src="{prefix}js/components/fisicas.js{q}" defer></script>',
        ],
        "gc_fisicas": [
            f'<script src="{prefix}js/engine/gc-fisicas.js{q}" defer></script>',
            f'<script src="{prefix}js/lib/qr.js{q}" defer></script>',
            f'<script src="{prefix}js/components/gc-fisicas.js{q}" defer></script>',
        ],
        "gc_baremo": [
            f'<script src="{prefix}js/engine/gc-baremo.js{q}" defer></script>',
            f'<script src="{prefix}js/lib/qr.js{q}" defer></script>',
            f'<script src="{prefix}js/components/gc-baremo.js{q}" defer></script>',
        ],
        "pl_fisicas": [
            f'<script src="{prefix}js/engine/pl-fisicas.js{q}" defer></script>',
            f'<script src="{prefix}js/lib/qr.js{q}" defer></script>',
            f'<script src="{prefix}js/components/pl-fisicas.js{q}" defer></script>',
        ],
        "progreso": [
            f'<script src="{prefix}js/components/progreso.js{q}" defer></script>',
        ],
    }
    inserted = []
    for tool in tools:
        inserted.extend(extra.get(tool) or [])
    return "\n".join(inserted + tags)


def page_shell(
    title: str,
    description: str,
    path: str,
    depth: int,
    body: str,
    calculator: bool = False,
    noindex: bool = False,
    fisicas: bool = False,
    website: bool = False,
    tools: tuple[str, ...] = (),
    robots: str | None = None,
    pin_assets: bool = False,
) -> str:
    canonical = f"{SITE}/{path}" if path else f"{SITE}/"
    extras = []
    if robots:
        extras.append(f'<meta name="robots" content="{escape(robots)}">')
    elif noindex:
        extras.append('<meta name="robots" content="noindex">')
    if website:
        extras.append(website_schema())
    extra_head = "\n  ".join(extras)
    resolved = tuple(tools)
    if calculator:
        resolved = ("calculator",) + resolved
    if fisicas:
        resolved = ("fisicas",) + resolved
    return f"""{head(title, description, canonical, "/", extra_head, pin_assets=pin_assets)}
<body data-root="/">
  <a class="skip" href="#contenido">Saltar al contenido</a>
  {nav("/", path)}
  <div class="wrap">{ad_slot("top")}</div>
  <main id="contenido" class="wrap">
    {body}
  </main>
  <div class="wrap">{ad_slot("bottom")}</div>
  {footer("/")}
  {scripts("/", resolved, pin_assets=pin_assets)}
</body>
</html>
"""


def embed_shell(
    title: str,
    description: str,
    path: str,
    body: str,
    tools: tuple[str, ...] = (),
    open_href: str = "/",
) -> str:
    canonical = f"{SITE}/{path}"
    extra = '<meta name="robots" content="noindex,nofollow">'
    resolved = tuple(tools)
    return f"""{head(title, description, canonical, "/", extra, csp=CSP_EMBED)}
<body class="is-embed" data-root="/">
  <header class="embed-header">
    <div class="wrap">
      <a class="brand" href="{escape(open_href)}" target="_blank" rel="noopener">
        <img src="/assets/logo.svg" width="36" height="36" alt="">
        <span>{BRAND}</span>
      </a>
    </div>
  </header>
  <main id="contenido" class="wrap">
    {body}
  </main>
  <footer class="embed-footer">
    <div class="wrap">
      <p>Cálculo orientativo. Prevalece la convocatoria oficial. <a href="{escape(open_href)}" target="_blank" rel="noopener">Abrir en {BRAND}</a></p>
    </div>
  </footer>
  {scripts("/", resolved)}
</body>
</html>
"""
