#!/usr/bin/env python3
from monitoring_test_common import pass_message, require
from monitoring.runtime.validators import validate_append_only_events, validate_dual_axis


def main() -> None:
    false_with_impact = {"epistemic_status": "FALSE", "market_impact_status": "ATTENTION_SHOCK", "causal_status": "TEMPORALLY_ASSOCIATED"}
    validate_dual_axis(false_with_impact)
    verified_without_impact = {"epistemic_status": "SUPPORTED", "market_impact_status": "NOT_MEASURED", "causal_status": "NOT_EVALUATED"}
    validate_dual_axis(verified_without_impact)
    hash_matched = dict(false_with_impact, artifact_sha256=["0" * 64])
    validate_dual_axis(hash_matched)
    require(hash_matched["epistemic_status"] == "FALSE", "hash must not upgrade epistemic status")
    require(false_with_impact["epistemic_status"] == "FALSE", "impact must not upgrade epistemic status")
    require(false_with_impact["causal_status"] != "CAUSAL_SUPPORT_ESTABLISHED", "temporal association must not become causation")
    original = {"event_id": "E1", "known_at": "2026-09-01T00:00:00Z", "supersedes_event_id": None}
    correction = {"event_id": "E2", "known_at": "2026-09-02T00:00:00Z", "supersedes_event_id": "E1"}
    validate_append_only_events([original, correction])
    require(original["event_id"] == "E1", "correction removed or mutated the original event")
    backward = {"event_id": "E0", "known_at": "2026-08-31T00:00:00Z", "supersedes_event_id": "E1"}
    try:
        validate_append_only_events([original, backward])
    except ValueError:
        pass
    else:
        raise AssertionError("backward supersession was accepted")
    require(correction["supersedes_event_id"] == "E1", "supersession direction changed")
    pass_message("INFORMATION_EVENT_DUAL_AXIS_TESTS")


if __name__ == "__main__": main()
