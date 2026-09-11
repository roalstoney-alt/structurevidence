from __future__ import annotations

from datetime import date, timezone
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from clock import normalize_as_of  # noqa: E402
from evaluator import evaluate  # noqa: E402
from freshness import evaluate_freshness  # noqa: E402
from resolver import resolve  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_CLOCK_TEST_FAIL: {message}")


def gate(evaluation, gate_id: str) -> dict:
    return next(row for row in evaluation.gate_results if row["gate_id"] == gate_id)


def main() -> None:
    fixed = evaluate(resolve("SOL", ROOT), ROOT, as_of="2026-09-10T00:00:00Z")
    if fixed.evaluation_as_of != "2026-09-10T00:00:00Z":
        fail("injected UTC timestamp was not preserved")
    current = evaluate(resolve("SOL", ROOT), ROOT)
    if normalize_as_of(current.evaluation_as_of).tzinfo != timezone.utc:
        fail("current UTC path did not produce timezone-aware UTC")
    try:
        normalize_as_of("2026-09-10T00:00:00")
    except ValueError:
        pass
    else:
        fail("naive timestamp was accepted")
    configured = {"categories": {"FIXTURE": {"status": "CONFIGURED", "max_age_days": 30}}}
    status, _, _ = evaluate_freshness("FIXTURE", "2026-09-01", date(2026, 9, 10), configured)
    if status != "PASS":
        fail("configured fixture should pass within max age")
    status, _, _ = evaluate_freshness("FIXTURE", "2026-09-01", date(2026, 10, 15), configured)
    if status != "STALE":
        fail("configured fixture should become stale in the future")
    historical_a = evaluate(resolve("BNB", ROOT), ROOT, as_of="2026-09-10T00:00:00Z")
    historical_b = evaluate(resolve("BNB", ROOT), ROOT, as_of="2026-09-10T00:00:00Z")
    if historical_a.input_bundle_sha256 != historical_b.input_bundle_sha256:
        fail("historical reproduction changed the input bundle hash")
    if gate(evaluate(resolve("BNB", ROOT), ROOT, as_of="2027-09-10T00:00:00Z"), "G3_EVIDENCE_FRESHNESS")["computed_facts"].get("policy_version") != "RDL_FRESHNESS_v0.1a":
        fail("RDL freshness policy should remain the G3 source at historical as_of")
    print("GDR_SE_CLOCK_TESTS_PASS")


if __name__ == "__main__":
    main()
