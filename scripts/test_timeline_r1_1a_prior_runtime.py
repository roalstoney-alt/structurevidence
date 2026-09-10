from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.validators import (  # noqa: E402
    validate_comparison_lineage,
    validate_explicit_change_precedence,
    validate_noncomparable_prior_block,
    validate_prior_comparison_runtime,
)


def main() -> None:
    results = [
        validate_prior_comparison_runtime(),
        validate_comparison_lineage(),
        validate_noncomparable_prior_block(),
        validate_explicit_change_precedence(),
    ]
    failures = [row for row in results if row.status != "PASS"]
    if failures:
        raise SystemExit("TIMELINE_R1_1A_PRIOR_RUNTIME_FAIL: " + ", ".join(f"{row.gate_id}={row.status}" for row in failures))
    print("TIMELINE_R1_1A_PRIOR_RUNTIME_PASS")


if __name__ == "__main__":
    main()
