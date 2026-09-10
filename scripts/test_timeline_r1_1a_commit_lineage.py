from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.validators import validate_commit_lineage  # noqa: E402


def main() -> None:
    results = validate_commit_lineage(remote_expected=False)
    lineage = next(row for row in results if row.gate_id == "TL11A_15_BASE_COMMIT_LINEAGE")
    if lineage.status != "PASS":
        raise SystemExit(f"TIMELINE_R1_1A_COMMIT_LINEAGE_FAIL: {lineage.computed_facts}")
    print("TIMELINE_R1_1A_COMMIT_LINEAGE_PASS")


if __name__ == "__main__":
    main()
