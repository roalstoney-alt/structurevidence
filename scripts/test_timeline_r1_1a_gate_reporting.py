from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.validation.gate_registry import normalize_results  # noqa: E402
from timeline.validation.gate_runner import REGISTRY_PATH, REPORT_PATH, run  # noqa: E402
from timeline.validation.reporter import render_report  # noqa: E402
from timeline.validation.validators import result, validate_gate_reporting  # noqa: E402


def main() -> None:
    run()
    results = validate_gate_reporting(REGISTRY_PATH, REPORT_PATH)
    failures = [row for row in results if row.status != "PASS"]
    if failures:
        raise SystemExit("TIMELINE_R1_1A_GATE_REPORTING_FAIL: " + ", ".join(f"{row.gate_id}={row.status}" for row in failures))
    mutated = normalize_results([result("TL11A_01_PRIOR_COMPARISON_RUNTIME", "FAIL", "fixture", ["fixture"], {}, "mutation")])
    report = render_report({"results": mutated, "metadata": {}})
    if "PRIOR_COMPARISON_RUNTIME\nFAIL" not in report:
        raise SystemExit("TIMELINE_R1_1A_GATE_REPORTING_FAIL: mutation did not affect report")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    if any(row["status"] == "NOT_EVALUATED" for row in registry["results"]):
        raise SystemExit("TIMELINE_R1_1A_GATE_REPORTING_FAIL: mandatory gate not evaluated")
    print("TIMELINE_R1_1A_GATE_REPORTING_PASS")


if __name__ == "__main__":
    main()
