#!/usr/bin/env python3
"""Validation and deterministic sealing for the IREN listed-project draft."""

from __future__ import annotations

import hashlib
import json
from typing import Any

DEPENDENCIES = {"ISSUER_AUTHORED", "DERIVED", "PARTIALLY_DEPENDENT", "INDEPENDENT", "UNKNOWN"}
LIABILITIES = {"FILED", "FURNISHED", "UNFILED", "UNDETERMINED"}
ASSURANCE = {
    "AUDITED_FINANCIAL_STATEMENT", "REVIEWED_INTERIM", "UNAUDITED_DISCLOSURE",
    "PROMOTIONAL", "NOT_APPLICABLE", "UNKNOWN",
}
STAGES = {"D0", "D1", "D2", "D3", "D4a", "D4b"}
CLAIM_STATES = {"SUPPORTED_AS_ATTRIBUTED", "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE"}


class TrackerProtocolError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def seal(value: dict, field: str = "snapshot_sha256") -> dict:
    item = {key: val for key, val in value.items() if key != field}
    return {**item, field: digest(item)}


def validate_financial_attributes(attrs: dict) -> None:
    if attrs.get("source_dependency") not in DEPENDENCIES:
        raise TrackerProtocolError("invalid source dependency")
    if attrs.get("liability_regime") not in LIABILITIES:
        raise TrackerProtocolError("invalid liability regime")
    if attrs.get("assurance") not in ASSURANCE:
        raise TrackerProtocolError("invalid assurance")
    stages = attrs.get("disclosure_stages")
    if not isinstance(stages, list) or not set(stages) <= STAGES or len(stages) != len(set(stages)):
        raise TrackerProtocolError("invalid disclosure stages")
    if not attrs.get("assurance_scope"):
        raise TrackerProtocolError("assurance scope is required")


def validate_source(source: dict) -> None:
    required = {
        "source_id", "accession", "url", "issuer", "publication_date", "capture_date",
        "sha256", "access_status", "byte_capture_status", "dependency_class", "review_status",
        "record_sha256",
    }
    if not required <= source.keys():
        raise TrackerProtocolError(f"source missing fields: {source.get('source_id')}")
    if source["dependency_class"] not in DEPENDENCIES:
        raise TrackerProtocolError("invalid dependency class")
    if source["sha256"] is None and source["byte_capture_status"] != "RETRIEVAL_FAILED":
        raise TrackerProtocolError("null byte hash requires retrieval failure")
    if source["sha256"] is not None and source["byte_capture_status"] != "CAPTURED":
        raise TrackerProtocolError("byte hash requires captured bytes")
    expected = digest({key: val for key, val in source.items() if key != "record_sha256"})
    if source["record_sha256"] != expected:
        raise TrackerProtocolError("source record digest mismatch")


def validate_claim(claim: dict, source_ids: set[str]) -> None:
    if claim.get("state") not in CLAIM_STATES:
        raise TrackerProtocolError("invalid claim state")
    if not claim.get("source_ids") or not set(claim["source_ids"]) <= source_ids:
        raise TrackerProtocolError(f"unknown or empty source lineage: {claim.get('claim_id')}")
    validate_financial_attributes(claim["financial_attributes"])
    if claim["state"] == "NOT_ESTABLISHED_WITHIN_REVIEWED_SCOPE" and not claim.get("what_would_change_it"):
        raise TrackerProtocolError("unestablished claim needs closure condition")
    if claim.get("client_action") != "UNSPECIFIED":
        raise TrackerProtocolError("client action must remain unspecified")


def validate_tracker(tracker: dict, sources: list[dict]) -> None:
    if tracker.get("publication_status") != "INTERNAL_DRAFT_NOT_PUBLICLY_ACTIVATED":
        raise TrackerProtocolError("tracker is not internal draft")
    if tracker.get("case_state_changed") is not False:
        raise TrackerProtocolError("existing case state may not change")
    source_ids = {source["source_id"] for source in sources}
    if len(source_ids) != len(sources):
        raise TrackerProtocolError("duplicate source id")
    for source in sources:
        validate_source(source)
    claims = tracker.get("claims", [])
    claim_ids = {claim["claim_id"] for claim in claims}
    if len(claim_ids) != len(claims):
        raise TrackerProtocolError("duplicate claim id")
    for claim in claims:
        validate_claim(claim, source_ids)
    if tracker.get("snapshot_sha256") != digest({key: val for key, val in tracker.items() if key != "snapshot_sha256"}):
        raise TrackerProtocolError("tracker snapshot digest mismatch")


def append_event(events: list[dict], event: dict) -> list[dict]:
    draft = {key: value for key, value in event.items() if key != "event_sha256"}
    draft["sequence"] = len(events) + 1
    draft["previous_event_sha256"] = events[-1]["event_sha256"] if events else None
    sealed = {**draft, "event_sha256": digest(draft)}
    return [*events, sealed]


def validate_events(events: list[dict]) -> None:
    for index, event in enumerate(events):
        if event.get("sequence") != index + 1:
            raise TrackerProtocolError("event sequence mismatch")
        expected_previous = events[index - 1]["event_sha256"] if index else None
        if event.get("previous_event_sha256") != expected_previous:
            raise TrackerProtocolError("event chain mismatch")
        if event.get("event_sha256") != digest({key: value for key, value in event.items() if key != "event_sha256"}):
            raise TrackerProtocolError("event digest mismatch")
        if event.get("event_type") == "SUPERSESSION" and not event.get("supersedes_event_id"):
            raise TrackerProtocolError("supersession target required")
