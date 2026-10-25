#!/usr/bin/env python3
"""Deterministic source-dependency records for SE-DUAL-SITE-002.

The module deliberately does not fetch sources or infer independence.  It
validates human-recorded provenance, applies an explicit gap-specific rule,
and produces auditable counts whose row membership is always returned.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime
from typing import Any
from urllib.parse import unquote, urlsplit, urlunsplit


ROW_SCHEMA_VERSION = "se-source-dependency-row-v0.1"
REGISTRY_SCHEMA_VERSION = "se-source-dependency-registry-v0.1"
RULE_SCHEMA_VERSION = "se-source-qualification-rules-v0.1"
DEPENDENCY_CLASSES = {
    "ISSUER_AUTHORED",
    "DERIVED",
    "PARTIALLY_DEPENDENT",
    "INDEPENDENT",
    "UNKNOWN",
}
EVIDENCE_LEVELS = ("E0", "E1", "E2", "E3", "E4", "E5")
QUALIFICATION_STATUSES = {
    "QUALIFIED",
    "NOT_QUALIFIED",
    "NOT_ASSESSED",
    "INSUFFICIENT_DATA",
}
SOURCE_ACCESS_STATUSES = {
    "READ_FULL",
    "READ_PARTIAL",
    "ABSTRACT_ONLY",
    "PAYWALLED",
    "UNAVAILABLE",
    "CORRUPT",
    "UNKNOWN",
}
ORIGINATOR_ROLES = {
    "OPERATOR",
    "SUPPLIER",
    "CUSTOMER",
    "REGULATOR",
    "RESEARCHER",
    "MEDIA",
    "OTHER",
    "UNKNOWN",
}
BAD_ACCESS = {"UNAVAILABLE", "CORRUPT", "UNKNOWN"}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ROW_ID_RE = re.compile(r"^SE-SOURCE-ROW-[A-Z0-9][A-Z0-9._-]*$")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
MARKUP_RE = re.compile(r"<\s*/?\s*[a-z!][^>]*>|javascript\s*:|\bon\w+\s*=", re.I)


class SourceDependencyError(ValueError):
    """Raised when a record cannot be safely or deterministically accepted."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_digest(row: dict[str, Any]) -> str:
    payload = copy.deepcopy(row)
    payload.pop("record_hash", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def seal_record(row: dict[str, Any]) -> dict[str, Any]:
    sealed = copy.deepcopy(row)
    sealed["record_hash"] = record_digest(sealed)
    return sealed


def _fail(message: str) -> None:
    raise SourceDependencyError(message)


def _iso8601(value: Any, field: str, *, nullable: bool = False) -> None:
    if value is None and nullable:
        return
    if not isinstance(value, str) or not value:
        _fail(f"{field} must be a non-empty ISO-8601 string")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise SourceDependencyError(f"{field} is not ISO-8601") from exc


def _safe_strings(value: Any, path: str = "record") -> None:
    if isinstance(value, str):
        decoded = unquote(value)
        if CONTROL_RE.search(value) or MARKUP_RE.search(value) or MARKUP_RE.search(decoded):
            _fail(f"unsafe markup or control content at {path}")
    elif isinstance(value, dict):
        for key, item in value.items():
            _safe_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _safe_strings(item, f"{path}[{index}]")


def normalize_url(value: Any) -> str:
    if not isinstance(value, str) or not value:
        _fail("immutable_source.url must be a non-empty string")
    if CONTROL_RE.search(value) or "\\" in value:
        _fail("source URL contains unsafe characters")
    parts = urlsplit(value)
    if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
        _fail("source URL must use http or https with a host")
    if parts.username or parts.password:
        _fail("source URL must not contain credentials")
    decoded_path = unquote(parts.path)
    if any(part in {".", ".."} for part in decoded_path.split("/")):
        _fail("source URL contains path traversal")
    if MARKUP_RE.search(unquote(value)):
        _fail("source URL contains executable markup")
    host = parts.hostname.lower()
    try:
        port = parts.port
    except ValueError as exc:
        raise SourceDependencyError("source URL contains an invalid port") from exc
    if port and not ((parts.scheme.lower() == "http" and port == 80) or (parts.scheme.lower() == "https" and port == 443)):
        host = f"{host}:{port}"
    return urlunsplit((parts.scheme.lower(), host, parts.path or "/", parts.query, ""))


def load_rules(document: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if document.get("schema_version") != RULE_SCHEMA_VERSION:
        _fail("unsupported qualification-rule schema_version")
    rules = document.get("rules")
    if not isinstance(rules, list) or not rules:
        _fail("qualification rules must be a non-empty array")
    indexed: dict[str, dict[str, Any]] = {}
    for rule in rules:
        required = {
            "qualification_rule_id",
            "gap_id",
            "claim_id",
            "minimum_evidence_level",
            "permitted_dependency_classes",
            "permitted_originator_roles",
            "required_evidence_facets",
            "rule_text",
            "rubric_version",
        }
        if not isinstance(rule, dict) or set(rule) != required:
            _fail("qualification rule fields do not match v0.1")
        rule_id = rule["qualification_rule_id"]
        if not isinstance(rule_id, str) or not rule_id or rule_id in indexed:
            _fail("qualification rule IDs must be unique non-empty strings")
        if rule["minimum_evidence_level"] not in EVIDENCE_LEVELS:
            _fail(f"invalid minimum evidence level for {rule_id}")
        if not set(rule["permitted_dependency_classes"]) <= DEPENDENCY_CLASSES:
            _fail(f"invalid dependency class in {rule_id}")
        if not set(rule["permitted_originator_roles"]) <= ORIGINATOR_ROLES:
            _fail(f"invalid originator role in {rule_id}")
        indexed[rule_id] = copy.deepcopy(rule)
    _safe_strings(document, "qualification_rules")
    return indexed


def evaluate_qualification(row: dict[str, Any], rule: dict[str, Any]) -> tuple[str, str]:
    """Apply only the declared rule; never infer truth or case state."""
    if row.get("source_access_status") in BAD_ACCESS:
        return "INSUFFICIENT_DATA", "The source was not available as a reviewable record."
    if row.get("gap_id") != rule["gap_id"] or row.get("claim_id") != rule["claim_id"]:
        return "NOT_ASSESSED", "The row is outside this gap-specific rule."
    level = row.get("evidence_level")
    if level not in EVIDENCE_LEVELS or EVIDENCE_LEVELS.index(level) < EVIDENCE_LEVELS.index(rule["minimum_evidence_level"]):
        return "NOT_QUALIFIED", f"{level or 'UNKNOWN'} is below the rule minimum {rule['minimum_evidence_level']}."
    if row.get("dependency_class") not in rule["permitted_dependency_classes"]:
        return "NOT_QUALIFIED", "The dependency class is outside the rule's permitted classes."
    if row.get("originator_role") not in rule["permitted_originator_roles"]:
        return "NOT_QUALIFIED", "The originator role is outside the rule's permitted roles."
    missing = sorted(set(rule["required_evidence_facets"]) - set(row.get("evidence_facets", [])))
    if missing:
        return "NOT_QUALIFIED", "Required facets are missing: " + ", ".join(missing) + "."
    return "QUALIFIED", "The row meets this explicit gap-specific rule; this does not establish truth or change case state."


def _require_exact_keys(value: Any, required: set[str], name: str) -> None:
    if not isinstance(value, dict) or set(value) != required:
        _fail(f"{name} fields do not match v0.1")


def validate_row(
    row: dict[str, Any],
    rules: dict[str, dict[str, Any]],
    registry_ids: set[str],
) -> None:
    required = {
        "schema_version", "source_row_id", "claim_id", "gap_id", "immutable_source",
        "originator_id", "originator_role", "authored_by_evidence",
        "originating_evidence_lineage", "author_issuer_relationship_evidence",
        "dependency_class", "dependency_rationale", "evidence_level", "evidence_facets",
        "evidence_rationale", "qualification_rule_id", "qualification_status",
        "qualification_reason", "source_access_status", "search_run_id", "search_scope",
        "evidence_cutoff", "last_checked_at", "reviewed_at", "rubric_version",
        "reviewers", "reviewer_disagreement", "supersession", "event_timestamp",
        "record_hash",
    }
    _require_exact_keys(row, required, "source row")
    _safe_strings(row)
    if row["schema_version"] != ROW_SCHEMA_VERSION:
        _fail("unsupported source-row schema_version")
    if not isinstance(row["source_row_id"], str) or not ROW_ID_RE.fullmatch(row["source_row_id"]):
        _fail("invalid source_row_id")
    if not isinstance(row["claim_id"], str) or not row["claim_id"]:
        _fail("claim_id is required")
    if row["gap_id"] is not None and (not isinstance(row["gap_id"], str) or not row["gap_id"]):
        _fail("gap_id must be null or a non-empty string")
    source = row["immutable_source"]
    _require_exact_keys(source, {"url", "title", "publisher_host", "capture"}, "immutable_source")
    normalize_url(source["url"])
    if not all(isinstance(source[key], str) and source[key] for key in ("title", "publisher_host")):
        _fail("source title and publisher_host are required")
    capture = source["capture"]
    _require_exact_keys(capture, {"capture_type", "captured_at", "sha256", "failure_reason"}, "capture")
    if capture["capture_type"] not in {"STRUCTURED_SNAPSHOT", "DOCUMENT_HASH", "REFERENCE_ONLY"}:
        _fail("invalid capture_type")
    _iso8601(capture["captured_at"], "captured_at", nullable=True)
    if capture["sha256"] is not None and (not isinstance(capture["sha256"], str) or not SHA256_RE.fullmatch(capture["sha256"])):
        _fail("capture.sha256 must be null or a lowercase SHA-256")
    if row["source_access_status"] in {"READ_FULL", "READ_PARTIAL", "ABSTRACT_ONLY"} and not capture["sha256"]:
        _fail("reviewed source content requires a capture hash")
    if row["source_access_status"] in BAD_ACCESS and not capture["failure_reason"]:
        _fail("unavailable, corrupt, or unknown access requires a failure reason")
    if capture["failure_reason"] is not None and not isinstance(capture["failure_reason"], str):
        _fail("capture.failure_reason must be null or a string")
    if row["originator_role"] not in ORIGINATOR_ROLES or not isinstance(row["originator_id"], str) or not row["originator_id"]:
        _fail("originator identity and role are required")
    for field in ("authored_by_evidence", "author_issuer_relationship_evidence"):
        values = row[field]
        if not isinstance(values, list) or not values or not all(isinstance(item, str) and item for item in values):
            _fail(f"{field} must contain auditable evidence references")
    lineage = row["originating_evidence_lineage"]
    if not isinstance(lineage, list) or not all(isinstance(item, str) and ROW_ID_RE.fullmatch(item) for item in lineage):
        _fail("originating_evidence_lineage is invalid")
    if row["source_row_id"] in lineage:
        _fail("a source row cannot depend on itself")
    missing_lineage = sorted(set(lineage) - registry_ids)
    if missing_lineage:
        _fail("lineage references missing source rows: " + ", ".join(missing_lineage))
    if row["dependency_class"] == "DERIVED" and not lineage:
        _fail("DERIVED rows require originating evidence lineage")
    if row["dependency_class"] not in DEPENDENCY_CLASSES:
        _fail("invalid dependency_class")
    if row["evidence_level"] not in EVIDENCE_LEVELS:
        _fail("invalid evidence_level")
    if not isinstance(row["evidence_facets"], list) or len(set(row["evidence_facets"])) != len(row["evidence_facets"]):
        _fail("evidence_facets must be a duplicate-free array")
    if row["qualification_status"] not in QUALIFICATION_STATUSES:
        _fail("invalid qualification_status")
    if row["source_access_status"] not in SOURCE_ACCESS_STATUSES:
        _fail("invalid source_access_status")
    rule_id = row["qualification_rule_id"]
    if rule_id not in rules:
        _fail("qualification_rule_id is not registered")
    expected_status, _ = evaluate_qualification(row, rules[rule_id])
    if row["qualification_status"] != expected_status:
        _fail(
            "qualification_status does not match the declared gap-specific rule: "
            f"expected {expected_status}"
        )
    for field in ("dependency_rationale", "evidence_rationale", "qualification_reason", "search_run_id", "rubric_version"):
        if not isinstance(row[field], str) or not row[field]:
            _fail(f"{field} is required")
    scope = row["search_scope"]
    _require_exact_keys(scope, {"query", "inclusion_scope", "exclusion_scope", "blocked_sources"}, "search_scope")
    if not all(isinstance(scope[key], str) for key in ("query", "inclusion_scope", "exclusion_scope")):
        _fail("search query and scope boundaries must be strings")
    if not isinstance(scope["blocked_sources"], list) or not all(isinstance(item, str) for item in scope["blocked_sources"]):
        _fail("blocked_sources must be an array of strings")
    for field in ("evidence_cutoff", "last_checked_at", "reviewed_at", "event_timestamp"):
        _iso8601(row[field], field)
    reviewers = row["reviewers"]
    if not isinstance(reviewers, list) or not 1 <= len(reviewers) <= 2:
        _fail("one or two reviewer records are required")
    review_keys = {"reviewer_id", "reviewed_at", "dependency_class", "evidence_level", "qualification_status", "note"}
    for review in reviewers:
        _require_exact_keys(review, review_keys, "reviewer")
        _iso8601(review["reviewed_at"], "reviewer.reviewed_at")
        if not isinstance(review["reviewer_id"], str) or not review["reviewer_id"] or not isinstance(review["note"], str):
            _fail("reviewer identity and note are required strings")
        if review["dependency_class"] not in DEPENDENCY_CLASSES or review["evidence_level"] not in EVIDENCE_LEVELS or review["qualification_status"] not in QUALIFICATION_STATUSES:
            _fail("reviewer labels are invalid")
    if len({review["reviewer_id"] for review in reviewers}) != len(reviewers):
        _fail("reviewer IDs must be unique")
    disagreement = row["reviewer_disagreement"]
    _require_exact_keys(disagreement, {"detected", "fields", "resolution_status", "resolution_note"}, "reviewer_disagreement")
    differing: list[str] = []
    if len(reviewers) == 2:
        for field in ("dependency_class", "evidence_level", "qualification_status"):
            if reviewers[0][field] != reviewers[1][field]:
                differing.append(field)
    if disagreement["detected"] != bool(differing) or sorted(disagreement["fields"]) != sorted(differing):
        _fail("reviewer disagreement must expose every conflicting label")
    if differing and disagreement["resolution_status"] not in {"UNRESOLVED", "RESOLVED"}:
        _fail("conflicting labels require an explicit resolution status")
    supersession = row["supersession"]
    _require_exact_keys(supersession, {"predecessor_source_row_id", "reason"}, "supersession")
    predecessor = supersession["predecessor_source_row_id"]
    if predecessor is not None and predecessor not in registry_ids:
        _fail("supersession predecessor is missing")
    if predecessor and not supersession["reason"]:
        _fail("supersession requires a reason")
    if supersession["reason"] is not None and not isinstance(supersession["reason"], str):
        _fail("supersession reason must be null or a string")
    if row["record_hash"] != record_digest(row):
        _fail("record_hash does not match canonical row content")


def validate_registry(registry: dict[str, Any], rules_document: dict[str, Any]) -> None:
    _require_exact_keys(registry, {"schema_version", "rubric_version", "rows"}, "registry")
    if registry["schema_version"] != REGISTRY_SCHEMA_VERSION:
        _fail("unsupported registry schema_version")
    if not isinstance(registry["rubric_version"], str) or not registry["rubric_version"]:
        _fail("registry rubric_version is required")
    rows = registry["rows"]
    if not isinstance(rows, list):
        _fail("registry rows must be an array")
    identifiers = [row.get("source_row_id") for row in rows if isinstance(row, dict)]
    if len(identifiers) != len(rows) or len(set(identifiers)) != len(identifiers):
        _fail("source_row_id values must be unique")
    rules = load_rules(rules_document)
    registry_ids = set(identifiers)
    for row in rows:
        validate_row(row, rules, registry_ids)
    lineage_by_id = {
        row["source_row_id"]: row["originating_evidence_lineage"] for row in rows
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(row_id: str) -> None:
        if row_id in visiting:
            _fail("source lineage contains a cycle")
        if row_id in visited:
            return
        visiting.add(row_id)
        for predecessor in lineage_by_id[row_id]:
            visit(predecessor)
        visiting.remove(row_id)
        visited.add(row_id)

    for row_id in sorted(registry_ids):
        visit(row_id)


def migrate_registry(document: dict[str, Any]) -> dict[str, Any]:
    """Idempotently wrap an empty/new static registry without reclassifying rows."""
    migrated = copy.deepcopy(document)
    version = migrated.get("schema_version")
    if version is None:
        migrated["schema_version"] = REGISTRY_SCHEMA_VERSION
    elif version != REGISTRY_SCHEMA_VERSION:
        _fail("no automatic migration exists for this registry version")
    migrated.setdefault("rubric_version", "SE-SOURCE-DEPENDENCY-RUBRIC-v0.1")
    migrated.setdefault("rows", [])
    return json.loads(canonical_json(migrated))


def assert_append_only(previous: dict[str, Any], current: dict[str, Any]) -> None:
    previous_rows = {row["source_row_id"]: row for row in previous.get("rows", [])}
    current_rows = {row["source_row_id"]: row for row in current.get("rows", [])}
    missing = sorted(set(previous_rows) - set(current_rows))
    if missing:
        _fail("immutable source rows were removed: " + ", ".join(missing))
    mutated = sorted(row_id for row_id, row in previous_rows.items() if current_rows[row_id] != row)
    if mutated:
        _fail("immutable source rows were changed: " + ", ".join(mutated))
    for row_id in sorted(set(current_rows) - set(previous_rows)):
        predecessor = current_rows[row_id]["supersession"]["predecessor_source_row_id"]
        if predecessor and predecessor not in previous_rows:
            _fail("a correction must supersede a row from the prior registry")


def deterministic_metrics(registry: dict[str, Any], scope: dict[str, str]) -> dict[str, Any]:
    rows = sorted(registry.get("rows", []), key=lambda row: row["source_row_id"])
    row_ids = [row["source_row_id"] for row in rows]

    def metric(value: int, members: list[str]) -> dict[str, Any]:
        return {"value": value, "source_row_ids": sorted(members), "scope": copy.deepcopy(scope)}

    normalized_urls: dict[str, list[str]] = {}
    originators: dict[str, list[str]] = {}
    independent: dict[str, list[str]] = {}
    for row in rows:
        row_id = row["source_row_id"]
        normalized_urls.setdefault(normalize_url(row["immutable_source"]["url"]), []).append(row_id)
        originators.setdefault(row["originator_id"], []).append(row_id)
        if row["dependency_class"] == "INDEPENDENT":
            independent.setdefault(row["originator_id"], []).append(row_id)
    qualified = [row["source_row_id"] for row in rows if row["qualification_status"] == "QUALIFIED"]
    unknown = [row["source_row_id"] for row in rows if row["dependency_class"] == "UNKNOWN"]
    partial = [row["source_row_id"] for row in rows if row["dependency_class"] == "PARTIALLY_DEPENDENT"]
    classified = [row["source_row_id"] for row in rows if row["dependency_class"] != "UNKNOWN"]

    lineage_by_id = {
        row["source_row_id"]: row["originating_evidence_lineage"] for row in rows
    }

    def lineage_roots(row_id: str, trail: frozenset[str] = frozenset()) -> set[str]:
        """Return originating rows so renderings never inflate evidence counts."""
        if row_id in trail:
            _fail("source dependency lineage contains a cycle")
        parents = lineage_by_id.get(row_id, [])
        if not parents:
            return {row_id}
        roots: set[str] = set()
        for parent in parents:
            roots.update(lineage_roots(parent, trail | {row_id}))
        return roots

    lineage_root_ids = sorted({
        root
        for row_id in row_ids
        for root in lineage_roots(row_id)
    })
    return {
        "reviewed_urls": metric(len(normalized_urls), [row_id for ids in normalized_urls.values() for row_id in ids]),
        "distinct_evidence_lineages": metric(len(lineage_root_ids), lineage_root_ids),
        "distinct_originators": metric(len(originators), [row_id for ids in originators.values() for row_id in ids]),
        "independent_originators": metric(len(independent), [row_id for ids in independent.values() for row_id in ids]),
        "qualified_evidence_rows": metric(len(qualified), qualified),
        "unknown_dependency_rows": metric(len(unknown), unknown),
        "partially_dependent_rows": metric(len(partial), partial),
        "classification_coverage": {
            "status": "INSUFFICIENT_DATA" if not row_ids else "AVAILABLE",
            "classified_row_count": len(classified),
            "total_row_count": len(row_ids),
            "source_row_ids": row_ids,
            "scope": copy.deepcopy(scope),
            "percentage": None if not row_ids else round(100 * len(classified) / len(row_ids), 6),
        },
    }
