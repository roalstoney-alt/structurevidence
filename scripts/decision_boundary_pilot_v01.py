#!/usr/bin/env python3
"""Append-only Decision Boundary Pilot protocol primitives (v0.1)."""

from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from typing import Any, Iterable


SCHEMA_VERSION = "se-decision-boundary-pilot-event-v0.1"
PROTOCOL_VERSION = "SE-DECISION-BOUNDARY-PILOT-v0.1"
EVENT_TYPES = (
    "BASELINE_FROZEN",
    "REVIEW_STARTED",
    "EVIDENCE_ADDED",
    "EVIDENCE_REJECTED",
    "CHALLENGE_RECEIVED",
    "RULE_CHECKED",
    "STOP_POINT_EMITTED",
    "CLIENT_DECISION_RECORDED",
    "OUTCOME_OBSERVED",
    "SUPERSEDED",
)
WORK_UNIT_FIELDS = (
    "researcher_minutes",
    "reviewer_touch_minutes",
    "source_acquisition_cost_minor_units",
    "review_rounds",
    "net_new_qualifying_sources",
    "clarifications",
    "challenge_submissions",
    "decision_condition_citations",
    "revisions_supersessions",
)
FORBIDDEN_PUBLIC_KEYS = {
    "client_name",
    "company_name",
    "customer_id",
    "email",
    "phone",
    "decision_owner",
    "internal_case_id",
    "d1_record_id",
}


