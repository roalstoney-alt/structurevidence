from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.validators import validate_append_simulation  # noqa: E402


def main() -> None:
    result = validate_append_simulation()
    if result.status != "PASS":
        raise SystemExit(f"TIMELINE_R1_1A_APPEND_SIMULATION_FAIL: {result.computed_facts}")
    print("TIMELINE_R1_1A_APPEND_SIMULATION_PASS")


if __name__ == "__main__":
    main()
