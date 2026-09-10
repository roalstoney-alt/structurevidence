from __future__ import annotations

from dataclasses import replace
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from evaluator import evaluate  # noqa: E402
from resolver import resolve  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_PROVENANCE_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def main() -> None:
    bnb = evaluate(resolve("BNB", ROOT), ROOT)
    if gate(bnb, "G2_RTP_PROVENANCE")["status"] != "PASS":
        fail("valid R1 provenance did not pass")
    missing = evaluate(replace(resolve("BNB", ROOT), source_inventory_path=ROOT / "missing.json"), ROOT)
    if gate(missing, "G2_RTP_PROVENANCE")["status"] != "FAIL" or missing.authorization != "VETO":
        fail("missing required artifact did not fail/veto")
    blank_hash = evaluate(replace(resolve("BNB", ROOT), sha256sums_path=None), ROOT)
    if gate(blank_hash, "G2_RTP_PROVENANCE")["status"] != "FAIL":
        fail("blank expected provenance hashes did not fail")
    mismatch = evaluate(replace(resolve("BNB", ROOT), source_inventory_path=resolve("SOL", ROOT).source_inventory_path), ROOT)
    if gate(mismatch, "G2_RTP_PROVENANCE")["status"] != "FAIL":
        fail("hash mismatch did not fail")
    strategy = evaluate(resolve("strategy", ROOT), ROOT)
    if gate(strategy, "G2_RTP_PROVENANCE")["status"] != "PARTIAL":
        fail("Strategy legacy provenance should be partial, not pass")
    print("GDR_SE_PROVENANCE_TESTS_PASS")


if __name__ == "__main__":
    main()
