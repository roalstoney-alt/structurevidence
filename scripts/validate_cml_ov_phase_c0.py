#!/usr/bin/env python3
"""Validate the Phase C0 framework and reviewed human-discovery records."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import date, datetime
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

from test_cml_v01 import ROOT, flatten_keys

ENTRY_SHA = "f2cb555aa773b788bd5268276d4adf054a1b5b25"
VERSION = "CML_OV_v0.1_PHASE_C0"
TARGETS = {"OV-01", "OV-03"}
DIRECT_CLASSES = {
    "DIRECT_USER_STATEMENT",
    "DIRECT_ENGINEER_STATEMENT",
    "DIRECT_SERVICE_STATEMENT",
    "DIRECT_SUPPLIER_STATEMENT",
}
QUALIFYING_STATES = {"ACTIVE_UNRESOLVED", "RESOLVED_BUT_SUBOPTIMAL"}
SENTINEL_BOTTLENECKS = {"NONE_IDENTIFIED", "UNKNOWN"}
PLACEHOLDER = "REPLACE_BEFORE_INGESTION"
FRAMEWORK_FILES = {
    "technical-risk/opportunity-validation/PHASE_C0_STATUS_VOCABULARY.json",
    "technical-risk/opportunity-validation/schema/phase-c0-response.schema.json",
    "technical-risk/opportunity-validation/templates/phase-c0-response.json",
    "scripts/validate_cml_ov_phase_c0.py",
    "scripts/test_cml_ov_phase_c0.py",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load(path: Path | str) -> dict:
    target = path if isinstance(path, Path) else ROOT / path
    return json.loads(target.read_text(encoding="utf-8"))


def schema_paths() -> tuple[Path, Path]:
    return (
        ROOT / "technical-risk/opportunity-validation/schema/phase-c0-response.schema.json",
        ROOT / "evidence/core/schema/evidence_core_record.schema.json",
    )


def schema_validate(value: dict) -> None:
    schema_path, core_path = schema_paths()
    schema, core = load(schema_path), load(core_path)
    registry = Registry().with_resource(core_path.as_uri(), Resource.from_contents(core))
    schema["$id"] = schema_path.as_uri()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema, registry=registry, format_checker=jsonschema.FormatChecker()
    ).validate(value)


def framework_integrity() -> dict:
    schema_path, _ = schema_paths()
    schema = load(schema_path)
    vocabulary = load("technical-risk/opportunity-validation/PHASE_C0_STATUS_VOCABULARY.json")
    template = load("technical-risk/opportunity-validation/templates/phase-c0-response.json")
    jsonschema.Draft202012Validator.check_schema(schema)
    schema_validate(template)
    require(vocabulary["version"] == VERSION, "vocabulary version drift")
    mappings = {
        "application_confirmation": "discovery_status",
        "binary_discovery_status": "discovery_status",
        "contact_type": "contact_type",
        "current_solution": "current_solution",
        "bottleneck": "bottleneck",
        "improvement_dimension": "improvement_dimension",
        "evidence_class": "evidence_class",
        "confidentiality": "confidentiality",
        "opportunity_state": "opportunity_state",
        "c0_result": "c0_result",
    }
    for vocabulary_key, schema_key in mappings.items():
        require(
            vocabulary[vocabulary_key] == schema["$defs"][schema_key]["enum"],
            f"schema/vocabulary drift: {vocabulary_key}",
        )
    require(template["discovery_response"]["record_kind"] == "TEMPLATE", "template marker missing")
    require(template["discovery_response"]["confidentiality"] == "PRIVATE", "template must default PRIVATE")
    return {"schema_valid": True, "template_valid": True, "vocabularies_checked": len(mappings)}


def entry_baseline() -> dict:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    remote = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=ROOT, text=True).strip()
    require(head == remote == ENTRY_SHA, "Phase C0 entry SHA mismatch")
    dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).splitlines()
    paths = {row[3:] for row in dirty}
    allowed_prefixes = (
        "technical-risk/records/amphenol-10081811-101-07lf/opportunity-validation/phase-c0/",
        "technical-risk/records/amphenol-rf-095-725-134-006/opportunity-validation/phase-c0/",
    )
    unexpected = sorted(path for path in paths if path not in FRAMEWORK_FILES and not path.startswith(allowed_prefixes))
    require(not unexpected, f"out-of-scope worktree changes: {unexpected}")
    outcomes = {}
    for target, slug in {
        "OV-01": "amphenol-10081811-101-07lf",
        "OV-03": "amphenol-rf-095-725-134-006",
    }.items():
        gate = load(ROOT / "technical-risk/records" / slug / "opportunity-validation/phase-b-r1/02_B_R1_GATE.json")
        outcomes[target] = gate["terminal_outcome"]
    require(set(outcomes.values()) == {"PUBLIC_EVIDENCE_CEILING"}, "authorized targets are not at the required B-R1 ceiling")
    return {"head": head, "origin_main": remote, "phase_b_r1_outcomes": outcomes, "unexpected_changes": []}


def _has_direct_statement(response: dict, field: str) -> bool:
    return any(
        statement["field"] == field and statement["evidence_class"] in DIRECT_CLASSES
        for statement in response["statements"]
    )


def _no_mixed_sentinel(values: list[str], sentinels: set[str], name: str) -> None:
    require(len(values) == 1 or not (set(values) & sentinels), f"{name} mixes a sentinel with substantive values")


def validate_response(record: dict) -> dict:
    schema_validate(record)
    core = record["core"]
    response = record["discovery_response"]
    require(response["record_kind"] == "RESPONSE", "template is not an ingestible response")
    require(response["target"] in TARGETS, "unauthorized target")
    require(core["core_version"] == "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1", "shared Evidence Core version required")
    require(core["domain"] == "TECHNICAL_RISK" and core["protocol"] == "CML", "Evidence Core domain/protocol mismatch")
    require(core["policy_version"] == VERSION, "policy version mismatch")
    require(core["subject_class"] == "CML_OPPORTUNITY_VALIDATION_DISCOVERY_RESPONSE", "subject class mismatch")
    require(core["subject_id"] == response["target"], "Evidence Core subject must match the C0 target")
    require(core["source_refs"], "direct response requires a private source reference")
    for key in ("input_hash", "record_hash"):
        value = core[key]
        require(len(value) == 64 and set(value) <= set("0123456789abcdef") and set(value) != {"0"}, f"{key} must be a populated SHA-256 value")
    require(PLACEHOLDER not in json.dumps(record), "unreplaced template placeholder")
    require(response["interaction_date"] is not None, "interaction date required for a response")
    require(response["contact_source"]["verified_public"], "contact path must be verified public")
    require(response["confidentiality"] == "PRIVATE", "direct response must remain PRIVATE absent separate publication authorization")
    require(response["statements"], "meaningful response requires classified statements")
    require(date.fromisoformat(response["interaction_date"]) <= datetime.fromisoformat(core["known_at"].replace("Z", "+00:00")).date(), "interaction cannot postdate knowledge time")

    _no_mixed_sentinel(response["current_solution"], {"UNKNOWN"}, "current_solution")
    _no_mixed_sentinel(response["current_bottleneck"], SENTINEL_BOTTLENECKS, "current_bottleneck")
    _no_mixed_sentinel(response["improvement_dimension"], {"UNKNOWN", "NO_MATERIAL_IMPROVEMENT_NEEDED"}, "improvement_dimension")
    require(not (flatten_keys(record) & {"opportunity_score", "numeric_opportunity_score", "risk_score"}), "numeric opportunity score is forbidden")

    state = response["opportunity_state"]
    specific_bottleneck = bool(set(response["current_bottleneck"]) - SENTINEL_BOTTLENECKS)
    if state in QUALIFYING_STATES:
        require(response["application_confirmed"] == "YES", "qualifying state requires confirmed application")
        require(specific_bottleneck, "qualifying state requires a specific bottleneck")
        require(_has_direct_statement(response, "APPLICATION"), "application confirmation requires direct testimony")
        require(_has_direct_statement(response, "BOTTLENECK"), "material bottleneck requires direct testimony")
        require(response["improvement_dimension"] not in (["UNKNOWN"], ["NO_MATERIAL_IMPROVEMENT_NEEDED"]), "qualifying state requires a material improvement dimension")
        if state == "RESOLVED_BUT_SUBOPTIMAL":
            require(response["current_solution"] != ["UNKNOWN"], "suboptimal resolution requires an identified current solution")
    elif state == "RESOLVED_COMPETITIVE":
        require(response["application_confirmed"] == "YES", "competitive resolution requires a confirmed application")
        require(_has_direct_statement(response, "APPLICATION"), "competitive resolution requires direct application evidence")
        require(response["current_solution"] != ["UNKNOWN"], "competitive resolution requires an identified current solution")
        require(response["current_bottleneck"] == ["NONE_IDENTIFIED"], "competitive resolution requires no material bottleneck")
        require(response["improvement_dimension"] == ["NO_MATERIAL_IMPROVEMENT_NEEDED"], "competitive resolution requires no material improvement")
    elif state == "NO_CURRENT_APPLICATION":
        require(response["application_confirmed"] == "NO", "no-current-application state requires NO")
        require(_has_direct_statement(response, "APPLICATION"), "no-current-application requires relevant direct evidence")

    hypothesis = response["improvement_hypothesis"]
    if hypothesis is not None:
        require(state in QUALIFYING_STATES and specific_bottleneck, "hypothesis requires a directly evidenced qualifying bottleneck")
    if response["c0_result"] == "PROCEED_TO_SOLUTION_SCOPING":
        require(state in QUALIFYING_STATES, "proceed result requires qualifying opportunity state")
        require(response["application_confirmed"] == "YES" and specific_bottleneck, "proceed result requires application and specific bottleneck")
        require(hypothesis is not None and response["measurable"] == "YES", "proceed result requires a testable, measurable hypothesis")
    if state == "INSUFFICIENT_DIRECT_EVIDENCE":
        require(response["c0_result"] in {"INSUFFICIENT_DIRECT_EVIDENCE", "MONITOR"}, "insufficient evidence cannot proceed or archive as a finding")

    return {
        "target": response["target"],
        "opportunity_state": state,
        "c0_result": response["c0_result"],
        "classified_statements": len(response["statements"]),
        "private": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", nargs="*", type=Path, help="reviewed Phase C0 response JSON files")
    args = parser.parse_args()
    result = {"entry": entry_baseline(), "framework": framework_integrity(), "records": []}
    for path in args.records:
        result["records"].append(validate_response(load(path.resolve())))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
