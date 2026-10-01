#!/usr/bin/env python3
"""Fail when generated public records differ from the canonical export."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict[str, str]:
    patterns = ["cases/*/index.json", "cases/*/case.yaml", "cases/*/evidence.json", "cases/*/counter_evidence.json", "cases/*/unknowns.json", "cases/*/state_history.json", "cases/*/search_provenance.json", "e/*/index.json", "e/*/index.html"]
    files = sorted({path for pattern in patterns for path in ROOT.glob(pattern)})
    return {str(path.relative_to(ROOT)): digest(path) for path in files}


def main() -> int:
    before = snapshot()
    result = subprocess.run([sys.executable, str(ROOT / "scripts/export_public_records.py")], cwd=ROOT, check=False)
    after = snapshot()
    drift = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
    print(f"WEBSITE_STATE = {'PASS' if not drift else 'FAIL'}")
    print(f"GITHUB_STATE = {'PASS' if not drift else 'FAIL'}")
    print(f"PUBLIC_RECORD_DRIFT = {'PASS' if not drift else 'FAIL'}")
    for path in drift:
        print(f"DRIFT = {path}")
    return 1 if drift or result.returncode else 0


if __name__ == "__main__":
    raise SystemExit(main())
