from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import publish_rdl_freshness as pub


def fail(message: str) -> None:
    raise SystemExit(f"RDL_FRESHNESS_RUNTIME_TEST_FAIL: {message}")


def main() -> None:
    policy = pub.load_policy()
    as_of = pub.parse_as_of("2026-09-11T00:00:00Z")
    fixture = copy.deepcopy(policy)
    fixture.profiles["profiles"].append({
        "rule_id": "FIXTURE-LEVEL",
        "subject_class": "L1_NETWORK",
        "dimension_id": "UTILITY_STRUCTURE",
        "state_type": "LEVEL",
        "time_rule": {"rule_type": "FIXED_WINDOW", "current_boundary_days": 10, "aging_boundary_days": 20, "refresh_boundary_days": 30},
        "event_triggers": ["PROTOCOL_UPGRADE"],
        "required_evidence_families": [],
        "evidence_basis": "EXPERT_METHOD_RULE",
        "evidence_strength": "WEAK",
        "status": "CONFIGURED",
    })
    if pub.time_state(fixture.profiles["profiles"][-1], 60) != "REFRESH_REQUIRED":
        fail("config mutation did not change Level freshness")
    if pub.time_state(pub.match_profile(policy, "L1_NETWORK", "UTILITY_STRUCTURE", "DELTA"), 10) != "POLICY_NOT_CONFIGURED":
        fail("Delta sparse state should remain policy-not-configured")
    event = {"event_id": "E", "known_at": "2026-09-03T00:00:00Z", "effective_at": "2026-09-03T00:00:00Z", "trigger_type": "GOVERNANCE_CHANGE", "verification_status": "VERIFIED"}
    if not pub.matching_events(policy, "L1_NETWORK", "GOVERNANCE_STRUCTURE", {"events": [event]}, "2026-09-01T00:00:00Z", as_of, "LEVEL"):
        fail("verified known event did not invalidate")
    if pub.matching_events(policy, "L1_NETWORK", "GOVERNANCE_STRUCTURE", {"events": [dict(event, known_at="2026-10-01T00:00:00Z")]}, "2026-09-01T00:00:00Z", as_of, "LEVEL"):
        fail("future-known event leaked into historical as_of")
    if pub.precedence_pick(policy, ["CURRENT", "SUPERSEDED"]) != "SUPERSEDED":
        fail("supersession precedence failed")
    first = json.loads((ROOT / "research/freshness/sol/FRESHNESS_EVALUATION_v0.1a.json").read_text(encoding="utf-8"))["input_bundle_hash"]
    pub.build(as_of)
    second = json.loads((ROOT / "research/freshness/sol/FRESHNESS_EVALUATION_v0.1a.json").read_text(encoding="utf-8"))["input_bundle_hash"]
    if first != second:
        fail("explicit as_of build is not reproducible")
    print("RDL_FRESHNESS_RUNTIME_TESTS_PASS")


if __name__ == "__main__":
    main()
