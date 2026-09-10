from __future__ import annotations

from dataclasses import replace
import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from evaluator import evaluate  # noqa: E402
from resolver import resolve  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_COUNTER_EVIDENCE_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def main() -> None:
    missing = evaluate(replace(resolve("BNB", ROOT), counter_evidence_path=ROOT / "missing_counter.json"), ROOT)
    if gate(missing, "G7_COUNTER_EVIDENCE_COMPLETENESS")["status"] != "FAIL" or missing.authorization != "VETO":
        fail("missing counter-evidence did not fail/veto")
    with tempfile.TemporaryDirectory() as tmp:
        generic_path = Path(tmp) / "generic_counter_evidence_fixture.json"
        fixture = [
            {"hypothesis_id": f"BNB-R1-H{i}", "queries": ["generic counter evidence"], "sources_checked": ["S"], "impact": "boilerplate", "remaining_uncertainty": "unknown"}
            for i in range(1, 6)
        ]
        generic_path.write_text(json.dumps(fixture), encoding="utf-8")
        generic = evaluate(replace(resolve("BNB", ROOT), counter_evidence_path=generic_path), ROOT)
    if gate(generic, "G7_COUNTER_EVIDENCE_COMPLETENESS")["status"] == "PASS":
        fail("generic counter-evidence placeholder passed")
    valid = evaluate(resolve("SOL", ROOT), ROOT)
    if gate(valid, "G7_COUNTER_EVIDENCE_COMPLETENESS")["status"] != "PARTIAL":
        fail("current repeated-pattern R1 log should be partial rather than pass")
    print("GDR_SE_COUNTER_EVIDENCE_TESTS_PASS")


if __name__ == "__main__":
    main()
