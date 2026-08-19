#!/usr/bin/env python3
"""Compare engine output to independently calculated fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from engine import evaluate  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def lookup(data, path: str):
    current = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current[part]
        else:
            raise KeyError(path)
    return current


def nearly_equal(actual, expected) -> bool:
    if isinstance(expected, bool) or expected is None:
        return actual is expected
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(actual) - float(expected)) < 1e-9
    return actual == expected


def run(prefix: str | None = None) -> int:
    fixtures = load_json(ROOT / "tests" / "fixtures.json")
    configs = {
        path.stem: load_json(path)
        for path in (ROOT / "data" / "oposiciones").glob("*.json")
    }
    failed = 0
    ran = 0
    for case in fixtures["cases"]:
        if prefix and not case["id"].startswith(prefix):
            continue
        ran += 1
        config = configs[case["config"]]
        expected = case["expected"]
        try:
            result = evaluate(config, case["inputs"])
        except Exception as exc:  # noqa: BLE001
            if expected.get("error") is True:
                print(f"[OK] {case['id']} (error: {exc})")
                continue
            failed += 1
            print(f"[FAIL] {case['id']}: unexpected error: {exc}")
            continue
        if expected.get("error") is True:
            failed += 1
            print(f"[FAIL] {case['id']}: expected error, got result")
            continue
        case_failed = False
        for key, value in expected.items():
            if key == "error":
                continue
            try:
                actual = lookup(result, key)
            except KeyError:
                failed += 1
                case_failed = True
                print(f"[FAIL] {case['id']}: missing {key}")
                continue
            if not nearly_equal(actual, value):
                failed += 1
                case_failed = True
                print(f"[FAIL] {case['id']}: {key} expected {value!r}, got {actual!r}")
        if not case_failed:
            print(f"[OK] {case['id']}")
    print(f"\nRan {ran} case(s), {failed} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    filt = sys.argv[1] if len(sys.argv) > 1 else None
    raise SystemExit(run(filt))
