#!/usr/bin/env python3
"""Encoding auditor: disk bytes + UTF-8 strict. Do not trust Windows console glyphs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules"}
TEXT_EXTENSIONS = {
    ".html",
    ".htm",
    ".json",
    ".xml",
    ".js",
    ".css",
    ".md",
    ".txt",
    ".py",
    ".yml",
    ".yaml",
}
MOJIBAKE_MARKERS = [
    "\ufffd",
    "Ã¡",
    "Ã©",
    "Ã­",
    "Ã³",
    "Ãº",
    "Ã±",
    "Ã¼",
    "Â¿",
    "Â¡",
    "â€™",
    "â€œ",
    "â€",
]
EXPECTED_WORDS = {
    "teoría": "74 65 6f 72 c3 ad 61",
    "psicotécnicos": "70 73 69 63 6f 74 c3 a9 63 6e 69 63 6f 73",
    "calificación": "63 61 6c 69 66 69 63 61 63 69 c3 b3 6e",
    "puntuación": "70 75 6e 74 75 61 63 69 c3 b3 6e",
}
WORD_FILES = [
    ROOT / "calculadoras/auxiliar-administrativo-age/calculadora-nota-2026/index.html",
    ROOT / "calculadoras/guardia-civil/calculadora-nota-2026/index.html",
    ROOT / "calculadoras/ayudantes-iipp/calculadora-nota-2026/index.html",
    ROOT / "calculadoras/auxilio-judicial/calculadora-nota-2026/index.html",
    ROOT / "data/oposiciones/auxiliar-age-2026.json",
    ROOT / "data/oposiciones/guardia-civil-2026.json",
    ROOT / "data/oposiciones/ayudantes-iipp-2026.json",
    ROOT / "js/engine/scoring.js",
    ROOT / "js/components/calculator.js",
    ROOT / "project-manifest.json",
]


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        yield path


def has_charset_meta(text: str) -> bool:
    lower = text.lower()
    if '<meta charset="utf-8">' in lower:
        return True
    if "<meta charset='utf-8'>" in lower:
        return True
    if "<meta charset=utf-8>" in lower:
        return True
    if re.search(r'<meta\s+charset\s*=\s*["\']?utf-8["\']?', lower):
        return True
    if "charset=utf-8" in lower and "http-equiv" in lower:
        return True
    return False


def hex_of(word: str) -> str:
    return word.encode("utf-8").hex(" ")


def word_proof(errors: list[str], warnings: list[str], proof: list[dict]) -> None:
    for path in WORD_FILES:
        rel = str(path.relative_to(ROOT))
        if not path.is_file():
            warnings.append(f"{rel}: no existe para prueba de palabras")
            continue
        text = path.read_text(encoding="utf-8")
        found = {}
        for word, expected_hex in EXPECTED_WORDS.items():
            present = word in text
            actual_hex = hex_of(word)
            found[word] = {
                "present": present,
                "repr": repr(word),
                "expected_utf8_hex": expected_hex,
                "literal_utf8_hex": actual_hex,
                "literal_matches_expected": actual_hex == expected_hex,
            }
            if present:
                start = text.index(word)
                snippet = text[start : start + len(word)]
                snippet_hex = snippet.encode("utf-8").hex(" ")
                found[word]["on_disk_repr"] = repr(snippet)
                found[word]["on_disk_hex"] = snippet_hex
                if snippet != word or snippet_hex != expected_hex:
                    errors.append(
                        f"{rel}: {word!r} en disco no coincide: {snippet!r} hex={snippet_hex}"
                    )
                broken = "teor\ufffda" in text or "teorÃ­a" in text
                if word == "teoría" and broken:
                    errors.append(f"{rel}: aparece teoría corrupta junto a la forma correcta")
        proof.append({"file": rel, "words": found})


def seo_and_messages(errors: list[str], warnings: list[str]) -> None:
    html_files = [p for p in iter_text_files() if p.suffix.lower() in {".html", ".htm"}]
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT))
        if not has_charset_meta(text):
            warnings.append(f"{rel}: falta meta charset UTF-8")
        title = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.I | re.S)
        for label, match in (("title", title), ("meta description", desc)):
            if not match:
                continue
            value = re.sub(r"\s+", " ", match.group(1)).strip()
            if "\ufffd" in value or any(m in value for m in MOJIBAKE_MARKERS if m != "\ufffd"):
                errors.append(f"{rel}: {label} con mojibake: {value!r}")
        if '<script type="application/ld+json">' in text.lower():
            for block in re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                text,
                flags=re.I | re.S,
            ):
                try:
                    json.loads(block)
                except json.JSONDecodeError as exc:
                    errors.append(f"{rel}: JSON-LD inválido: {exc}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    scanned = 0

    for path in iter_text_files():
        scanned += 1
        rel = str(path.relative_to(ROOT))
        try:
            raw = path.read_bytes()
            if b"\x00" in raw:
                errors.append(f"{rel}: contiene byte NUL")
                continue
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            errors.append(f"{rel}: no es UTF-8 válido: {exc}")
            continue

        if path.resolve() != Path(__file__).resolve():
            for marker in MOJIBAKE_MARKERS:
                if marker in text:
                    warnings.append(f"{rel}: posible mojibake {marker!r}")

    proof: list[dict] = []
    word_proof(errors, warnings, proof)
    seo_and_messages(errors, warnings)

    report = {
        "verdict": "FAIL" if errors else "Disk UTF-8 PASS / Windows console display issue",
        "scanned_files": scanned,
        "errors": errors,
        "warnings": warnings,
        "word_proof": proof,
        "expected_literals": {word: {"repr": repr(word), "hex": hex_} for word, hex_ in EXPECTED_WORDS.items()},
    }
    report_path = ROOT / "research" / "encoding-audit-2026-08-19.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("ENCODING AUDIT")
    print(f"Scanned: {scanned}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")
    print(f"Report: {report_path.relative_to(ROOT)}")
    if not errors:
        print("Disk UTF-8 PASS / Windows console display issue")

    for item in errors:
        print("[ERROR]", item)
    for item in warnings:
        print("[WARN]", item)

    print("WORD PROOF (repr + utf-8 hex; ignore console glyphs)")
    for word, expected_hex in EXPECTED_WORDS.items():
        print(f"  literal {word!r} hex={hex_of(word)} expected={expected_hex} match={hex_of(word) == expected_hex}")
    for entry in proof:
        present = [w for w, info in entry["words"].items() if info["present"]]
        print(f"  {entry['file']}: found={present}")
        for word in present:
            info = entry["words"][word]
            print(f"    {word!r} on_disk_repr={info.get('on_disk_repr')} on_disk_hex={info.get('on_disk_hex')}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
