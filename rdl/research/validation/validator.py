"""Semantic validator for RDL_RESEARCH_RECORD_v0.1."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import jsonschema
from referencing import Registry, Resource


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "rdl/research/schema/research-record.schema.json"
CORE_SCHEMA_PATH = ROOT / "evidence/core/schema/evidence_core_record.schema.json"
STOP_REASONS_PATH = ROOT / "rdl/research/vocabulary/STOP_REASONS.json"

FAILED_RESEARCH_REASONS = {
    "DUPLICATE_ONLY",
    "PUBLIC_DATA_INSUFFICIENT",
    "SOURCE_UNAVAILABLE",
    "SEARCH_SPACE_EXHAUSTED",
    "EVIDENCE_CONTRADICTED",
    "WRONG_HYPOTHESIS",
    "COMMERCIAL_RELEVANCE_FAILED",
}
PROHIBITED_SCORE_KEYS = {
    "confidence_score",
    "research_quality_score",
    "mev_score",
    "marginal_evidence_value_score",
}
PRIVATE_KEYS = {
    "raw_private_prompt",
    "billing_credentials",
    "api_key",
    "customer_secret",
    "uploaded_file_contents",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_keys(child) for child in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_keys(child) for child in value), set())
    return set()


def schema_validate(record: dict) -> None:
    schema = load(SCHEMA_PATH)
    core = load(CORE_SCHEMA_PATH)
    schema["$id"] = SCHEMA_PATH.as_uri()
    core["$id"] = CORE_SCHEMA_PATH.as_uri()
    registry = Registry().with_resource(CORE_SCHEMA_PATH.as_uri(), Resource.from_contents(core))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema,
        registry=registry,
        format_checker=jsonschema.FormatChecker(),
    ).validate(record)


def _measurement(record: dict, field: str) -> dict:
    return record["research_record"]["telemetry"][field]


def validate(record: dict) -> dict:
    schema_validate(record)
    core = record["core"]
    payload = record["research_record"]

    require(core["core_version"] == "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1", "existing Evidence Core must be reused")
    require(core["domain"] == "RESEARCH_GOVERNANCE", "RDL research domain mismatch")
    require(core["protocol"] == "RDL", "RDL protocol required")
    require(core["policy_version"] == "RDL_RESEARCH_RECORD_v0.1", "RDL policy version mismatch")
    require(core["record_id"] == payload["research_id"], "core and payload research identity mismatch")
    require(datetime.fromisoformat(payload["completed_at"].replace("Z", "+00:00")) >= datetime.fromisoformat(payload["started_at"].replace("Z", "+00:00")), "research completed before it started")

    all_keys = {key.lower() for key in _keys(record)}
    require(not (all_keys & PROHIBITED_SCORE_KEYS), "opaque research score prohibited")
    require(not (all_keys & PRIVATE_KEYS), "private raw data or credentials prohibited")
    require(payload["structural_interpretation_authority"] == "CML_REFERENCE_ONLY", "RDL cannot determine structural truth")

    level = payload["research_level"]
    authorization = payload["authorization"]
    if level in {"L2_INVESTIGATE", "L3_DEEP"}:
        require(authorization["status"] != "NOT_REQUIRED", "L2/L3 must represent required authorization")
        if authorization["status"] == "AUTHORIZED":
            require(bool(authorization["authorization_ref"]), "authorized L2/L3 requires external authorization reference")
    if level == "L0_REUSE":
        require(all(not action["external_research"] for action in payload["research_actions"]), "L0 cannot contain external research")

    if payload["decision_changed"]:
        require(payload["decision_before"] != payload["decision_after"], "decision_changed requires a real before/after delta")
        require(bool(payload["decision_change_reason"]), "decision_changed requires reason")
    else:
        require(payload["decision_before"] == payload["decision_after"], "unchanged decision must preserve decision value")

    source_checked = set(payload["source_refs_checked"])
    source_used = set(payload["source_refs_used"])
    source_rejected = set(payload["source_refs_rejected"])
    require(source_used <= source_checked, "used sources must have been checked")
    require(source_rejected <= source_checked, "rejected sources must have been checked")
    require(not (source_used & source_rejected), "a source cannot be both used and rejected")

    new_evidence = set(payload["new_evidence_refs"])
    duplicate_evidence = set(payload["duplicate_evidence_refs"])
    counter_evidence = set(payload["counter_evidence_refs"])
    require(not (new_evidence & duplicate_evidence), "new evidence cannot also be duplicate evidence")
    require(not (new_evidence & counter_evidence), "event evidence must be referenced by one research-result role")
    if payload["stop_reason"] == "DUPLICATE_ONLY":
        require(not new_evidence and bool(duplicate_evidence), "DUPLICATE_ONLY requires zero new and at least one duplicate evidence ref")
    if payload["stop_reason"] in FAILED_RESEARCH_REASONS:
        require(isinstance(payload["new_evidence_refs"], list), "failed research remains valid structured data")

    standard_reasons = set(load(STOP_REASONS_PATH)["reasons"])
    stop_reason = payload["stop_reason"]
    require(stop_reason in standard_reasons or re.fullmatch(r"EXTENSION_[A-Z0-9_]+", stop_reason), "invalid stop reason")
    if stop_reason == "HUMAN_REVIEW_REQUIRED":
        require(payload["human_review_required"], "human review stop must require human review")

    estimated_fields = {"estimated_tokens", "estimated_model_cost"}
    observed_fields = {"observed_input_tokens", "observed_output_tokens", "observed_model_cost", "data_cost"}
    for field in estimated_fields:
        require(_measurement(record, field)["status"] in {"ESTIMATED", "UNKNOWN", "NOT_APPLICABLE"}, f"{field} cannot masquerade as observed")
    for field in observed_fields:
        require(_measurement(record, field)["status"] in {"OBSERVED", "UNKNOWN", "NOT_APPLICABLE"}, f"{field} cannot masquerade as estimated")
    for field, measurement in payload["telemetry"].items():
        if isinstance(measurement, dict) and measurement["status"] == "UNKNOWN":
            require(measurement["value"] is None, f"UNKNOWN {field} must be null, not zero")

    if payload["research_class"] != "CUSTOMER_SPECIFIC_RESEARCH":
        require(payload["customer_case_id"] is None, "public company mention cannot imply customer-specific research")

    require(all(row["preserves_original"] for row in payload["revision_history"]), "research corrections must preserve originals")
    return {
        "research_id": payload["research_id"],
        "research_level": level,
        "stop_reason": stop_reason,
        "decision_changed": payload["decision_changed"],
        "new_evidence_count": len(new_evidence),
        "duplicate_evidence_count": len(duplicate_evidence),
        "evidence_store_created": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="+", type=Path)
    args = parser.parse_args()
    results = [validate(load(path.resolve())) for path in args.records]
    print(json.dumps({"schema_version": "RDL_RESEARCH_RECORD_v0.1", "records": results}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
