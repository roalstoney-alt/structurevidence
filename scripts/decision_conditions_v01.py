#!/usr/bin/env python3
"""Deterministic, public Decision Conditions derived from Phase B artifacts.

The module is intentionally pure: it does not fetch sources, alter evidence
records, or infer a customer action.  Callers provide the already-reviewed
public artifacts and receive a sealed export package.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import unquote, urlsplit

from source_dependency_v01 import current_rows, load_rules, validate_registry


SCHEMA_VERSION = "se-decision-conditions-package-v0.1"
PROTOCOL_VERSION = "SE-DECISION-CONDITIONS-v0.1"
BASELINE_MAIN_SHA = "bbced95da00ed259e942aa63ebd89d93f70c54a0"
CASE_ID = "CML-PDRE-001"
PUBLIC_BASE = "https://structurevidence.org/cases/800vdc/decision-conditions"
GAP_IDS = ("OEG-CML-001", "OEG-CML-002")
CONDITION_IDS = {
    "OEG-CML-001": "SE-DC-CML-PDRE-001-OEG-CML-001-v0.1",
    "OEG-CML-002": "SE-DC-CML-PDRE-001-OEG-CML-002-v0.1",
}
DECISION_TYPES = {
    "OEG-CML-001": "ILLUSTRATIVE_TECHNICAL_QUALIFICATION",
    "OEG-CML-002": "ILLUSTRATIVE_DEPLOYMENT_REPLICATION_REVIEW",
}
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MARKUP_RE = re.compile(r"<\s*/?\s*[a-z!][^>]*>|javascript\s*:|\bon\w+\s*=", re.I)


class DecisionConditionError(ValueError):
    """Raised when a safe deterministic export cannot be produced."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def file_digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _parse_time(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise DecisionConditionError(f"{field} must be a non-empty ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DecisionConditionError(f"{field} is not ISO-8601") from exc
    if parsed.tzinfo is None:
        raise DecisionConditionError(f"{field} must include a timezone")
    return parsed


