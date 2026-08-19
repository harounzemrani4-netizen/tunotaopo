#!/usr/bin/env python3
"""Static security and ad-inventory checks. No live AdSense."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = list(ROOT.glob("*.html")) + list(ROOT.rglob("*/index.html"))
HTML = [p for p in HTML if "node_modules" not in p.parts and "research" not in p.parts]


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    raise SystemExit(1)


def main() -> int:
    errors = 0

    def err(msg: str) -> None:
        nonlocal errors
        errors += 1
        print(f"[FAIL] {msg}")

    ht = (ROOT / ".htaccess").read_text(encoding="utf-8")
    for needle in (
        "X-Content-Type-Options",
        "Content-Security-Policy",
        "X-Frame-Options",
        "Permissions-Policy",
        "Options -Indexes",
        "research|tests|scripts|release|data",
    ):
        if needle not in ht:
            err(f".htaccess missing {needle}")

    headers = (ROOT / "_headers").read_text(encoding="utf-8")
    for needle in (
        "X-Content-Type-Options",
        "Content-Security-Policy",
        "X-Frame-Options",
        "Permissions-Policy",
        "Cross-Origin-Opener-Policy",
        "Strict-Transport-Security",
    ):
        if needle not in headers:
            err(f"_headers missing {needle}")

    ads = (ROOT / "ads.txt").read_text(encoding="utf-8")
    if "pub-" in ads.lower() or "google.com" in ads.lower():
        err("ads.txt must not invent a Publisher ID")

    forbidden_src = (
        "googlesyndication",
        "googleadservices",
        "doubleclick",
        "googletagmanager",
        "google-analytics",
    )
    inline_handler = re.compile(r"\son\w+\s*=")
    csp_ok = 0
    reserved = 0
    active_ads = 0

    for path in HTML:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        low = text.lower()
        for src in forbidden_src:
            if src in low:
                err(f"{rel}: third-party ad/analytics script ({src})")
        if inline_handler.search(text):
            err(f"{rel}: inline event handler")
        if 'http-equiv="Content-Security-Policy"' in text:
            csp_ok += 1
        reserved += text.count("ad-slot is-reserved")
        active_ads += text.count("pagead2.googlesyndication")

    if csp_ok != len(HTML):
        err(f"CSP meta missing on {len(HTML) - csp_ok} HTML page(s)")
    if reserved < 20:
        err(f"expected reserved ad slots on public pages, found {reserved}")
    if active_ads:
        err("AdSense script present while ads must stay inactive")

    calc = (ROOT / "js" / "components" / "calculator.js").read_text(encoding="utf-8")
    if "function escapeHtml" not in calc:
        err("calculator.js missing escapeHtml")

    print(f"HTML pages: {len(HTML)}")
    print(f"Reserved ad slots: {reserved}")
    print(f"CSP pages: {csp_ok}/{len(HTML)}")
    if errors:
        print(f"Security checks: {errors} failure(s)")
        return 1
    print("Security checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
