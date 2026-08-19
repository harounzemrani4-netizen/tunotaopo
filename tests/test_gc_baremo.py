#!/usr/bin/env python3
"""Apéndice I Guardia Civil 2026 — BOE-A-2026-9982."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "js" / "engine" / "gc-baremo.js"


def evaluate(payload: dict) -> dict:
    script = ENGINE.read_text(encoding="utf-8") + (
        "\nconst out = NotaOpoGcBaremo.evaluate(" + json.dumps(payload) + ");"
        "\nprocess.stdout.write(JSON.stringify(out));\n"
    )
    proc = subprocess.run(
        ["node", "-e", script],
        capture_output=True,
        text=True,
        cwd=str(ROOT),
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr or proc.stdout or "node failed")
    return json.loads(proc.stdout)


def close(got: float, expected: float) -> bool:
    return abs(got - expected) < 1e-9


def main() -> int:
    tropa = evaluate(
        {
            "turno": "tropa",
            "tropa_years": 10,
            "tropa_rank": "cabo1",
            "academic": "none",
            "languages": [],
        }
    )
    if not close(tropa["professional"]["points"], 12.6):
        print(f"[FAIL] tropa 10 años + cabo 1º -> {tropa['professional']['points']}, esperado 12.6")
        return 1
    if tropa["professional"]["items"][0]["points"] != 9:
        print("[FAIL] 10 años de tropa deben toparse a 9")
        return 1

    libre = evaluate(
        {
            "turno": "libre",
            "age_years": 2,
            "reservist_months": 12,
            "academic": "bachiller",
            "languages": [{"lang": "ingles", "level": "c2", "via": "eoi"}],
            "perm_a": True,
            "perm_c": True,
        }
    )
    # 1.8 + 0.3 = 2.1 prof; 2 + 9 = 11 acad; 3+2=5 -> cap 4.5 other; total 17.6
    if not close(libre["professional"]["points"], 2.1):
        print(f"[FAIL] profesional libre {libre['professional']['points']}")
        return 1
    if not close(libre["academic"]["points"], 11):
        print(f"[FAIL] académico {libre['academic']['points']}")
        return 1
    if not close(libre["other"]["points"], 4.5):
        print(f"[FAIL] otros debe toparse a 4.5, got {libre['other']['points']}")
        return 1
    if not close(libre["total"], 17.6):
        print(f"[FAIL] total {libre['total']}")
        return 1

    filo = evaluate(
        {
            "turno": "libre",
            "academic": "filologia",
            "degree_lang": "ingles",
            "languages": [{"lang": "ingles", "level": "c2", "via": "eoi"}],
        }
    )
    if not close(filo["academic"]["points"], 9):
        print(f"[FAIL] filología + mismo idioma no duplica: {filo['academic']['points']}")
        return 1

    slp = evaluate(
        {
            "turno": "tropa",
            "academic": "none",
            "fas": True,
            "languages": [{"lang": "frances", "level": "c1", "via": "slp"}],
        }
    )
    if not close(slp["academic"]["points"], 7):
        print(f"[FAIL] SLP C1 {slp['academic']['points']}")
        return 1

    print("Baremo GC: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
