#!/usr/bin/env python3
"""Anexo II Policía Nacional 2026 — tablas BOE-A-2026-15055."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "js" / "engine" / "pn-fisicas.js"


def evaluate(payload: dict) -> dict:
    script = ENGINE.read_text(encoding="utf-8") + (
        "\nconst out = NotaOpoFisicas.evaluate(" + json.dumps(payload) + ");"
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
    cases = [
        ({"sex": "hombres", "circuit": "10.2", "pullups": "10", "run_min": "3", "run_sec": "18"}, 5, 5, 6),
        ({"sex": "hombres", "circuit": "8.2", "pullups": "17", "run_min": "2", "run_sec": "54"}, 10, 10, 10),
        ({"sex": "hombres", "circuit": "11.7", "pullups": "10", "run_min": "3", "run_sec": "18"}, 0, 5, 6),
        ({"sex": "mujeres", "circuit": "11.3", "hang": "95", "run_min": "3", "run_sec": "24"}, 5, 10, 10),
    ]
    for payload, c, f, r in cases:
        out = evaluate(payload)
        got = (out["circuit"]["score"], out["force"]["score"], out["run"]["score"])
        expected = (c, f, r)
        if got != expected:
            print(f"[FAIL] {payload} -> {got}, expected {expected}")
            return 1
        print(f"[OK] {payload['sex']} circuito {payload['circuit']}")
    zero = evaluate({"sex": "hombres", "circuit": "11.7", "pullups": "10", "run_min": "3", "run_sec": "18"})
    if zero["passed"] or not zero["zeroOut"]:
        print("[FAIL] 0 en circuito debe eliminar")
        return 1
    women_hang0 = evaluate({"sex": "mujeres", "circuit": "11.3", "hang": "35", "run_min": "3", "run_sec": "24"})
    if women_hang0["force"]["score"] != 0:
        print("[FAIL] 35 s suspensión mujeres debe ser 0")
        return 1
    women_hang1 = evaluate({"sex": "mujeres", "circuit": "11.3", "hang": "36", "run_min": "3", "run_sec": "24"})
    if women_hang1["force"]["score"] < 1:
        print("[FAIL] 36 s suspensión mujeres debe puntuar")
        return 1
    men_pull_lim = evaluate({"sex": "hombres", "circuit": "10.2", "pullups": "4", "run_min": "3", "run_sec": "18"})
    if men_pull_lim["force"]["score"] != 0:
        print("[FAIL] 4 dominadas hombres debe ser 0")
        return 1
    men_pull_ok = evaluate({"sex": "hombres", "circuit": "10.2", "pullups": "5", "run_min": "3", "run_sec": "18"})
    if men_pull_ok["force"]["score"] != 1:
        print("[FAIL] 5 dominadas hombres debe ser 1")
        return 1
    try:
        evaluate({"sex": "hombres", "circuit": "-1", "pullups": "10", "run_min": "3", "run_sec": "18"})
        print("[FAIL] circuito negativo debería fallar")
        return 1
    except SystemExit:
        pass
    except Exception:
        pass
    print("Físicas PN: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
