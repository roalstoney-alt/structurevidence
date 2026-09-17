#!/usr/bin/env python3
"""Validate CML v1.1 Task V11-2 schemas, vocabularies and PDRE semantics."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

import cml_v11_regression as regression

ROOT = Path(__file__).resolve().parents[1]
V11_2_ENTRY_SHA = "2baced87c4df494fbbe706b4e73029d767050779"
V11_2_ACCEPTED_SHA = "33931a5de0e931b1ad218d63d83a9183fd3778ec"
VERSION = "CML_v1.1"
SCHEMA_DIR = ROOT / "technical-risk/cml-v1.1/schema"
VOCAB_DIR = ROOT / "technical-risk/cml-v1.1/vocabulary"
TEMPLATE_DIR = ROOT / "technical-risk/cml-v1.1/templates"
SCHEMAS = {
    "pdre": SCHEMA_DIR / "pdre-record.schema.json",
    "dependency": SCHEMA_DIR / "dependency-record.schema.json",
    "exposure": SCHEMA_DIR / "structural-exposure.schema.json",
    "beneficiary": SCHEMA_DIR / "beneficiary-map.schema.json",
}
TEMPLATES = {
    "pdre": TEMPLATE_DIR / "pdre-record.template.json",
    "dependency": TEMPLATE_DIR / "dependency-record.template.json",
    "exposure": TEMPLATE_DIR / "structural-exposure.template.json",
    "beneficiary": TEMPLATE_DIR / "beneficiary-map.template.json",
}
READINESS = {
    "R0": ("THEORETICAL", "POSSIBLE"),
    "R1": ("SPECIFICATION_COMPATIBLE", "POSSIBLE"),
    "R2": ("ENGINEERING_REVIEWED", "TECHNICALLY_CREDIBLE"),
    "R3": ("SAMPLE_BENCH_TESTED", "TECHNICALLY_CREDIBLE"),
    "R4": ("APPLICATION_QUALIFIED", "PRODUCTION_CAPABLE_CANDIDATE"),
    "R5": ("FIELD_DEPLOYED", "REAL_WORLD_VALIDATED"),
    "R6": ("OPERATING_HISTORY_AVAILABLE", "REAL_WORLD_VALIDATED"),
    "R7": ("MULTI_ENTITY_REPLICATION", "INDUSTRY_LEVEL_MIGRATION_EVIDENCE"),
}
FRICTION = {
    "AF1": "CAPITAL_LOCK_IN", "AF2": "QUALIFICATION_LOCK_IN", "AF3": "INSTALLED_BASE_LOCK_IN",
    "AF4": "SUPPLIER_LOCK_IN", "AF5": "SOFTWARE_INTERFACE_LOCK_IN", "AF6": "ORGANIZATIONAL_LOCK_IN",
    "AF7": "REGULATORY_CERTIFICATION_LOCK_IN", "AF8": "CANNIBALIZATION_RISK",
    "AF9": "CUSTOMER_ACCEPTANCE_RISK", "AF10": "UNKNOWN_INTERNAL_FRICTION",
}
STAGES = [
    "RESEARCH_THEORY", "PATENT_PROTOTYPE", "ENGINEERING_VALIDATION", "PILOT_APPLICATION",
    "QUALIFICATION", "PRODUCTION", "FIELD_DEPLOYMENT", "MULTI_USER_MULTI_OEM_REPLICATION",
]
STAGE_EVIDENCE = {
    "RESEARCH_THEORY": {"RESEARCH_PUBLICATION"},
    "PATENT_PROTOTYPE": {"PATENT", "PROTOTYPE"},
    "ENGINEERING_VALIDATION": {"TEST_RESULT", "ENGINEERING_VALIDATION"},
    "PILOT_APPLICATION": {"TEST_RESULT", "ENGINEERING_VALIDATION", "MANUFACTURING_EVIDENCE"},
    "QUALIFICATION": {"QUALIFICATION_RESULT"},
    "PRODUCTION": {"PRODUCTION_DEPLOYMENT", "MANUFACTURING_EVIDENCE"},
    "FIELD_DEPLOYMENT": {"FIELD_OPERATION"},
    "MULTI_USER_MULTI_OEM_REPLICATION": {"MULTI_ENTITY_REPLICATION"},
}
NARRATIVE_TYPES = {"MARKETING_CLAIM", "MANAGEMENT_STATEMENT", "INTERVIEW", "ANALYST_OPINION"}
PROHIBITED_LANGUAGE = [
    "management failed", "management failure", "technologically backward", "management ignored technology",
]


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


def registry() -> Registry:
    paths = [*SCHEMAS.values(), ROOT / "evidence/core/schema/evidence_core_record.schema.json"]
    result = Registry()
    for path in paths:
        schema = load(path)
        schema["$id"] = path.as_uri()
        result = result.with_resource(path.as_uri(), Resource.from_contents(schema))
    return result


def schema_validate(value: dict, kind: str) -> None:
    path = SCHEMAS[kind]
    schema = load(path)
    schema["$id"] = path.as_uri()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(
        schema, registry=registry(), format_checker=jsonschema.FormatChecker()
    ).validate(value)


def _enum(schema: dict, definition: str) -> list[str]:
    return schema["$defs"][definition]["enum"]


def framework_integrity() -> dict:
    for kind, template in TEMPLATES.items():
        schema_validate(load(template), kind)
    pdre_schema = load(SCHEMAS["pdre"])
    constraint = load(VOCAB_DIR / "STRUCTURAL_CONSTRAINTS.json")
    readiness = load(VOCAB_DIR / "MIGRATION_READINESS.json")
    friction = load(VOCAB_DIR / "ADOPTION_FRICTION.json")
    constraint_enum = pdre_schema["properties"]["pdre_record"]["properties"]["structural_constraints"]["items"]["properties"]["constraint_class"]["enum"]
    require(constraint["classes"] == constraint_enum, "structural constraint schema/vocabulary drift")
    require([(row["code"], row["name"], row["interpretation"]) for row in readiness["states"]] == [(code, *READINESS[code]) for code in READINESS], "migration readiness vocabulary drift")
    require({row["code"]: row["name"] for row in friction["classes"]} == FRICTION, "adoption friction vocabulary drift")
    require(readiness["company_assessment_minimum_state"] == "R4", "company assessment threshold drift")
    return {"schemas": len(SCHEMAS), "templates": len(TEMPLATES), "readiness_states": len(READINESS), "friction_classes": len(FRICTION)}


def preservation_regression() -> dict:
    milestone = regression.validate_v11_2_milestone()
    method = json.loads((ROOT / "technical-risk/cml-method-registry.json").read_text())
    transition = json.loads((ROOT / "technical-risk/cml-v1.1/METHOD_TRANSITION.json").read_text())
    freeze = json.loads((ROOT / "technical-risk/cml-v1.1/history/HISTORICAL_BRANCH_FREEZE.json").read_text())
    require(method["active_method"]["method_version"] == VERSION, "CML v1.1 is not active")
    require(not transition["historical_records_rewritten"] and not transition["scientific_findings_changed"], "V11-1 transition boundary changed")
    require(len(freeze["branches"]) == 5 and all(row["status"] == "HISTORICAL_METHOD_BRANCH" for row in freeze["branches"]), "historical freeze changed")
    historical = regression.historical_mutations()
    require(not historical, f"historical mutation: {historical}")
    regression.validate_version_history()
    return {"active_method": VERSION, "frozen_branches": 5, "old_record_mutation_count": 0, "v11_2_accepted_sha": milestone["accepted"], "frozen_core_files": milestone["frozen_core_files"]}


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_keys(v) for v in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_keys(v) for v in value), set())
    return set()


def validate_core(core: dict, subject_class: str) -> None:
    require(core["core_version"] == "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1", "shared Evidence Core required")
    require(core["domain"] == "TECHNICAL_RISK" and core["protocol"] == "CML", "Evidence Core domain/protocol mismatch")
    require(core["policy_version"] == VERSION and core["subject_class"] == subject_class, "Evidence Core policy/subject mismatch")


def validate_dependency(record: dict) -> dict:
    schema_validate(record, "dependency")
    validate_core(record["core"], "CML_DEPENDENCY_RECORD")
    dependency = record["dependency"]
    if dependency["substitution_difficulty"] != "UNKNOWN":
        require(dependency["evidence_refs"], "known substitution difficulty requires evidence")
    return {"dependency_id": dependency["dependency_id"]}


def validate_exposure(record: dict) -> dict:
    schema_validate(record, "exposure")
    validate_core(record["core"], "CML_STRUCTURAL_EXPOSURE")
    exposure = record["structural_exposure"]
    nodes = [node for layer in ["technology", "component", "subsystem", "product", "supplier", "customer", "company", "industry"] for node in exposure[layer]]
    for node in nodes:
        if node["state"] != "UNKNOWN":
            require(node["evidence_refs"], "known structural exposure requires evidence")
    return {"exposure_id": exposure["exposure_id"], "nodes": len(nodes)}


def validate_beneficiary(record: dict) -> dict:
    schema_validate(record, "beneficiary")
    validate_core(record["core"], "CML_BENEFICIARY_MAP")
    beneficiary = record["beneficiary_map"]
    for row in beneficiary["beneficiaries"]:
        require(row["evidence_refs"], "beneficiary classification requires evidence")
        if row["commercial_customer_status"] == "CONFIRMED":
            require(row["commercial_evidence_refs"], "affected or benefiting entity is not automatically a commercial customer")
    return {"beneficiary_map_id": beneficiary["beneficiary_map_id"], "beneficiaries": len(beneficiary["beneficiaries"])}


def validate_pdre(record: dict) -> dict:
    schema_validate(record, "pdre")
    validate_core(record["core"], "CML_PDRE_RECORD")
    payload = record["pdre_record"]
    require(payload["record_kind"] == "PDRE_RECORD", "template is not an ingestible PDRE record")
    require("REPLACE_BEFORE_INGESTION" not in json.dumps(record), "unreplaced template placeholder")
    forbidden_keys = {key for key in _keys(record) if re.search(r"(^|_)(risk|opportunity|combined|aggregate)_?score$", key.lower())}
    require(not forbidden_keys, f"opaque aggregate score prohibited: {sorted(forbidden_keys)}")
    lowered = json.dumps(record).lower()
    require(not [phrase for phrase in PROHIBITED_LANGUAGE if phrase in lowered], "unsupported accusatory management language")

    evidence = {row["evidence_id"]: row for row in payload["known_evidence"]}
    require(len(evidence) == len(payload["known_evidence"]), "duplicate evidence ID")
    for row in evidence.values():
        if row["evidence_type"] in NARRATIVE_TYPES:
            require(not row["structural_fact"], "narrative or management claim promoted to structural fact")

    chain = payload["pdre"]["pdre_evidence_chain"]
    require([row["stage"] for row in chain] == STAGES, "PDRE evidence chain must contain all stages in order")
    chain_by_stage = {row["stage"]: row for row in chain}
    for row in chain:
        refs = row["evidence_refs"]
        require(set(refs) <= evidence.keys(), f"unresolved evidence reference in {row['stage']}")
        if row["status"] in {"ESTABLISHED", "PARTIAL"}:
            require(refs, f"{row['stage']} status requires evidence")
            types = {evidence[ref]["evidence_type"] for ref in refs}
            require(types & STAGE_EVIDENCE[row["stage"]], f"evidence type cannot establish {row['stage']}")
            require(not (types <= NARRATIVE_TYPES), f"narrative claims cannot establish {row['stage']}")

    readiness = payload["migration_readiness"]
    code = readiness["code"]
    require((readiness["name"], readiness["interpretation"]) == READINESS[code], "readiness code/name/interpretation mismatch")
    require(set(readiness["evidence_refs"]) <= evidence.keys(), "unresolved migration-readiness evidence")
    if readiness["supports_company_structural_assessment"]:
        require(int(code[1:]) >= 4, "only R4+ may support company-level structural assessment")
    readiness_gate = {
        "R1": (None, {"DATASHEET", "STANDARD", "ENGINEERING_VALIDATION"}),
        "R2": ("ENGINEERING_VALIDATION", STAGE_EVIDENCE["ENGINEERING_VALIDATION"]),
        "R3": ("PILOT_APPLICATION", STAGE_EVIDENCE["PILOT_APPLICATION"]),
        "R4": ("QUALIFICATION", STAGE_EVIDENCE["QUALIFICATION"]),
        "R5": ("FIELD_DEPLOYMENT", STAGE_EVIDENCE["FIELD_DEPLOYMENT"]),
        "R6": ("FIELD_DEPLOYMENT", {"OPERATING_HISTORY"}),
        "R7": ("MULTI_USER_MULTI_OEM_REPLICATION", STAGE_EVIDENCE["MULTI_USER_MULTI_OEM_REPLICATION"]),
    }
    if code != "R0":
        stage, permitted = readiness_gate[code]
        require(readiness["evidence_refs"], f"{code} requires evidence")
        types = {evidence[ref]["evidence_type"] for ref in readiness["evidence_refs"]}
        require(types & permitted, f"evidence does not support {code}")
        if stage:
            require(chain_by_stage[stage]["status"] == "ESTABLISHED", f"{code} requires established {stage}")
    if payload["pdre"]["status"] == "CONFIRMED":
        require(int(code[1:]) >= 4 and chain_by_stage["QUALIFICATION"]["status"] == "ESTABLISHED", "confirmed PDRE requires a qualified viable path")

    friction = payload["adoption_friction"]
    require({row["code"] for row in friction} == set(FRICTION), "all AF1-AF10 dimensions required exactly once")
    for row in friction:
        require(row["name"] == FRICTION[row["code"]], "friction code/name mismatch")
        if row["state"] not in {"UNKNOWN", "NOT_APPLICABLE"}:
            require(row["evidence_refs"], "known friction cannot be inferred from UNKNOWN")
            require(set(row["evidence_refs"]) <= evidence.keys(), "unresolved friction evidence")

    for dimension in payload["path_dependency"].values():
        if dimension["status"] == "OBSERVED":
            require(dimension["evidence_refs"], "observed path dependency requires evidence")
    for constraint in payload["structural_constraints"]:
        if constraint["status"] == "OBSERVED":
            require(constraint["evidence_refs"], "observed structural constraint requires evidence")

    exposure_record = {"core": {**record["core"], "subject_class": "CML_STRUCTURAL_EXPOSURE"}, "structural_exposure": payload["structural_exposure"]}
    beneficiary_record = {"core": {**record["core"], "subject_class": "CML_BENEFICIARY_MAP"}, "beneficiary_map": payload["beneficiary_map"]}
    validate_exposure(exposure_record)
    validate_beneficiary(beneficiary_record)
    require(payload["structural_exposure"]["exposure_id"] != payload["beneficiary_map"]["beneficiary_map_id"], "structural exposure cannot be reused as beneficiary map")

    return {"pdre_id": payload["identity"]["pdre_id"], "readiness": code, "evidence_items": len(evidence), "opaque_score": False}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdre", action="append", type=Path, default=[])
    parser.add_argument("--dependency", action="append", type=Path, default=[])
    parser.add_argument("--exposure", action="append", type=Path, default=[])
    parser.add_argument("--beneficiary", action="append", type=Path, default=[])
    args = parser.parse_args()
    result = {"preservation": preservation_regression(), "framework": framework_integrity(), "records": []}
    for kind, paths, validator in [
        ("pdre", args.pdre, validate_pdre), ("dependency", args.dependency, validate_dependency),
        ("exposure", args.exposure, validate_exposure), ("beneficiary", args.beneficiary, validate_beneficiary),
    ]:
        result["records"].extend({"kind": kind, **validator(load(path.resolve()))} for path in paths)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
