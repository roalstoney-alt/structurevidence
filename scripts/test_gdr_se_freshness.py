from __future__ import annotations

from datetime import date
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from freshness import evaluate_freshness  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_FRESHNESS_TEST_FAIL: {message}")


def main() -> None:
    config = {"categories": {"CORPORATE_TREASURY": {"status": "UNCONFIGURED"}}}
    status, reason, facts = evaluate_freshness("CORPORATE_TREASURY", "2026-09-08", date(2026, 9, 10), config, subject="strategy")
    if facts.get("policy_version") != "RDL_FRESHNESS_v0.1a":
        fail("mapped subject did not consume RDL freshness policy")
    status, _, facts = evaluate_freshness("UNKNOWN", "2026-09-08", date(2026, 9, 10), config)
    if status != "UNRESOLVED" or facts["policy_status"] != "ABSENT":
        fail("unknown freshness category did not become UNRESOLVED")
    configured = {"categories": {"L1_NETWORK": {"status": "CONFIGURED", "max_age_days": 1, "date_field": "last_reviewed"}}}
    status, _, facts = evaluate_freshness("L1_NETWORK", "2026-09-01", date(2026, 9, 10), configured, subject="missing")
    if status != "STALE" or facts["age_days"] != 9:
        fail("configured stale policy did not compute age")
    print("GDR_SE_FRESHNESS_TESTS_PASS")


if __name__ == "__main__":
    main()