def _safe(value: Any, path: str = "document") -> None:
    if isinstance(value, str):
        decoded = unquote(value)
        if CONTROL_RE.search(value) or MARKUP_RE.search(value) or MARKUP_RE.search(decoded):
            raise DecisionConditionError(f"unsafe content at {path}")
    elif isinstance(value, dict):
        for key, child in value.items():
            _safe(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _safe(child, f"{path}[{index}]")


def _public_http_url(value: Any, field: str) -> None:
    if not isinstance(value, str):
        raise DecisionConditionError(f"{field} must be a URL")
    parts = urlsplit(value)
    if parts.scheme not in {"http", "https"} or not parts.hostname or parts.username or parts.password:
        raise DecisionConditionError(f"{field} must be a public http(s) URL without credentials")
    _safe(value, field)


def validate_inputs(
    view: dict[str, Any],
    matrix: dict[str, Any],
    registry: dict[str, Any],
    rules_document: dict[str, Any],
) -> None:
    """Reject silent ambiguity before producing an export."""
    validate_registry(registry, rules_document)
    rules = load_rules(rules_document)
    if view.get("case_id") != CASE_ID or matrix.get("case_id") != CASE_ID:
        raise DecisionConditionError("Phase C accepts only the declared 800VDC case")
    by_gap = {rule["gap_id"]: rule for rule in rules.values()}
    if set(by_gap) != set(GAP_IDS):
        raise DecisionConditionError("active rules must contain exactly the two declared gaps")
    metrics = view.get("metrics")
    if not isinstance(metrics, dict) or set(metrics) != set(GAP_IDS):
        raise DecisionConditionError("source view is missing a declared gap")
    for field in ("evidence_cutoff", "last_source_check_at", "reviewed_at"):
        _parse_time(view.get(field), field)
    if _parse_time(view["evidence_cutoff"], "evidence_cutoff") > _parse_time(view["reviewed_at"], "reviewed_at"):
        raise DecisionConditionError("evidence cutoff cannot be after review time")
    if _parse_time(view["last_source_check_at"], "last_source_check_at") > _parse_time(view["reviewed_at"], "reviewed_at"):
        raise DecisionConditionError("last source check cannot be after review time")
    active = current_rows(registry)
    expected_active = len(view.get("sources", [])) * len(GAP_IDS)
    if len(active) != expected_active:
        raise DecisionConditionError("active source rows do not match the bounded source view")
    for row in active:
        if row["gap_id"] not in GAP_IDS:
            raise DecisionConditionError("active registry contains an undeclared gap")
        disagreement = row.get("reviewer_disagreement", {})
        if disagreement.get("detected") and disagreement.get("resolution_status") not in {
            "UNRESOLVED", "RESOLVED"
        }:
            raise DecisionConditionError("reviewer conflict must be explicitly resolved or preserved as UNRESOLVED")
    review = view.get("review_policy", {})
    if review.get("second_real_human_review") != "UNSUPPORTED":
        raise DecisionConditionError("second real human review status must remain explicit")
    dispute = view.get("chindata_e4_consistency_review", {})
    if dispute.get("adjudication_status") != "UNRESOLVED":
        raise DecisionConditionError("Chindata E3/E4 dispute must remain UNRESOLVED")
    _safe(view, "source_view")
    _safe(matrix, "review_matrix")


def _source_entry(row: dict[str, Any]) -> dict[str, Any]:
    source = row["immutable_source"]
    _public_http_url(source["url"], "immutable_source.url")
    return {
        "source_row_id": row["source_row_id"],
        "source_record_hash": row["record_hash"],
        "title": source["title"],
        "url": source["url"],
        "capture_sha256": source["capture"]["sha256"],
        "originator_id": row["originator_id"],
        "originator_role": row["originator_role"],
        "dependency_class": row["dependency_class"],
        "originating_evidence_lineage": copy.deepcopy(row["originating_evidence_lineage"]),
        "evidence_level": row["evidence_level"],
        "evidence_facets": copy.deepcopy(row["evidence_facets"]),
        "qualification_status": row["qualification_status"],
        "qualification_reason": row["qualification_reason"],
        "source_access_status": row["source_access_status"],
        "supersedes_source_row_id": row["supersession"]["predecessor_source_row_id"],
    }


def _access_limit(row: dict[str, Any]) -> dict[str, Any]:
    source = row["immutable_source"]
    return {
        "source_row_id": row["source_row_id"],
        "source_access_status": row["source_access_status"],
        "capture_failure_or_limit": source["capture"]["failure_reason"],
        "blocked_sources_or_limits": copy.deepcopy(row["search_scope"]["blocked_sources"]),
    }


def _oeg_cml_001_closure_from_rule(rule: dict[str, Any]) -> str:
    """Render OEG-CML-001 only from its active rule, never another gap's prose."""
    if rule.get("gap_id") != "OEG-CML-001":
        raise DecisionConditionError("OEG-CML-001 closure received a cross-gap rule")
    dependencies = ", ".join(rule["permitted_dependency_classes"])
    roles = ", ".join(rule["permitted_originator_roles"])
    facets = ", ".join(rule["required_evidence_facets"])
    return (
        "A source row qualifies only if its evidence level is "
        f"{rule['minimum_evidence_level']} or higher; its dependency class is one of {dependencies}; "
        f"its originator role is one of {roles}; and it contains every required evidence facet: {facets}."
    )


def _condition(
    gap_id: str,
    view: dict[str, Any],
    matrix: dict[str, Any],
    active_rows: list[dict[str, Any]],
    rules_by_gap: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    rows = sorted((row for row in active_rows if row["gap_id"] == gap_id), key=lambda row: row["source_row_id"])
    if not rows:
        raise DecisionConditionError(f"no active source rows for {gap_id}")
    rule = rules_by_gap[gap_id]
    qualifying = [_source_entry(row) for row in rows if row["qualification_status"] == "QUALIFIED"]
    nonqualifying = [_source_entry(row) for row in rows if row["qualification_status"] != "QUALIFIED"]
    unavailable = [_source_entry(row) for row in rows if row["source_access_status"] in {"UNAVAILABLE", "CORRUPT", "UNKNOWN"}]
    predecessor_links = [
        {
            "active_source_row_id": row["source_row_id"],
            "predecessor_source_row_id": row["supersession"]["predecessor_source_row_id"],
        }
        for row in rows
        if row["supersession"]["predecessor_source_row_id"]
    ]
    metric = view["metrics"][gap_id]
    question = view["decision_boundary"]["scoped_questions"][gap_id]
    closure = (
        _oeg_cml_001_closure_from_rule(rule)
        if gap_id == "OEG-CML-001"
        else view["decision_boundary"]["closure_conditions"][gap_id]
    )
    condition = {
        "decision_condition_id": CONDITION_IDS[gap_id],
        "version": "v0.1",
        "previous_snapshot_sha256": None,
        "supersedes_decision_condition_id": None,
        "stable_urls": {
            "html": f"{PUBLIC_BASE}/#{CONDITION_IDS[gap_id]}",
            "json": f"{PUBLIC_BASE}-v0.1.json",
            "markdown": f"{PUBLIC_BASE}-v0.1.md#{CONDITION_IDS[gap_id].lower()}",
            "gap": view["challenge_routes"][gap_id]["url"],
        },
        "case_id": CASE_ID,
        "gap_id": gap_id,
        "claim_id": rule["claim_id"],
        "decision_type": DECISION_TYPES[gap_id],
        "decision_context_status": "PUBLIC_ILLUSTRATION_NOT_CLIENT_ADOPTION",
        "scope": {
            "question": question,
            "bounded_sample": metric["reviewed_urls"]["scope"]["sample"],
            "reviewed_url_count": metric["reviewed_urls"]["value"],
            "distinct_lineage_count": metric["distinct_evidence_lineages"]["value"],
            "authority_status": view["decision_boundary"]["authority_status"],
        },
        "current_evidence_state": {
            "case_state": view["case_state"],
            "case_state_as_of": view["case_state_as_of"],
            "state_changed_by_export": False,
            "interpretation": "A time-bounded reviewed state, not authoritative truth and not a client action.",
        },
        "time_boundary": {
            "evidence_cutoff": view["evidence_cutoff"],
            "last_source_check_at": view["last_source_check_at"],
            "reviewed_at": view["reviewed_at"],
        },
        "source_evidence_rule": {
            "qualification_rule_id": rule["qualification_rule_id"],
            "rubric_version": rule["rubric_version"],
            "minimum_evidence_level": rule["minimum_evidence_level"],
            "permitted_dependency_classes": copy.deepcopy(rule["permitted_dependency_classes"]),
            "permitted_originator_roles": copy.deepcopy(rule["permitted_originator_roles"]),
            "required_evidence_facets": copy.deepcopy(rule["required_evidence_facets"]),
            "rule_text": rule["rule_text"],
            "exact_closure_test": closure,
            "acceptable_source_types": {
                "originator_roles": copy.deepcopy(rule["permitted_originator_roles"]),
                "dependency_classes": copy.deepcopy(rule["permitted_dependency_classes"]),
                "minimum_level": rule["minimum_evidence_level"],
                "all_required_facets_must_be_present": True,
            },
        },
        "source_evidence_result": {
            "qualification_outcome": "QUALIFYING_EVIDENCE_PRESENT" if qualifying else "NOT_QUALIFIED_WITHIN_BOUNDED_REVIEW",
            "qualifying_evidence_present": bool(qualifying),
            "qualifying_evidence": qualifying,
            "nonqualifying_evidence": nonqualifying,
            "qualifying_counterevidence": [],
            "counterevidence_status": "NO_QUALIFYING_CONTRADICTION_ESTABLISHED_WITHIN_BOUNDED_PACKET",
            "inaccessible_sources": unavailable,
            "source_access_limitations": [_access_limit(row) for row in rows],
            "search_scope_limits": sorted({row["search_scope"]["exclusion_scope"] for row in rows}),
            "zero_interpretation": view["zero_interpretation"],
        },
        "preserved_uncertainty": {
            "unknown": [view["decision_boundary"]["current_state"]["unknown"]],
            "unresolved": [{
                "issue": "CHINDATA_E3_E4",
                "status": "UNRESOLVED",
                "active_level": view["chindata_e4_consistency_review"]["active_level"],
                "caveat": view["chindata_e4_consistency_review"]["active_level_caveat"],
            }],
            "unsupported": [{
                "capability": "SECOND_REAL_HUMAN_REVIEW",
                "status": "UNSUPPORTED",
                "capability_status": view["review_policy"]["second_review_capability_status"],
                "effect": "NO_EVIDENCE_OR_CASE_STATE_CHANGE",
            }],
        },
        "client_action_condition": {
            "ownership": "CLIENT_DEFINED",
            "selected_action": "UNSPECIFIED",
            "allowed_client_vocabulary": ["PROCEED", "HOLD", "EXIT", "REVIEW"],
            "decision_trigger": "UNSPECIFIED",
            "review_date": "UNSPECIFIED",
            "fallback": "UNSPECIFIED",
            "exposure_threshold": "UNSPECIFIED",
            "status": "NO_CLIENT_DECISION_RECORDED",
            "separation_from_evidence_rule": "A source qualification result never selects a client action.",
        },
        "source_supersession_links": predecessor_links,
        "challenge_boundary": {
            "url": view["challenge_routes"][gap_id]["url"],
            "submission_effect": view["challenge_routes"][gap_id]["effect"],
            "automatic_condition_or_state_change": False,
        },
        "not_a_decision_recommendation": "StructEvidence reports a time-bounded evidence condition. It does not recommend an investment, purchase, architecture, deployment, rejection, or client action.",
    }
    condition["record_sha256"] = digest(condition)
    return condition


def build_package(
    view: dict[str, Any],
    matrix: dict[str, Any],
    registry: dict[str, Any],
    rules_document: dict[str, Any],
    provenance: dict[str, str],
) -> dict[str, Any]:
    validate_inputs(view, matrix, registry, rules_document)
    rules_by_gap = {rule["gap_id"]: rule for rule in load_rules(rules_document).values()}
    active_rows = current_rows(registry)
    package = {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "project": "SE-DUAL-SITE-UPGRADE-002",
        "phase": "C",
        "baseline_main_sha": BASELINE_MAIN_SHA,
        "generated_from_review_time": view["reviewed_at"],
        "content_hash_algorithm": "SHA-256 over RFC-8785-style sorted compact JSON; snapshot_sha256 excluded from its own input",
        "public_capability_status": "ILLUSTRATIVE_PUBLIC_EXPORT",
        "commercial_integration_status": "PROPOSED_NOT_LIVE",
        "conditions": [
            _condition(gap_id, view, matrix, active_rows, rules_by_gap)
            for gap_id in GAP_IDS
        ],
        "provenance": copy.deepcopy(provenance),
        "append_only_versioning": {
            "version": "v0.1",
            "previous_snapshot_sha256": None,
            "update_policy": "Future changes create a new version that cites this snapshot digest; this export is never overwritten in place.",
        },
        "case_state_changed": False,
        "client_decision_recorded": False,
    }
    package["snapshot_sha256"] = digest(package)
    validate_package(package)
    return package


def validate_package(package: dict[str, Any]) -> None:
    if package.get("schema_version") != SCHEMA_VERSION:
        raise DecisionConditionError("unsupported Decision Conditions schema")
    if [item.get("gap_id") for item in package.get("conditions", [])] != list(GAP_IDS):
        raise DecisionConditionError("Decision Conditions must contain the two declared gaps in stable order")
    for item in package["conditions"]:
        expected_record = copy.deepcopy(item)
        actual_record_hash = expected_record.pop("record_sha256", None)
        if actual_record_hash != digest(expected_record):
            raise DecisionConditionError("Decision Condition record hash mismatch")
        action = item["client_action_condition"]
        if action["selected_action"] != "UNSPECIFIED" or action["status"] != "NO_CLIENT_DECISION_RECORDED":
            raise DecisionConditionError("public export must not infer a client action")
        if item["preserved_uncertainty"]["unresolved"][0]["status"] != "UNRESOLVED":
            raise DecisionConditionError("unresolved evidence status was lost")
        if item["preserved_uncertainty"]["unsupported"][0]["status"] != "UNSUPPORTED":
            raise DecisionConditionError("unsupported review capability was lost")
    expected = copy.deepcopy(package)
    actual_hash = expected.pop("snapshot_sha256", None)
    if actual_hash != digest(expected):
        raise DecisionConditionError("Decision Conditions snapshot hash mismatch")
    _safe(package, "decision_conditions")
