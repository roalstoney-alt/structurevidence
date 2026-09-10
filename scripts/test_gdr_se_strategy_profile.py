from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from evaluator import evaluate  # noqa: E402
from resolver import resolve  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_STRATEGY_PROFILE_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def main() -> None:
    context = resolve("strategy", ROOT)
    if context.counter_evidence_path.name != "COUNTER_EVIDENCE_SEARCH_LOG_v3.json":
        fail("Strategy counter-evidence does not map to the executed log")
    if context.counter_evidence_path.name == "Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_EN.md":
        fail("Method Paper is still mapped as counter-evidence")
    for path in [context.source_dependency_path, context.counter_evidence_path, context.hypothesis_registry_path, context.claim_registry_path]:
        if path is None or not path.exists():
            fail(f"Strategy mapped artifact missing: {path}")
    evaluation = evaluate(context, ROOT, as_of="2026-09-10T00:00:00Z")
    if gate(evaluation, "G2_RTP_PROVENANCE")["status"] != "PARTIAL":
        fail("Strategy legacy provenance should remain partial where expected hashes are incomplete")
    if gate(evaluation, "G4_SOURCE_DEPENDENCY")["computed_facts"]["dependency_groups"] <= 0:
        fail("Strategy source dependency graph was not parsed")
    if gate(evaluation, "G7_COUNTER_EVIDENCE_COMPLETENESS")["status"] != "PASS":
        fail("Strategy executed counter-evidence log was not accepted by the parser")
    print("GDR_SE_STRATEGY_PROFILE_TESTS_PASS")


if __name__ == "__main__":
    main()
