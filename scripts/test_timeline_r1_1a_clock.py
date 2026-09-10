from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.validators import validate_clock  # noqa: E402


def main() -> None:
    results = validate_clock()
    failures = [row for row in results if row.status != "PASS"]
    if failures:
        raise SystemExit("TIMELINE_R1_1A_CLOCK_FAIL: " + ", ".join(f"{row.gate_id}={row.status}" for row in failures))
    naive = subprocess.run([sys.executable, "-B", "scripts/build_timeline_model.py", "--as-of", "2026-09-10T14:18:35"], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if naive.returncode == 0:
        raise SystemExit("TIMELINE_R1_1A_CLOCK_FAIL: naive CLI timestamp accepted")
    print("TIMELINE_R1_1A_CLOCK_PASS")


if __name__ == "__main__":
    main()
