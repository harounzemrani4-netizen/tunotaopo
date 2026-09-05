"""Assets generados en el build: SW versionado, offline y security.txt."""

from __future__ import annotations

from site_config import ASSET_V, CONTACT_EMAIL, CSP, CSP_EMBED, ROOT, SITE
from site_io import write
from html_shell import page_shell


SW_JS = f"""/* TuNotaOpo: cache de CSS, JS y motor. El HTML se pide a la red. */
var CACHE = "tunotaopo-core-{ASSET_V}";
var CORE = [
  "/offline.html",
  "/css/app.css?v={ASSET_V}",
  "/js/theme-boot.js?v={ASSET_V}",
  "/js/site.js?v={ASSET_V}",
  "/js/components/analytics.js?v={ASSET_V}",
  "/js/components/tools.js?v={ASSET_V}",
  "/js/engine/scoring.js?v={ASSET_V}",
  "/js/components/calculator.js?v={ASSET_V}",
  "/assets/logo.svg"
];

self.addEventListener("install", function (event) {{
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {{
      return cache.addAll(CORE);
    }}).then(function () {{
      return self.skipWaiting();
    }})
  );
}});

self.addEventListener("activate", function (event) {{
  event.waitUntil(
    caches.keys().then(function (keys) {{
      return Promise.all(
        keys.filter(function (key) {{ return key !== CACHE; }}).map(function (key) {{
          return caches.delete(key);
        }})
      );
    }}).then(function () {{
      return self.clients.claim();
    }})
  );
}});

self.addEventListener("fetch", function (event) {{
  var req = event.request;
  if (req.method !== "GET") return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (req.mode === "navigate" || (req.headers.get("accept") || "").indexOf("text/html") !== -1) {{
    event.respondWith(
      fetch(req).then(function (res) {{
        return res;
      }}).catch(function () {{
        return caches.match(req).then(function (hit) {{
          return hit || caches.match("/offline.html");
        }});
      }})
    );
    return;
  }}
  event.respondWith(
    caches.match(req).then(function (hit) {{
      return hit || fetch(req).then(function (res) {{
        if (res && res.ok && url.searchParams.get("v") && (url.pathname.indexOf("/js/") === 0 || url.pathname.indexOf("/css/") === 0)) {{
          var copy = res.clone();
          caches.open(CACHE).then(function (cache) {{
            cache.put(req, copy);
          }});
        }}
        return res;
      }});
    }})
  );
}});
"""

SECURITY_TXT = f"""Contact: mailto:{CONTACT_EMAIL}
Expires: 2027-09-03T00:00:00.000Z
Preferred-Languages: es
Canonical: {SITE}/.well-known/security.txt
"""


def offline_page() -> str:
    return page_shell(
        f"Sin conexión — TuNotaOpo",
        "Esta página se muestra si no hay red. Las calculadoras ya abiertas pueden seguir en este dispositivo.",
        "offline.html",
        0,
        """
    <div class="hero hero-home">
      <p class="eyebrow">Sin conexión</p>
      <h1>No hay red en este momento</h1>
      <p class="lede">Si ya habías abierto una calculadora, prueba a recargar. El motor vive en este dispositivo; las páginas nuevas necesitan conexión.</p>
      <p class="hero-actions"><a class="button button-primary" href="/">Ir al inicio</a>
      <a class="button button-secondary" href="/oposiciones/">Ver oposiciones</a></p>
    </div>
        """,
        noindex=True,
    )


HEADERS = f"""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=(), clipboard-write=(self)
  Cross-Origin-Opener-Policy: same-origin
  Content-Security-Policy: {CSP}
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Cache-Control: no-cache, must-revalidate

/*.webp
  Cache-Control: public, max-age=2592000

/*.jpg
  Cache-Control: public, max-age=2592000

/*.jpeg
  Cache-Control: public, max-age=2592000

/*.png
  Cache-Control: public, max-age=2592000

/*.svg
  Cache-Control: public, max-age=2592000

/*.avif
  Cache-Control: public, max-age=2592000

/*.ico
  Cache-Control: public, max-age=2592000

/*.woff
  Cache-Control: public, max-age=2592000

/*.woff2
  Cache-Control: public, max-age=2592000

/embed/*
  X-Frame-Options: ALLOWALL
  Content-Security-Policy: {CSP_EMBED}
"""


def write_htaccess_csp() -> None:
    path = ROOT / ".htaccess"
    text = path.read_text(encoding="utf-8")
    needle = 'Header always set Content-Security-Policy "'
    start = text.find(needle)
    if start < 0:
        raise SystemExit(".htaccess sin Content-Security-Policy")
    quote = start + len(needle)
    end = text.find('"', quote)
    if end < 0:
        raise SystemExit(".htaccess CSP sin cierre")
    path.write_text(text[:quote] + CSP + text[end:], encoding="utf-8")


def write_generated_assets() -> None:
    write(ROOT / "sw.js", SW_JS)
    write(ROOT / "offline.html", offline_page())
    write(ROOT / ".well-known" / "security.txt", SECURITY_TXT)
    write(ROOT / "_headers", HEADERS)
    write_htaccess_csp()
