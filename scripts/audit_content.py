#!/usr/bin/env python3
"""Mide texto visible y repetición entre las páginas del sitemap."""

from __future__ import annotations

import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


class Text(HTMLParser):
    SKIP = {"script", "style", "noscript", "svg", "template"}
    CHROME = {"header", "footer", "nav"}

    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.chrome = 0
        self.main: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.CHROME:
            self.chrome += 1
        if "hidden" in data and tag not in {"input"}:
            self.hidden += 1 if tag not in {"br", "img", "meta", "link"} else 0

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.CHROME and self.chrome:
            self.chrome -= 1

    def handle_data(self, data):
        if self.skip or self.chrome:
            return
        text = data.strip()
        if text:
            self.main.append(text)


def page_for(loc: str) -> Path:
    path = urlparse(loc).path.lstrip("/")
    return ROOT / path / "index.html" if not path.endswith(".html") else ROOT / path


def main() -> int:
    locs = re.findall(r"<loc>([^<]+)</loc>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))
    rows = []
    sentence_pages: dict[str, set[str]] = {}
    for loc in locs:
        file = page_for(loc)
        parser = Text()
        parser.feed(file.read_text(encoding="utf-8"))
        text = " ".join(parser.main)
        words = len(re.findall(r"\w+", text))
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            sentence = sentence.strip()
            if len(sentence) > 60:
                sentence_pages.setdefault(sentence, set()).add(loc)
        rows.append((words, loc, text))
    shared = Counter()
    for sentence, pages in sentence_pages.items():
        if len(pages) >= 4:
            for loc in pages:
                shared[loc] += len(sentence.split())
    print("words  shared  url")
    for words, loc, _ in sorted(rows):
        print(f"{words:5d}  {shared[loc]:6d}  {loc}")
    print()
    print("Frases repetidas en 4+ páginas:")
    for sentence, pages in sorted(sentence_pages.items(), key=lambda kv: -len(kv[1]))[:25]:
        if len(pages) >= 4:
            print(f"  [{len(pages)}] {sentence[:140]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
