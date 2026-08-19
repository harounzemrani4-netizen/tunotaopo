#!/usr/bin/env python3
"""Copy only public files into dist/ for Cloudflare Pages. No build step."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

PUBLIC_FILES = (
    "index.html",
    "404.html",
    "ads.txt",
    "robots.txt",
    "sitemap.xml",
    "_headers",
)

PUBLIC_DIRS = (
    "assets",
    "aviso-legal",
    "calculadoras",
    "contacto",
    "cookies",
    "css",
    "fuentes",
    "js",
    "metodologia",
    "privacidad",
)

BLOCKED = {
    "data",
    "dist",
    "node_modules",
    "release",
    "research",
    "scripts",
    "tests",
}


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()

    for name in PUBLIC_FILES:
        src = ROOT / name
        if not src.is_file():
            raise SystemExit(f"missing public file: {name}")
        shutil.copy2(src, DIST / name)

    for name in PUBLIC_DIRS:
        src = ROOT / name
        if not src.is_dir():
            raise SystemExit(f"missing public directory: {name}")
        shutil.copytree(src, DIST / name, ignore=shutil.ignore_patterns(".*"))

    leaked = [p.name for p in DIST.iterdir() if p.name in BLOCKED]
    if leaked:
        raise SystemExit(f"blocked paths leaked into dist/: {leaked}")

    print("Cloudflare Pages bundle:", DIST)


if __name__ == "__main__":
    main()