class PilotProtocolError(ValueError):
    """Raised when a pilot record violates the frozen protocol."""


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _parse_datetime(value: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise PilotProtocolError(f"invalid RFC3339 date-time: {value!r}") from exc


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key
            yield from _walk_keys(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_keys(nested)


def validate_context(context: dict[str, Any]) -> None:
    required = {
        "protocol_version",
        "pilot_id",
        "classification",
        "real_customer_authorization",
        "human_scope_approval",
        "data_boundary",
        "case_state_changed",
        "evidence_records_changed",
        "second_real_human_review",
    }
    missing = sorted(required - context.keys())
    if missing:
        raise PilotProtocolError(f"missing context fields: {missing}")
    if context["protocol_version"] != PROTOCOL_VERSION:
        raise PilotProtocolError("unexpected protocol version")
    if context["case_state_changed"] or context["evidence_records_changed"]:
        raise PilotProtocolError("a pilot cannot change case state or evidence records")
    if context["second_real_human_review"] != "UNSUPPORTED":
        raise PilotProtocolError("unsupported reviewer status must remain truthful")

    classification = context["classification"]
    if classification == "PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT":
        if context["real_customer_authorization"] != "NOT_GRANTED":
            raise PilotProtocolError("a public illustration cannot imply customer authorization")
        if context["human_scope_approval"] != "NOT_APPLICABLE_TEST_FIXTURE":
            raise PilotProtocolError("fixture scope boundary is inconsistent")
        if context["data_boundary"] != "PUBLIC_TEST_FIXTURE_ONLY":
            raise PilotProtocolError("fixture data must remain public synthetic data")
    elif classification == "REAL_CUSTOMER_PILOT":
        authorization = context.get("authorization") or {}
        if context["real_customer_authorization"] != "INDEPENDENTLY_AUTHORIZED":
            raise PilotProtocolError("real customer pilot requires independent authorization")
        if context["human_scope_approval"] != "APPROVED":
            raise PilotProtocolError("real customer pilot requires human scope approval")
        for key in ("written_opt_in_reference", "scope_approval_reference"):
            if not isinstance(authorization.get(key), str) or not authorization[key].strip():
                raise PilotProtocolError(f"real customer pilot requires {key}")
        if authorization.get("private_storage_confirmed") is not True:
            raise PilotProtocolError("real customer data requires confirmed private storage")
        if context["data_boundary"] != "PRIVATE_CUSTOMER_RECORD_NOT_PUBLIC_EXPORT":
            raise PilotProtocolError("real customer data cannot use the public fixture boundary")
    else:
        raise PilotProtocolError(f"unsupported pilot classification: {classification!r}")

    if context["data_boundary"] == "PUBLIC_TEST_FIXTURE_ONLY":
        exposed = sorted(set(_walk_keys(context)) & FORBIDDEN_PUBLIC_KEYS)
        if exposed:
            raise PilotProtocolError(f"public fixture contains forbidden identity fields: {exposed}")


def empty_work_units() -> dict[str, int | str]:
    return {**{name: 0 for name in WORK_UNIT_FIELDS}, "currency": "USD"}


def validate_work_units(value: dict[str, Any]) -> None:
    expected = set(WORK_UNIT_FIELDS) | {"currency"}
    if set(value) != expected:
        raise PilotProtocolError("work_units must declare the complete frozen metric set")
    if value["currency"] != "USD":
        raise PilotProtocolError("fixture cost currency must be explicit and stable")
    for name in WORK_UNIT_FIELDS:
        metric = value[name]
        if not isinstance(metric, int) or isinstance(metric, bool) or metric < 0:
            raise PilotProtocolError(f"work unit {name} must be a non-negative integer")


def seal_event(event: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(event)
    sealed.pop("event_sha256", None)
    sealed["event_sha256"] = sha256(sealed)
    return sealed


def validate_event(event: dict[str, Any], previous: dict[str, Any] | None, context: dict[str, Any]) -> None:
    required = {
        "schema_version", "protocol_version", "pilot_id", "event_id", "sequence",
        "event_type", "occurred_at", "recorded_at", "data_classification",
        "previous_event_sha256", "payload", "event_sha256",
    }
    if set(event) != required:
        raise PilotProtocolError(f"event fields differ from frozen schema: {sorted(set(event) ^ required)}")
    if event["schema_version"] != SCHEMA_VERSION or event["protocol_version"] != PROTOCOL_VERSION:
        raise PilotProtocolError("event protocol version mismatch")
    if event["pilot_id"] != context["pilot_id"]:
        raise PilotProtocolError("event pilot_id mismatch")
    if event["event_type"] not in EVENT_TYPES:
        raise PilotProtocolError(f"unsupported event type: {event['event_type']}")
    _parse_datetime(event["occurred_at"])
    _parse_datetime(event["recorded_at"])
    expected_sequence = 1 if previous is None else previous["sequence"] + 1
    expected_previous = None if previous is None else previous["event_sha256"]
    if event["sequence"] != expected_sequence or event["previous_event_sha256"] != expected_previous:
        raise PilotProtocolError("append-only sequence or hash-chain mismatch")
    if previous is None and event["event_type"] != "BASELINE_FROZEN":
        raise PilotProtocolError("the first event must freeze the baseline")
    if event["data_classification"] != context["data_boundary"]:
        raise PilotProtocolError("event crosses the declared data boundary")
    if seal_event(event)["event_sha256"] != event["event_sha256"]:
        raise PilotProtocolError("event hash mismatch")
    if context["data_boundary"] == "PUBLIC_TEST_FIXTURE_ONLY":
        exposed = sorted(set(_walk_keys(event)) & FORBIDDEN_PUBLIC_KEYS)
        if exposed:
            raise PilotProtocolError(f"public event contains forbidden identity fields: {exposed}")

    payload = event["payload"]
    validate_work_units(payload.get("work_units", {}))
    if event["event_type"] == "BASELINE_FROZEN":
        required_baseline = {
            "decision_question", "decision_event", "deadline_status", "private_owner_status",
            "scoped_source_ids", "qualifying_rule_ids", "evidence_cutoff", "last_reviewed_at",
            "unknowns", "competing_hypotheses", "record_freeze_hash", "baseline_measurement",
        }
        if not required_baseline <= payload.keys():
            raise PilotProtocolError("baseline event is incomplete")
        measurement = payload["baseline_measurement"]
        if measurement.get("status") != "SYNTHETIC_COMPARATOR_ONLY":
            raise PilotProtocolError("fixture baseline must not be presented as observed")
        frozen_scope = {key: value for key, value in payload.items() if key not in {"record_freeze_hash", "work_units"}}
        if payload["record_freeze_hash"] != sha256(frozen_scope):
            raise PilotProtocolError("baseline freeze hash does not seal the declared T0 scope")
    elif event["event_type"] == "CLIENT_DECISION_RECORDED":
        if payload.get("decision_source") != "CLIENT_SUPPLIED":
            raise PilotProtocolError("client decisions may only be client supplied")
        if context["classification"] != "REAL_CUSTOMER_PILOT":
            raise PilotProtocolError("a fixture cannot record a real client decision")
    elif event["event_type"] == "OUTCOME_OBSERVED":
        if payload.get("observation_status") != "INDEPENDENTLY_OBSERVED_AND_PERMITTED":
            raise PilotProtocolError("outcome requires independent observation and scope permission")
        if context["classification"] != "REAL_CUSTOMER_PILOT":
            raise PilotProtocolError("a fixture cannot record a real outcome")
    elif event["event_type"] == "SUPERSEDED":
        target = payload.get("supersedes_event_id")
        if previous is None or not isinstance(target, str):
            raise PilotProtocolError("supersession must reference an earlier event")


def validate_events(events: list[dict[str, Any]], context: dict[str, Any]) -> None:
    validate_context(context)
    if not events:
        raise PilotProtocolError("event ledger cannot be empty")
    seen: set[str] = set()
    prior_ids: set[str] = set()
    previous = None
    for event in events:
        if event["event_id"] in seen:
            raise PilotProtocolError("event_id must be unique")
        validate_event(event, previous, context)
        if event["event_type"] == "SUPERSEDED" and event["payload"]["supersedes_event_id"] not in prior_ids:
            raise PilotProtocolError("supersession target must already exist")
        seen.add(event["event_id"])
        prior_ids.add(event["event_id"])
        previous = event


def append_event(events: list[dict[str, Any]], draft: dict[str, Any], context: dict[str, Any]) -> list[dict[str, Any]]:
    """Append once; an exact replay is idempotent and a conflicting replay fails."""
    validate_context(context)
    existing = next((item for item in events if item["event_id"] == draft["event_id"]), None)
    if existing is not None:
        replay = copy.deepcopy(draft)
        replay.update({
            "sequence": existing["sequence"],
            "previous_event_sha256": existing["previous_event_sha256"],
        })
        replay = seal_event(replay)
        if replay != existing:
            raise PilotProtocolError("event_id replay conflicts with immutable event")
        return copy.deepcopy(events)

    event = copy.deepcopy(draft)
    event["sequence"] = len(events) + 1
    event["previous_event_sha256"] = events[-1]["event_sha256"] if events else None
    event = seal_event(event)
    validate_event(event, events[-1] if events else None, context)
    result = copy.deepcopy(events) + [event]
    validate_events(result, context)
    return result


def aggregate_work_units(events: list[dict[str, Any]]) -> dict[str, int | str]:
    totals = empty_work_units()
    for event in events:
        units = event["payload"]["work_units"]
        for name in WORK_UNIT_FIELDS:
            totals[name] += units[name]
    return totals


def build_report(context: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    validate_events(events, context)
    baseline = events[0]["payload"]["baseline_measurement"]
    telemetry = aggregate_work_units(events)
    simulation_difference = {
        "classification": "TEST_FIXTURE_ONLY_NOT_EVIDENCE",
        "fixture_time_difference_minutes": (
            telemetry["researcher_minutes"] + telemetry["reviewer_touch_minutes"]
            - baseline["researcher_minutes"] - baseline["reviewer_touch_minutes"]
        ),
        "fixture_cost_difference_minor_units": (
            telemetry["source_acquisition_cost_minor_units"]
            - baseline["source_acquisition_cost_minor_units"]
        ),
        "interpretation": "Arithmetic for deterministic test coverage only; not a customer result, causal estimate, saving, or ROI claim.",
    }
    report: dict[str, Any] = {
        "schema_version": "se-decision-boundary-pilot-report-v0.1",
        "protocol_version": PROTOCOL_VERSION,
        "project": "SE-DUAL-SITE-UPGRADE-002",
        "phase": "E",
        "pilot_id": context["pilot_id"],
        "classification": context["classification"],
        "event_count": len(events),
        "event_chain_head_sha256": events[-1]["event_sha256"],
        "event_ledger_sha256": sha256(events),
        "observed_telemetry": {
            "status": "NO_REAL_CUSTOMER_OBSERVATIONS",
            "values": None,
        },
        "simulation_telemetry": telemetry,
        "baseline_comparison": {
            "status": "INSUFFICIENT_DATA",
            "reason": "No independently authorized customer pilot with an actual comparable baseline and outcome has been recorded.",
            "observed_before": None,
            "observed_after": None,
            "causal_attribution": "NOT_ESTABLISHED",
            "roi_status": "NOT_EVALUATED",
        },
        "simulation_diagnostics": simulation_difference,
        "missing_data": [
            "INDEPENDENT_REAL_CUSTOMER_AUTHORIZATION",
            "ACTUAL_COMPARABLE_BASELINE",
            "CLIENT_SUPPLIED_DECISION",
            "INDEPENDENTLY_OBSERVED_PERMITTED_OUTCOME",
            "CAUSAL_COUNTERFACTUAL",
        ],
        "causal_limitations": [
            "Synthetic work units cannot establish customer time or cost effects.",
            "A before/after difference alone would not establish causation.",
            "No avoided-loss value is estimated.",
            "StructEvidence does not convert an evidence boundary into a client recommendation.",
        ],
        "preserved_boundaries": {
            "case_state_changed": False,
            "evidence_records_changed": False,
            "client_decision_recorded": False,
            "outcome_observed": False,
            "second_real_human_review": "UNSUPPORTED",
            "production_deployed": False,
        },
        "report_sha256": "",
    }
    report["report_sha256"] = sha256({key: value for key, value in report.items() if key != "report_sha256"})
    return report


def validate_report(report: dict[str, Any], context: dict[str, Any], events: list[dict[str, Any]]) -> None:
    expected = build_report(context, events)
    if report != expected:
        raise PilotProtocolError("report is not the deterministic projection of the event ledger")
    if report["baseline_comparison"]["status"] != "INSUFFICIENT_DATA":
        raise PilotProtocolError("fixture cannot claim an observed baseline comparison")
