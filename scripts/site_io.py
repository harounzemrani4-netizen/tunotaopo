"""Escritura de HTML: no toca el disco si el contenido no cambió."""

from __future__ import annotations

from pathlib import Path


def write(path: Path, text: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n")
    if path.exists():
        try:
            if path.read_text(encoding="utf-8") == normalized:
                return False
        except OSError:
            pass
    path.write_text(normalized, encoding="utf-8", newline="\n")
    return True
