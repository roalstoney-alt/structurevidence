from __future__ import annotations

import copy
import json
import sys
from dataclasses import replace
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))
sys.path.insert(0, str(ROOT / "commercial" / "intelligence"))

from aggregation import aggregate  # noqa: E402
from evaluator import evaluate  # noqa: E402
from resolver import resolve  # noqa: E402


FIXED_AS_OF = "2026-09-10T00:00:00Z"


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_RUNTIME_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def semantic_gate_results(evaluation):
    return [{k: row[k] for k in ["gate_id", "status", "severity", "validator", "rule_version", "reason", "computed_facts"]} for row in evaluation.gate_results]


def test_runtime_records() -> None:
    for subject in ["strategy", "BNB", "SOL", "TRX", "XLM"]:
        evaluation = evaluate(resolve(subject, ROOT), ROOT, as_of=FIXED_AS_OF)
        if evaluation.authorization not in {"ALLOW_WITH_LIMITATIONS", "HUMAN_REVIEW_REQUIRED", "VETO"}:
            fail(f"{subject} produced unknown authorization")
        g3 = gate(evaluation, "G3_EVIDENCE_FRESHNESS")
        if g3["computed_facts"].get("policy_version") != "RDL_FRESHNESS_v0.1a":
            fail(f"{subject} G3 did not consume RDL freshness")
        if not evaluation.input_bundle_sha256 or len(evaluation.input_bundle_sha256) != 64:
            fail(f"{subject} missing input bundle hash")
        path = resolve(subject, ROOT).output_dir / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json"
        record = json.loads(path.read_text(encoding="utf-8"))
        if record["evaluation_mode"] != "RUNTIME_EVALUATED":
            fail(f"{subject} runtime record missing evaluation mode")
        if record["runtime_revision"] != "R1.1":
            fail(f"{subject} runtime record missing R1.1 revision")
        if not record["supersedes_authorization_id"]:
            fail(f"{subject} runtime record does not supersede prior static record")
        if record["authorization"] != evaluation.authorization:
            fail(f"{subject} written record diverges from production evaluator")


def test_determinism() -> None:
    first = evaluate(resolve("SOL", ROOT), ROOT, as_of=FIXED_AS_OF)
    second = evaluate(resolve("SOL", ROOT), ROOT, as_of=FIXED_AS_OF)
    if semantic_gate_results(first) != semantic_gate_results(second):
        fail("gate semantic results are not deterministic")
    if first.authorization != second.authorization or first.input_bundle_sha256 != second.input_bundle_sha256:
        fail("authorization or input bundle hash is not deterministic")


def test_no_upgrade_cases() -> None:
    sol = evaluate(resolve("SOL", ROOT), ROOT, as_of=FIXED_AS_OF)
    if gate(sol, "G6_ECL_CONSISTENCY")["status"] != "PARTIAL":
        fail("POTENTIAL_CONFLICT must map to PARTIAL")
    mutated = copy.deepcopy(sol.gate_results)
    for row in mutated:
        if row["gate_id"] == "G6_ECL_CONSISTENCY":
            row["status"] = "INSUFFICIENT_DATA"
    if aggregate(mutated) == "ALLOW_PUBLICATION":
        fail("INSUFFICIENT_DATA upgraded to allow publication")
    mutated = copy.deepcopy(sol.gate_results)
    for row in mutated:
        if row["gate_id"] == "G2_RTP_PROVENANCE":
            row["status"] = "FAIL"
            row["severity"] = "HARD"
    if aggregate(mutated) != "VETO":
        fail("missing provenance did not veto")
    superseded = replace(resolve("BNB", ROOT), supersession_status="SUPERSEDED")
    if evaluate(superseded, ROOT, as_of=FIXED_AS_OF).authorization != "VETO":
        fail("superseded report did not veto")


def main() -> None:
    test_runtime_records()
    test_determinism()
    test_no_upgrade_cases()
    print("GDR_SE_RUNTIME_TESTS_PASS")


if __name__ == "__main__":
    main()
