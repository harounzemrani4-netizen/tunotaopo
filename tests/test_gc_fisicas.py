#!/usr/bin/env python3
"""Apéndice II Guardia Civil 2026 — BOE-A-2026-9982."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "js" / "engine" / "gc-fisicas.js"


def evaluate(payload: dict) -> dict:
    script = ENGINE.read_text(encoding="utf-8") + (
        "\nconst out = NotaOpoGcFisicas.evaluate(" + json.dumps(payload) + ");"
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


def main() -> int:
    exact = evaluate(
        {
            "sex": "hombres",
            "band": "lt35",
            "run_min": "9",
            "run_sec": "25",
            "circuit": "14.00",
            "pushups": "16",
            "swim": "70",
        }
    )
    if not exact["passed"]:
        print("[FAIL] exactamente el máximo/mínimo debe ser apto")
        return 1
    over = evaluate(
        {
            "sex": "hombres",
            "band": "lt35",
            "run_min": "9",
            "run_sec": "26",
            "circuit": "14.00",
            "pushups": "16",
            "swim": "70",
        }
    )
    if over["passed"] or over["tests"][0]["passed"]:
        print("[FAIL] 9:26 en 2.000 m hombres <35 debe ser no apto")
        return 1
    women = evaluate(
        {
            "sex": "mujeres",
            "band": "ge40",
            "run_min": "12",
            "run_sec": "49",
            "circuit": "17.90",
            "pushups": "9",
            "swim": "88",
        }
    )
    if not women["passed"]:
        print("[FAIL] mínimos mujeres ≥40 deben ser apto")
        return 1
    low_push = evaluate(
        {
            "sex": "mujeres",
            "band": "lt35",
            "run_min": "11",
            "run_sec": "14",
            "circuit": "16.00",
            "pushups": "10",
            "swim": "81",
        }
    )
    if low_push["passed"] or low_push["tests"][2]["passed"]:
        print("[FAIL] 10 extensiones mujeres <35 debe ser no apto")
        return 1
    swim_ok = evaluate(
        {
            "sex": "mujeres",
            "band": "lt35",
            "run_min": "11",
            "run_sec": "14",
            "circuit": "16.00",
            "pushups": "11",
            "swim": "81",
        }
    )
    if not swim_ok["passed"] or not swim_ok["tests"][3]["passed"]:
        print("[FAIL] 81 s natación mujeres <35 debe ser apto")
        return 1
    swim_over = evaluate(
        {
            "sex": "mujeres",
            "band": "lt35",
            "run_min": "11",
            "run_sec": "14",
            "circuit": "16.00",
            "pushups": "11",
            "swim": "85",
        }
    )
    if swim_over["passed"] or swim_over["tests"][3]["passed"]:
        print("[FAIL] 85 s natación mujeres <35 debe ser no apto")
        return 1
    print("Físicas GC: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
