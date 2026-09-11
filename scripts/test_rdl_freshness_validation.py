from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from rdl.freshness.validation.gate_registry import GATES, normalize, summarize  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"RDL_FRESHNESS_VALIDATION_TEST_FAIL: {message}")


def main() -> None:
    rows = normalize([])
    if len(rows) != 45 or any(row["status"] != "NOT_EVALUATED" for row in rows):
        fail("missing validators are not registered as NOT_EVALUATED")
    if summarize(rows)["acceptance"] != "METHOD_PILOT_PARTIAL":
        fail("NOT_EVALUATED registry should not pass")
    registry = json.loads((ROOT / "rdl/freshness/validation/RDL_FRESHNESS_GATE_RESULTS.json").read_text(encoding="utf-8"))
    if [row["gate_id"] for row in registry["results"]] != GATES:
        fail("gate registry order or completeness changed")
    print("RDL_FRESHNESS_VALIDATION_TESTS_PASS")


if __name__ == "__main__":
    main()
