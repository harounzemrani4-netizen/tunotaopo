#!/usr/bin/env python3
"""Run local QA: engine fixtures, manifest, verify_project."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT.parent / "skill_archive" / "crear-web-micro-saas" / "scripts"


def run(cmd: list[str]) -> None:
    print(">", " ".join(cmd))
    subprocess.check_call(cmd, cwd=ROOT)


def main() -> int:
    run([sys.executable, str(ROOT / "scripts" / "generate_pages.py")])
    run([sys.executable, str(ROOT / "tests" / "test_engine.py")])
    run([sys.executable, str(ROOT / "tests" / "test_fisicas.py")])
    run([sys.executable, str(ROOT / "tests" / "test_gc_fisicas.py")])
    run([sys.executable, str(ROOT / "tests" / "test_gc_baremo.py")])
    run([sys.executable, str(ROOT / "tests" / "test_security.py")])
    run([sys.executable, str(SKILL / "validate_project_manifest.py"), str(ROOT / "project-manifest.json")])
    run([sys.executable, str(SKILL / "verify_project.py"), "--project", str(ROOT)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
