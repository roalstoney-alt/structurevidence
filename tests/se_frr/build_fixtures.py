#!/usr/bin/env python3
"""Build deterministic, synthetic-only SE-FRR protocol fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from se_frr_protocol import PROTOCOL_VERSION, finalize_change, finalize_evidence, finalize_state  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / "fixtures"
RECORDED = "2026-09-25T12:00:00Z"
SUBJECT = "SE-SUBJ-000001"


def prov(recorded_at: str, supersedes=None, superseded_by=None):
    return {
        "repository": "StructEvidence synthetic protocol fixtures",
        "commit_sha": None,
        "source_object": "SYNTHETIC_TEST_FIXTURE",
        "created_by": "SE-FRR fixture builder",
        "method_version": PROTOCOL_VERSION,
        "recorded_at": recorded_at,
        "supersedes": supersedes,
        "superseded_by": superseded_by,
    }


def write(kind, object_id, value):
    target = FIXTURES / kind / f"{object_id}.json"
    target.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def evidence(evidence_id, status, claim, observed_at, counter_to=None, supersedes=None, superseded_by=None):
    item = {
        "schema_version": "SE_EVIDENCE_v0.1", "evidence_id": evidence_id, "subject_id": SUBJECT,
        "published_at": "2026-09-20T08:00:00Z", "observed_at": observed_at,
        "recorded_at": RECORDED, "effective_at": observed_at,
        "source": {"name": "Synthetic protocol source", "url": None, "type": "SYNTHETIC", "publisher": None,
                   "snapshot_ref": "SYNTHETIC_TEST_FIXTURE", "retrieved_at": RECORDED},
        "raw_reference": f"synthetic://{evidence_id}", "normalized_claim": claim,
        "evidence_type": "SYNTHETIC_PROTOCOL_EVIDENCE",
        "review": {"status": status, "reason": f"Synthetic {status.lower()} fixture.", "reviewed_at": RECORDED, "reviewed_by": "fixture-reviewer"},
        "counter_to": counter_to or [], "research_class": "SYNTHETIC_TEST_ONLY", "visibility": "PUBLIC",
        "content_hash": "0" * 64, "provenance": prov(RECORDED, supersedes, superseded_by),
    }
    return finalize_evidence(item)


def main():
    subject = {
        "schema_version": "SE_SUBJECT_v0.1", "subject_id": SUBJECT, "canonical_name": "Synthetic Industrial Path A",
        "subject_type": "SYNTHETIC_TECHNICAL_PATH", "aliases": ["Fixture Subject A"], "industry": "Synthetic",
        "geography": ["TEST_ONLY"], "description": "Non-production fixture for temporal-state protocol verification.",
        "created_at": "2026-09-25T10:00:00Z", "created_by": "SE-FRR fixture builder", "visibility": "PUBLIC",
        "status": "WATCH", "tags": ["SYNTHETIC", "TEST_ONLY"], "provenance": prov("2026-09-25T10:00:00Z"),
    }
    write("subjects", SUBJECT, subject)

    ev1 = evidence("SE-EV-20260925-000001", "ACCEPTED", "A legacy dependency is observed.", "2026-09-21T09:00:00Z")
    ev2 = evidence("SE-EV-20260925-000002", "COUNTER", "Deployment is not yet demonstrated.", "2026-09-22T09:00:00Z", [ev1["evidence_id"]])
    ev3 = evidence("SE-EV-20260925-000003", "REJECTED", "An unattributed claim asserts full deployment.", "2026-09-22T10:00:00Z")
    ev4 = evidence("SE-EV-20260925-000004", "ACCEPTED", "A technically credible alternative path is demonstrated.", "2026-09-24T09:00:00Z")
    ev5 = evidence("SE-EV-20260925-000005", "SUPERSEDED", "An older observation is retained after correction.", "2026-09-20T09:00:00Z", superseded_by=ev4["evidence_id"])
    for item in [ev1, ev2, ev3, ev4, ev5]:
        write("evidence", item["evidence_id"], item)

    change_id = "SE-CHG-20260925-000001"
    branch_a = "SE-BR-20260925-000001"
    branch_b = "SE-BR-20260925-000002"
    st1_raw = {
        "schema_version": "SE_STATE_v0.1", "state_id": "SE-ST-20260925-000001", "subject_id": SUBJECT,
        "observed_at": "2026-09-22T12:00:00Z", "recorded_at": "2026-09-25T12:00:00Z", "state_code": "WATCH",
        "previous_state_id": None, "previous_state_hash": None, "current_dependency": "Synthetic legacy path",
        "constraints": ["Field operation is unverified"], "alternative_paths": [], "migration_readiness": "OBSERVATION_ONLY",
        "field_deployment_status": "NOT_ESTABLISHED", "accepted_evidence_ids": [ev1["evidence_id"]],
        "rejected_evidence_ids": [ev3["evidence_id"]], "counter_evidence_ids": [ev2["evidence_id"]], "unresolved_evidence_ids": [],
        "unknowns": ["Operating history"], "confidence_boundary": {"supported": ["Legacy dependency observed"], "unsupported": ["Field deployment"], "unknown": ["Operating history"]},
        "branch_ids": [], "state_changed": False, "change_event_id": None, "state_hash": "0" * 64, "chain_hash": "0" * 64,
        "method_version": PROTOCOL_VERSION, "visibility": "PUBLIC", "provenance": prov("2026-09-25T12:00:00Z"),
    }
    st1 = finalize_state(st1_raw)
    st2_raw = {
        **st1_raw, "state_id": "SE-ST-20260925-000002", "observed_at": "2026-09-24T12:00:00Z", "recorded_at": "2026-09-25T13:00:00Z",
        "state_code": "ALTERNATIVE_PATH_IDENTIFIED", "previous_state_id": st1["state_id"], "previous_state_hash": st1["state_hash"],
        "alternative_paths": ["Synthetic alternative path"], "migration_readiness": "TECHNICALLY_CREDIBLE",
        "accepted_evidence_ids": [ev1["evidence_id"], ev4["evidence_id"]], "branch_ids": [branch_a, branch_b],
        "state_changed": True, "change_event_id": change_id,
        "confidence_boundary": {"supported": ["Legacy dependency observed", "Alternative path demonstrated"], "unsupported": ["Field deployment"], "unknown": ["Operating history"]},
        "provenance": prov("2026-09-25T13:00:00Z", supersedes=st1["state_id"]),
    }
    st2 = finalize_state(st2_raw, st1["chain_hash"])
    write("states", st1["state_id"], st1)
    write("states", st2["state_id"], st2)

    change = finalize_change({
        "schema_version": "SE_CHANGE_v0.1", "change_id": change_id, "subject_id": SUBJECT,
        "previous_state_id": st1["state_id"], "previous_state_hash": st1["state_hash"], "new_state_id": st2["state_id"], "new_state_hash": st2["state_hash"],
        "detected_at": "2026-09-24T12:00:00Z", "recorded_at": "2026-09-25T13:00:00Z", "trigger_evidence_ids": [ev4["evidence_id"]],
        "unknowns_resolved": [], "unknowns_added": [], "counter_evidence_added": [], "counter_evidence_removed": [],
        "change_summary": "A credible alternative path was identified; deployment remains unverified.", "materiality": "MATERIAL", "visibility": "PUBLIC", "change_hash": "0" * 64,
        "provenance": prov("2026-09-25T13:00:00Z"),
    })
    write("changes", change_id, change)

    for branch_id, name, status, support, contradict in [
        (branch_a, "Qualification path", "STRENGTHENING", [ev4["evidence_id"]], [ev2["evidence_id"]]),
        (branch_b, "Incumbent persists", "POSSIBLE", [ev2["evidence_id"]], [ev4["evidence_id"]]),
    ]:
        write("branches", branch_id, {
            "schema_version": "SE_BRANCH_v0.1", "branch_id": branch_id, "state_id": st2["state_id"], "subject_id": SUBJECT,
            "created_at": "2026-09-25T13:00:00Z", "name": name, "description": f"Synthetic branch: {name}.", "status": status,
            "required_conditions": ["A later observable must be recorded"], "supporting_evidence_ids": support, "contradicting_evidence_ids": contradict,
            "strengthening_signals": ["Independent operational evidence"], "weakening_signals": ["Qualification failure"],
            "kill_conditions": ["Contradictory verified outcome"], "realization_evidence_ids": [], "visibility": "PUBLIC", "provenance": prov("2026-09-25T13:00:00Z"),
        })

    request_id = "SE-REQ-20260925-000001"
    write("requests", request_id, {
        "schema_version": "SE_REQUEST_v0.1", "request_id": request_id, "submitted_at": "2026-09-25T14:00:00Z",
        "requester_ref": "PRIVATE_FIXTURE_REQUESTER", "subject_text": "Synthetic Industrial Path A", "linked_subject_id": SUBJECT,
        "question": "Should the synthetic alternative be tested?", "decision_context": "Private fixture decision context.", "urgency": "TEST_ONLY",
        "visibility": "CUSTOMER_PRIVATE", "payment_status": "NOT_REQUIRED", "research_status": "DELIVERED", "linked_state_id": st2["state_id"],
        "outcome_status": "REPORTED", "provenance": prov("2026-09-25T14:00:00Z"),
    })
    write("challenges", "SE-CLG-20260925-000001", {
        "schema_version": "SE_CHALLENGE_v0.1", "challenge_id": "SE-CLG-20260925-000001", "submitted_at": "2026-09-25T14:30:00Z",
        "subject_id": SUBJECT, "state_id": st2["state_id"], "challenger_ref": "SYNTHETIC_CHALLENGER", "claim": "The accepted signal is not deployment evidence.",
        "submitted_evidence_refs": ["synthetic://challenge-1"], "review_status": "ACCEPTED", "review_reason": "Boundary retained.",
        "resulting_evidence_ids": [ev2["evidence_id"]], "resulting_state_id": st2["state_id"], "visibility": "FOUNDING_MEMBER", "provenance": prov("2026-09-25T14:30:00Z"),
    })
    for outcome_id, visibility, authorized, result in [
        ("SE-OUT-20260925-000001", "CUSTOMER_PRIVATE", False, "Private test result retained in protected plane."),
        ("SE-OUT-20260925-000002", "PUBLIC", True, "Authorized synthetic result may enter the public projection."),
    ]:
        write("outcomes", outcome_id, {
            "schema_version": "SE_OUTCOME_v0.1", "outcome_id": outcome_id, "request_id": request_id, "subject_id": SUBJECT, "state_id_used": st2["state_id"],
            "reported_at": "2026-09-26T09:00:00Z", "action": "Ran a synthetic bench test.", "action_at": "2026-09-26T08:00:00Z", "reported_result": result,
            "verification_status": "VERIFIED", "supporting_evidence_refs": [ev4["evidence_id"]], "commercial_result": None,
            "technical_result": "Synthetic fixture result.", "authorization_for_public_use": authorized, "visibility": visibility,
            "created_at": "2026-09-26T09:30:00Z", "provenance": prov("2026-09-26T09:30:00Z"),
        })


if __name__ == "__main__":
    main()
