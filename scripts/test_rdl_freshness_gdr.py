from __future__ import annotations

import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from evaluator import evaluate  # noqa: E402
from freshness import evaluate_freshness  # noqa: E402
from resolver import resolve  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"RDL_FRESHNESS_GDR_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def main() -> None:
    for subject in ["strategy", "BNB", "SOL", "TRX", "XLM"]:
        evaluation = evaluate(resolve(subject, ROOT), ROOT, as_of="2026-09-11T00:00:00Z")
        g3 = gate(evaluation, "G3_EVIDENCE_FRESHNESS")
        if g3["computed_facts"].get("policy_version") != "RDL_FRESHNESS_v0.1":
            fail(f"{subject} G3 did not consume RDL policy")
        if evaluation.authorization == "ALLOW_PUBLICATION":
            fail(f"{subject} was upgraded to unrestricted publication by freshness")
    status, _, facts = evaluate_freshness("MARKET_CONTEXT", "2026-09-01", date(2026, 9, 11), subject="missing")
    if status != "UNRESOLVED" or facts.get("policy_status") not in {"UNCONFIGURED", "ABSENT"}:
        fail("unmapped GDR category did not remain unresolved")
    status, _, facts = evaluate_freshness("MARKET_CONTEXT", "2026-09-01", date(2026, 9, 11), {"categories": {}}, subject="missing")
    if status != "UNRESOLVED" or facts.get("policy_status") != "ABSENT":
        fail("absent fallback category did not remain unresolved")
    print("RDL_FRESHNESS_GDR_TESTS_PASS")


if __name__ == "__main__":
    main()
