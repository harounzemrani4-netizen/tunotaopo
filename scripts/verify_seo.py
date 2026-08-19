#!/usr/bin/env python3
"""Comprueba titles, H1, meta, canonical, sitemap y enlaces internos de las páginas generadas."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://tunotaopo.es"
SKIP_DIRS = {
    "node_modules",
    "research",
    "tests",
    "scripts",
    "release",
    "data",
    ".aipa",
    "js",
    "css",
    "assets",
    "functions",
    "dist",
}


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title_parts: list[str] = []
        self.in_title = False
        self.h1_count = 0
        self.descriptions: list[str] = []
        self.canonical: str | None = None
        self.robots: str | None = None
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        data = {k: v or "" for k, v in attrs}
        if tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and data.get("name") == "description":
            self.descriptions.append(data.get("content", ""))
        elif tag == "meta" and data.get("name") == "robots":
            self.robots = data.get("content", "")
        elif tag == "link" and data.get("rel") == "canonical":
            self.canonical = data.get("href")
        elif tag == "a" and data.get("href"):
            self.links.append(data["href"])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self.title_parts).strip()


def html_pages() -> list[Path]:
    pages = []
    for path in ROOT.rglob("*.html"):
        rel = path.relative_to(ROOT)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        pages.append(path)
    return sorted(pages)


def resolve_href(page: Path, href: str) -> Path | None:
    if href.startswith(("mailto:", "tel:", "javascript:")):
        return None
    href = href.split("#", 1)[0].split("?", 1)[0]
    if not href:
        return None
    if href.startswith("http://") or href.startswith("https://"):
        parsed = urlparse(href)
        if parsed.netloc not in {"tunotaopo.es", "www.tunotaopo.es"}:
            return None
        path = parsed.path
        if path.endswith("/"):
            path += "index.html"
        elif not path.endswith(".html") and "." not in path.rsplit("/", 1)[-1]:
            path = path.rstrip("/") + "/index.html"
        return ROOT / path.lstrip("/")
    base = page.parent.as_posix() + "/"
    joined = urljoin("file:///" + base, href)
    local = joined.replace("file:///", "")
    target = Path(local)
    if target.suffix == "" or target.name == "":
        target = target / "index.html"
    return target


def sitemap_locs() -> list[str]:
    text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", text)


def main() -> int:
    errors: list[str] = []
    self_titles: dict[str, str] = {}
    self_descriptions: dict[str, str] = {}
    pages = html_pages()
    for path in pages:
        html = path.read_text(encoding="utf-8")
        parser = Page()
        parser.feed(html)
        rel = path.relative_to(ROOT).as_posix()
        if "OpoRuta" in html:
            errors.append(f"{rel}: menciona un competidor")
        is_embed = rel.startswith("embed/")
        page_url = f"{SITE}/" if rel == "index.html" else f"{SITE}/{rel.replace('/index.html', '/')}"
        if rel.endswith("404.html"):
            page_url = f"{SITE}/404.html"
        canonical_self = parser.canonical and parser.canonical.rstrip("/") == page_url.rstrip("/")
        if not parser.title:
            errors.append(f"{rel}: title vacío")
        elif canonical_self and not is_embed and parser.title in self_titles:
            errors.append(f"{rel}: title duplicado con {self_titles[parser.title]}")
        elif canonical_self and not is_embed:
            self_titles[parser.title] = rel
        if parser.h1_count != 1:
            errors.append(f"{rel}: H1 count={parser.h1_count}")
        if not parser.descriptions or not parser.descriptions[0].strip():
            errors.append(f"{rel}: meta description vacía")
        elif canonical_self and not is_embed:
            desc = parser.descriptions[0]
            if desc in self_descriptions and rel != "404.html":
                errors.append(f"{rel}: meta description duplicada con {self_descriptions[desc]}")
            else:
                self_descriptions[desc] = rel
        if not parser.canonical:
            errors.append(f"{rel}: canonical ausente")
        elif not parser.canonical.startswith(SITE):
            errors.append(f"{rel}: canonical no usa {SITE}: {parser.canonical}")
        if is_embed and (not parser.robots or "noindex" not in parser.robots):
            errors.append(f"{rel}: embed sin noindex")
        for href in parser.links:
            target = resolve_href(path, href)
            if target is None:
                continue
            try:
                target = target.resolve()
            except OSError:
                errors.append(f"{rel}: enlace irresoluble {href}")
                continue
            if ROOT.resolve() not in target.parents and target != ROOT.resolve():
                continue
            if not target.exists():
                errors.append(f"{rel}: enlace interno roto {href} -> {target.relative_to(ROOT) if ROOT in target.parents or target.parent == ROOT else target}")

    locs = sitemap_locs()
    if not locs:
        errors.append("sitemap.xml sin <loc>")
    if not (ROOT / "oposiciones" / "academias" / "index.html").exists():
        errors.append("falta oposiciones/academias/index.html")
    if (ROOT / "academias").exists():
        errors.append("la carpeta raíz academias/ debería haberse movido a oposiciones/academias/")
    tool_files = [
        ROOT / "calculadoras" / "guardia-civil" / "index.html",
        ROOT / "calculadoras" / "policia-nacional" / "index.html",
        ROOT / "calculadoras" / "ayudantes-iipp" / "index.html",
        ROOT / "calculadoras" / "auxilio-judicial" / "index.html",
        ROOT / "calculadoras" / "auxiliar-administrativo-age" / "index.html",
        ROOT / "oposiciones" / "policia-nacional" / "pruebas-fisicas" / "index.html",
        ROOT / "oposiciones" / "guardia-civil" / "pruebas-fisicas" / "index.html",
        ROOT / "oposiciones" / "guardia-civil" / "baremo" / "index.html",
    ]
    markers = (
        'id="classroom-enter"',
        'id="share-native"',
        'id="show-qr"',
        'id="save-progress"',
        "Reportar error",
    )
    for tool_path in tool_files:
        rel = tool_path.relative_to(ROOT).as_posix()
        if not tool_path.exists():
            errors.append(f"{rel}: no existe")
            continue
        html = tool_path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in html:
                errors.append(f"{rel}: falta {marker}")
        if "tool-toolbar" not in html:
            errors.append(f"{rel}: falta barra de herramientas visible")
    for loc in locs:
        if "/embed/" in loc:
            errors.append(f"sitemap incluye embed: {loc}")
        path = urlparse(loc).path
        if path.endswith("/"):
            file = ROOT / path.lstrip("/") / "index.html"
        else:
            file = ROOT / path.lstrip("/")
        if path not in {"/", ""} and not file.exists() and not (ROOT / path.lstrip("/") / "index.html").exists():
            if path == "/":
                file = ROOT / "index.html"
            if not file.exists():
                errors.append(f"sitemap apunta a archivo inexistente: {loc}")

    if errors:
        print(f"[FAIL] {len(errors)} comprobaciones SEO")
        for err in errors:
            print(" -", err)
        return 1
    print(f"[OK] SEO {len(pages)} páginas, {len(locs)} URLs en sitemap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
