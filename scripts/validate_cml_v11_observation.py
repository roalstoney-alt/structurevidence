#!/usr/bin/env python3
"""Validate CML v1.1 Task V11-3 observation and commercial-boundary objects."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import jsonschema
from referencing import Registry, Resource

import cml_v11_regression as regression

ROOT = Path(__file__).resolve().parents[1]
VERSION = "CML_v1.1"
SCHEMA_DIR = ROOT / "technical-risk/cml-v1.1/schema"
VOCAB_DIR = ROOT / "technical-risk/cml-v1.1/vocabulary"
TEMPLATE_DIR = ROOT / "technical-risk/cml-v1.1/templates"
SCHEMAS = {
    "trigger": SCHEMA_DIR / "trigger-event.schema.json",
    "response": SCHEMA_DIR / "real-world-response.schema.json",
    "market": SCHEMA_DIR / "market-validation.schema.json",
    "failure": SCHEMA_DIR / "migration-failure.schema.json",
    "public": SCHEMA_DIR / "public-pdre-research-object.schema.json",
}
TEMPLATES = {kind: TEMPLATE_DIR / f"{name}.template.json" for kind, name in {
    "trigger":"trigger-event", "response":"real-world-response", "market":"market-validation",
    "failure":"migration-failure", "public":"public-pdre-research-object",
}.items()}
DEPENDENCY_SCHEMAS = [
    SCHEMA_DIR / "pdre-record.schema.json", SCHEMA_DIR / "dependency-record.schema.json",
    SCHEMA_DIR / "structural-exposure.schema.json", SCHEMA_DIR / "beneficiary-map.schema.json",
    ROOT / "evidence/core/schema/evidence_core_record.schema.json",
]
NARRATIVE_TYPES = {"EXECUTIVE_STATEMENT", "CEO_STATEMENT", "MANAGEMENT_STATEMENT", "MARKETING_CLAIM", "INTERVIEW", "ANALYST_OPINION"}
TECHNICAL_RESPONSE_TYPES = {"SUPPLIER_CHANGE", "PRODUCT_REDESIGN", "MOTOR_ARCHITECTURE_CHANGE", "CONTROLLER_CHANGE", "SECOND_SOURCE_QUALIFIED", "MANUFACTURING_CHANGE", "CAPEX_INCREASE", "LEGACY_LINE_CLOSED"}
PRIVATE_KEYS = {"customer_bom", "private_customer_bom", "private_pricing", "customer_pricing", "private_drawings", "customer_drawings", "private_qualification_data", "customer_qualification_data"}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def registry() -> Registry:
    result = Registry()
    for path in [*SCHEMAS.values(), *DEPENDENCY_SCHEMAS]:
        schema = load(path)
        schema["$id"] = path.as_uri()
        result = result.with_resource(path.as_uri(), Resource.from_contents(schema))
    return result


def schema_validate(value: dict, kind: str) -> None:
    path = SCHEMAS[kind]
    schema = load(path)
    schema["$id"] = path.as_uri()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema, registry=registry(), format_checker=jsonschema.FormatChecker()).validate(value)


def validate_core(core: dict, subject_class: str) -> None:
    require(core["core_version"] == "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1", "existing Evidence Core required")
    require(core["domain"] == "TECHNICAL_RISK" and core["protocol"] == "CML", "Evidence Core domain/protocol mismatch")
    require(core["policy_version"] == VERSION and core["subject_class"] == subject_class, "Evidence Core policy/subject mismatch")


def all_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(all_keys(v) for v in value.values()), set())
    if isinstance(value, list):
        return set().union(*(all_keys(v) for v in value), set())
    return set()


def evidence_map(rows: list[dict]) -> dict[str, dict]:
    result = {row["source_ref"]: row for row in rows}
    require(len(result) == len(rows), "duplicate evidence source reference")
    return result


def non_narrative(refs: list[str], evidence: dict[str, dict]) -> bool:
    return any(evidence[ref]["tier"] != "TIER_5" and evidence[ref]["evidence_type"] not in NARRATIVE_TYPES for ref in refs)


def framework_integrity() -> dict:
    for kind, path in TEMPLATES.items():
        schema_validate(load(path), kind)
    trigger = load(VOCAB_DIR / "TRIGGER_TYPES.json")
    response = load(VOCAB_DIR / "REAL_WORLD_RESPONSE.json")
    market = load(VOCAB_DIR / "MARKET_VALIDATION.json")
    failure = load(VOCAB_DIR / "MIGRATION_FAILURE.json")
    tiers = load(VOCAB_DIR / "EVIDENCE_PRIORITY.json")
    paths = load(VOCAB_DIR / "COMMERCIAL_PATHS.json")
    boundary = load(ROOT / "technical-risk/cml-v1.1/publication/PUBLIC_PAID_BOUNDARY.json")
    require(len(trigger["types"]) == 13 and len(response["response_types"]) == 10, "trigger/response vocabulary drift")
    require(market["states"] == ["VALIDATED","PARTIALLY_VALIDATED","REJECTED","SUPERSEDED","UNRESOLVED"], "market states drift")
    require(len(failure["classes"]) == 10 and [row["code"] for row in tiers["tiers"]] == [f"TIER_{n}" for n in range(1,6)], "failure/evidence vocabulary drift")
    trigger_schema=load(SCHEMAS["trigger"])["properties"]["trigger_event"]["properties"]
    response_schema=load(SCHEMAS["response"])["properties"]["real_world_response"]["properties"]
    market_schema=load(SCHEMAS["market"])["properties"]["market_validation"]["properties"]
    failure_schema=load(SCHEMAS["failure"])["properties"]["migration_failure"]["properties"]
    require(trigger_schema["trigger_type"]["enum"] == trigger["types"], "trigger schema/vocabulary drift")
    require(response_schema["response_type"]["enum"] == response["response_types"], "response schema/vocabulary drift")
    require(response_schema["migration_lag"]["properties"]["classification"]["enum"] == response["migration_lag_classifications"], "migration-lag schema/vocabulary drift")
    require(market_schema["current_state"]["enum"] == market["states"], "market schema/vocabulary drift")
    require(failure_schema["FAILURE_CLASS"]["enum"] == failure["classes"], "failure schema/vocabulary drift")
    require(paths["beneficiary_path"][0] == "PUBLIC_PDRE" and paths["incumbent_path"][0] == "PUBLIC_RESEARCH", "commercial paths collapsed")
    require(not boundary["pricing_in_scope"] and not boundary["website_or_checkout_change"], "public/paid boundary drift")
    return {"schemas":5,"templates":5,"trigger_types":13,"response_types":10,"evidence_tiers":5}


def preservation_regression() -> dict:
    regression.validate_v11_1_milestone()
    regression.validate_v11_2_milestone()
    regression.validate_version_history()
    historical = regression.historical_mutations()
    frozen = regression.frozen_v11_2_mutations()
    require(not historical, f"historical mutation: {historical}")
    require(not frozen, f"V11-2 frozen core mutation: {frozen}")
    return {"old_record_mutation_count":0,"v11_2_frozen_core_files":len(regression.frozen_v11_2_paths())}


def validate_trigger(record: dict) -> dict:
    schema_validate(record, "trigger")
    validate_core(record["core"], "CML_TRIGGER_EVENT")
    event = record["trigger_event"]
    evidence = evidence_map(event["evidence_basis"])
    refs = set(event["source_refs"])
    require(refs == set(evidence), "trigger source/evidence mismatch")
    require(set(event["effective_at_evidence_refs"]) <= refs and set(event["known_at_evidence_refs"]) <= refs, "unresolved clock evidence")
    require(event["known_at_evidence_refs"], "knowledge time requires independent evidence registration")
    require(event["effective_at_evidence_refs"], "event time requires evidence")
    if event["occurrence_status"] == "OBSERVED":
        require(refs and non_narrative(list(refs), evidence), "narrative evidence cannot establish a trigger occurrence")
    return {"trigger_id":event["trigger_id"],"dual_clock":True}


def validate_response(record: dict) -> dict:
    schema_validate(record, "response")
    validate_core(record["core"], "CML_REAL_WORLD_RESPONSE")
    response = record["real_world_response"]
    evidence = evidence_map(response["evidence_basis"])
    refs = set(response["source_refs"])
    require(refs == set(evidence) and refs, "observable response requires reciprocal evidence")
    require(parse_time(response["known_at"]) >= parse_time(response["observed_at"]), "response knowledge predates observation")
    if response["response_type"] in TECHNICAL_RESPONSE_TYPES:
        require(non_narrative(list(refs), evidence), "narrative evidence cannot establish technical deployment or qualification")
    lag = response["migration_lag"]
    if lag["enterprise_adoption_time"]:
        require(parse_time(lag["enterprise_adoption_time"]) >= parse_time(lag["pdre_time"]), "negative migration lag")
    if lag["classification"] in {"FAST_ADOPTER","NORMAL_ADOPTER","LATE_ADOPTER"}:
        require(lag["classification_policy_ref"], "adopter classification requires configured domain policy")
    else:
        require(lag["classification"] in {"NO_OBSERVABLE_MIGRATION","UNKNOWN","POLICY_NOT_CONFIGURED"}, "unsupported migration-lag classification")
    for inference in response["secondary_inferences"]:
        require(inference["evidence_refs"] and set(inference["evidence_refs"]) <= refs, "secondary inference requires separate evidence")
        require(non_narrative(inference["evidence_refs"], evidence), "narrative evidence cannot establish management or economic inference")
    return {"response_id":response["response_id"],"migration_lag":lag["classification"]}


def original_publication_digest(original: dict) -> str:
    return canonical_hash({key:original[key] for key in ["publication_ref","publication_time","original_hypothesis","original_state"]})


def validate_market(record: dict) -> dict:
    schema_validate(record, "market")
    validate_core(record["core"], "CML_MARKET_VALIDATION")
    value = record["market_validation"]
    original = value["original_publication"]
    require(original["publication_hash"] == original_publication_digest(original), "original publication content/hash mismatch")
    state = original["original_state"]
    publication_time = parse_time(original["publication_time"])
    seen = set()
    for event in value["validation_events"]:
        require(event["event_id"] not in seen, "duplicate validation event")
        seen.add(event["event_id"])
        require(event["prior_state"] == state, "validation history does not append from prior state")
        require(parse_time(event["known_at"]) >= publication_time, "later outcome back-projected into prior knowledge")
        state = event["new_state"]
    require(value["current_state"] == state, "current state differs from append-only validation history")
    history_refs = [row["event_ref"] for row in value["revision_history"]]
    require(value["revision_history"][0]["event_ref"] is None, "first revision must preserve original publication")
    require(set(seen) <= set(history_refs), "validation event missing from revision history")
    return {"validation_id":value["validation_id"],"current_state":state,"events":len(seen)}


def validate_failure(record: dict) -> dict:
    schema_validate(record, "failure")
    validate_core(record["core"], "CML_MIGRATION_FAILURE")
    failure = record["migration_failure"]
    require(parse_time(failure["known_at"]) >= parse_time(failure["effective_at"]), "failure knowledge predates event")
    require(all(row["failure_preserved"] for row in failure["revision_history"]), "failed migration removed from revision history")
    return {"failure_id":failure["failure_id"],"preserved":True}


def validate_public(record: dict) -> dict:
    schema_validate(record, "public")
    validate_core(record["core"], "CML_PUBLIC_PDRE_RESEARCH_OBJECT")
    value = record["public_pdre_research_object"]
    keys = {key.lower() for key in all_keys(record)}
    require(not (keys & PRIVATE_KEYS), f"private customer data in public object: {sorted(keys & PRIVATE_KEYS)}")
    score_keys = {key for key in keys if re.search(r"(^|_)(market|risk|opportunity|aggregate|combined)_?score$", key)}
    require(not score_keys, f"opaque score prohibited: {sorted(score_keys)}")
    require(value["PDRE_ID"] == record["core"]["subject_id"], "public PDRE subject mismatch")
    require(not value["COMMERCIAL_PATHS"]["affected_entity_is_paying_customer"], "affected entity cannot be automatic paying customer")
    require(not value["COMMERCIAL_PATHS"]["legacy_incumbent_automatic_priority"], "legacy incumbent cannot be automatic priority")
    for row in value["KNOWN_EVIDENCE"]["value"]:
        if row["evidence_type"] in {"MARKETING_CLAIM","MANAGEMENT_STATEMENT","INTERVIEW","ANALYST_OPINION"}:
            require(not row["structural_fact"], "narrative evidence promoted to structural fact")
    return {"pdre_id":value["PDRE_ID"],"public_only":True,"private_data":False,"opaque_score":False}


def main() -> None:
    parser=argparse.ArgumentParser()
    for kind in SCHEMAS: parser.add_argument(f"--{kind}",action="append",type=Path,default=[])
    args=parser.parse_args()
    validators={"trigger":validate_trigger,"response":validate_response,"market":validate_market,"failure":validate_failure,"public":validate_public}
    result={"preservation":preservation_regression(),"framework":framework_integrity(),"records":[]}
    for kind,validator in validators.items():
        result["records"].extend({"kind":kind,**validator(load(path.resolve()))} for path in getattr(args,kind))
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__": main()
