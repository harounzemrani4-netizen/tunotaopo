#!/usr/bin/env python3
"""Python y JS deben dar la misma nota sobre las mismas fixtures."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from engine import evaluate  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"[FAIL] {message}")


def lookup(data, path: str):
    current = data
    for part in path.split("."):
        current = current[part]
    return current


def nearly_equal(actual, expected) -> bool:
    if isinstance(expected, bool) or expected is None:
        return actual is expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(actual) - float(expected)) < 1e-9
    return actual == expected


def python_cases() -> dict[str, dict]:
    fixtures = json.loads((ROOT / "tests" / "fixtures.json").read_text(encoding="utf-8"))
    configs = {
        path.stem: json.loads(path.read_text(encoding="utf-8"))
        for path in (ROOT / "data" / "oposiciones").glob("*.json")
    }
    out: dict[str, dict] = {}
    for case in fixtures["cases"]:
        expected = case["expected"]
        try:
            result = evaluate(configs[case["config"]], case["inputs"])
        except Exception as exc:  # noqa: BLE001
            out[case["id"]] = {"error": True, "message": str(exc)}
            continue
        row = {"error": False}
        for key in expected:
            if key == "error":
                continue
            row[key] = lookup(result, key)
        out[case["id"]] = row
    return out


def main() -> int:
    node = shutil.which("node")
    if not node:
        fail("hace falta node para comparar el motor JS")

    js = subprocess.run(
        [node, str(ROOT / "tests" / "engine_js_runner.js")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if js.returncode != 0:
        sys.stderr.write(js.stdout)
        sys.stderr.write(js.stderr)
        fail("el motor JS no reproduce las fixtures")

    py = python_cases()
    fixtures = json.loads((ROOT / "tests" / "fixtures.json").read_text(encoding="utf-8"))
    mismatches = 0
    for case in fixtures["cases"]:
        cid = case["id"]
        expected_error = case["expected"].get("error") is True
        got = py[cid]
        if expected_error:
            if not got.get("error"):
                mismatches += 1
                print(f"[FAIL] {cid}: Python no fallo y JS si (o al reves)")
            continue
        if got.get("error"):
            mismatches += 1
            print(f"[FAIL] {cid}: Python error {got.get('message')}")
    if mismatches:
        fail(f"paridad JS/Python: {mismatches} desajuste(s)")
    print("[OK] motor JS y Python alineados sobre las fixtures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
