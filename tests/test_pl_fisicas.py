#!/usr/bin/env python3
"""Anexo II Policía Municipal Madrid — BOAM núm. 9829."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "js" / "engine" / "pl-fisicas.js"


def evaluate(payload: dict) -> dict:
    script = ENGINE.read_text(encoding="utf-8") + (
        "\nconst out = NotaOpoPlFisicas.evaluate(" + json.dumps(payload) + ");"
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


def nearly(actual, expected) -> bool:
    if actual is None or expected is None:
        return actual is expected
    return abs(float(actual) - float(expected)) < 1e-9


def main() -> int:
    exact5 = {
        "sex": "hombres",
        "run800_min": "2",
        "run800_sec": "50",
        "run60": "9.10",
        "ball": "5.50",
        "jump": "2.15",
        "swim": "24.0",
    }
    out = evaluate(exact5)
    if not out["passed"] or out["average"] != 5:
        print(f"[FAIL] marcas de 5: {out}")
        return 1
    print("[OK] hombres marcas de 5 = media 5")

    exact10 = {
        "sex": "hombres",
        "run800_min": "1",
        "run800_sec": "55",
        "run60": "7",
        "ball": "10.50",
        "jump": "3.15",
        "swim": "10",
    }
    out = evaluate(exact10)
    if not out["passed"] or out["average"] != 10:
        print(f"[FAIL] marcas de 10: {out}")
        return 1
    print("[OK] hombres marcas de 10 = media 10")

    mid = {
        "sex": "hombres",
        "run800_min": "2",
        "run800_sec": "45",
        "run60": "8.68",
        "ball": "6.00",
        "jump": "2.35",
        "swim": "21.2",
    }
    out = evaluate(mid)
    if not nearly(out["events"]["run800"]["score"], 5.45):
        print(f"[FAIL] 800 m 2:45 interpolado: {out['events']['run800']}")
        return 1
    if not nearly(out["events"]["run60"]["score"], 6):
        print(f"[FAIL] 60 m 8,68: {out['events']['run60']}")
        return 1
    if not nearly(out["events"]["ball"]["score"], 5.5):
        print(f"[FAIL] balón 6,00 interpolado: {out['events']['ball']}")
        return 1
    print("[OK] interpolación 800 m y balón")

    fail = dict(exact5)
    fail["run800_sec"] = "55"
    fail["run800_min"] = "2"
    out = evaluate(fail)
    if out["passed"] or out["events"]["run800"]["score"] is not None or out["average"] is not None:
        print(f"[FAIL] 800 m peor que 5 no debe inventar nota: {out['events']['run800']} media={out['average']}")
        return 1
    print("[OK] peor que la marca de 5: sin nota inventada")

    women = {
        "sex": "mujeres",
        "run800_min": "3",
        "run800_sec": "30",
        "run60": "10.40",
        "ball": "5.50",
        "jump": "1.85",
        "swim": "26.0",
    }
    out = evaluate(women)
    if not out["passed"] or out["average"] != 5:
        print(f"[FAIL] mujeres marcas de 5: {out}")
        return 1
    print("[OK] mujeres marcas de 5 = media 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
