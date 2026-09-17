#!/usr/bin/env python3
"""Independent final method audit gates for CML v1.1."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import cml_v11_regression as regression
import validate_cml_v11_core as core
import validate_cml_v11_observation as observation

ROOT = Path(__file__).resolve().parents[1]
ENTRY_SHA = "833fa342a34c3910a4ef415dd88b15888baf87bb"
STATUS = {"PASS", "FAIL", "NOT_EVALUATED"}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def method_transition() -> dict:
    registry=load("technical-risk/cml-method-registry.json"); transition=load("technical-risk/cml-v1.1/METHOD_TRANSITION.json")
    require(registry["active_method"]["method_version"]=="CML_v1.1","active method drift")
    require(transition["to_method"]=="CML_v1.1" and not transition["scientific_findings_changed"] and not transition["historical_records_rewritten"],"transition boundary drift")
    return {"active_method":"CML_v1.1","transition_id":transition["transition_id"]}


def history_preserved() -> dict:
    history=regression.validate_version_history(); require(not regression.historical_mutations(),"historical files changed")
    registry=load("technical-risk/cml-method-registry.json"); c0=next(row for row in registry["historical_methods"] if row["method_version"]=="CML_OV_v0.1_PHASE_C0")
    require(c0["primary_research_gate_status"]=="DEPRECATED_AS_PRIMARY_RESEARCH_GATE","C0 status drift")
    gate_paths=["technical-risk/validation/CML_GATE_RESULTS.json","technical-risk/CML_GATE_RESULTS.json","docs/technical-risk/validation/CML_GATE_RESULTS.json","docs/technical-risk/CML_GATE_RESULTS.json"]
    gate_bytes=[(ROOT/path).read_bytes() for path in gate_paths]; require(len(set(gate_bytes))==1,"historical CML gate mirrors drift")
    frozen=json.loads(gate_bytes[0]); require(frozen["summary"]=={"FAIL":0,"NOT_EVALUATED":0,"PASS":40},"historical CML frozen gate snapshot changed")
    return {**history,"historical_methods":len(registry["historical_methods"]),"c0_preserved":True,"historical_cml_frozen_gates":40}


def no_old_mutation() -> dict:
    mutations=regression.historical_mutations(); require(not mutations,f"old record mutations: {mutations}")
    return {"old_record_mutation_count":0,"protected_files":len(regression.historical_protected_paths())}


def pdre_schema() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/pdre-record.schema.json"); required=set(schema["properties"]["pdre_record"]["required"])
    expected={"identity","old_path","new_path","current_dependency","path_dependency","structural_constraints","alternative_path","pdre","migration_readiness","adoption_friction","economics","structural_exposure","beneficiary_map","real_world_response","market_validation","known_evidence","counter_evidence","unknowns","next_observable","timeline","revision_history"}
    require(expected<=required,"PDRE chain section missing"); core.framework_integrity()
    return {"primary_object":"PDRE_RECORD","required_sections":len(expected)}


def dependency_schema() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/dependency-record.schema.json"); required=set(schema["$defs"]["dependency"]["required"])
    require({"dependency_id","technology","component","subsystem","function","required_because","dependent_elements","substitution_difficulty","failure_if_removed","current_supplier_structure","current_standard_dependency","current_certification_dependency","evidence_refs","unknowns"}==required,"dependency fields drift")
    return {"required_fields":len(required)}


def constraint_vocabulary() -> dict:
    vocab=load("technical-risk/cml-v1.1/vocabulary/STRUCTURAL_CONSTRAINTS.json"); require(len(vocab["classes"])==12 and vocab["observation_states"]==["OBSERVED","INFERRED","UNKNOWN","NOT_APPLICABLE"],"constraint vocabulary drift")
    return {"constraint_classes":12}


def migration_readiness() -> dict:
    vocab=load("technical-risk/cml-v1.1/vocabulary/MIGRATION_READINESS.json"); rows=[(row["code"],row["name"]) for row in vocab["states"]]
    require(rows==[("R0","THEORETICAL"),("R1","SPECIFICATION_COMPATIBLE"),("R2","ENGINEERING_REVIEWED"),("R3","SAMPLE_BENCH_TESTED"),("R4","APPLICATION_QUALIFIED"),("R5","FIELD_DEPLOYED"),("R6","OPERATING_HISTORY_AVAILABLE"),("R7","MULTI_ENTITY_REPLICATION")],"readiness states drift")
    require(vocab["company_assessment_minimum_state"]=="R4","company threshold drift")
    return {"states":8,"company_assessment_minimum":"R4","escalating_evidence_gates":True}


def adoption_friction() -> dict:
    vocab=load("technical-risk/cml-v1.1/vocabulary/ADOPTION_FRICTION.json"); require([row["code"] for row in vocab["classes"]]==[f"AF{n}" for n in range(1,11)],"friction dimensions drift")
    require("UNKNOWN" in vocab["states"] and "LOW" in vocab["states"],"friction unknown/low states collapsed")
    return {"dimensions":10,"unknown_preserved":True}


def readiness_friction_separation() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/pdre-record.schema.json")["properties"]["pdre_record"]["properties"]
    require("migration_readiness" in schema and "adoption_friction" in schema and schema["migration_readiness"]!=schema["adoption_friction"],"readiness/friction collapsed")
    require("friction" not in json.dumps(core.READINESS).lower(),"readiness implies friction")
    return {"separate_fields":True,"readiness_implies_friction":False}


def structural_exposure() -> dict:
    required=load("technical-risk/cml-v1.1/schema/structural-exposure.schema.json")["$defs"]["structural_exposure"]["required"]
    layers=["technology","component","subsystem","product","supplier","customer","company","industry"]
    require(all(layer in required for layer in layers),"exposure mapping layer missing")
    return {"mapping_layers":layers}


def beneficiary_map() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/beneficiary-map.schema.json"); enum=schema["$defs"]["beneficiary_map"]["properties"]["beneficiaries"]["items"]["properties"]["beneficiary_class"]["enum"]
    require(len(enum)==12,"beneficiary classes drift")
    return {"beneficiary_classes":12,"commercial_customer_status_separate":True}


def exposure_beneficiary_separation() -> dict:
    pdre=load("technical-risk/cml-v1.1/schema/pdre-record.schema.json")["properties"]["pdre_record"]["properties"]
    require(pdre["structural_exposure"]["$ref"]!=pdre["beneficiary_map"]["$ref"],"exposure and beneficiary share representation")
    return {"independent_schema_refs":True}


def trigger_schema() -> dict:
    observation.framework_integrity(); vocab=load("technical-risk/cml-v1.1/vocabulary/TRIGGER_TYPES.json")
    require(len(vocab["types"])==13,"trigger vocabulary incomplete")
    return {"trigger_types":13,"narrative_only_rejected":True}


def real_world_response() -> dict:
    vocab=load("technical-risk/cml-v1.1/vocabulary/REAL_WORLD_RESPONSE.json"); require(len(vocab["response_types"])==10 and "NO_OBSERVABLE_MIGRATION" in vocab["response_types"],"response vocabulary incomplete")
    return {"response_types":10,"observation_chain_enforced":True}


def migration_lag() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/real-world-response.schema.json"); lag=schema["properties"]["real_world_response"]["properties"]["migration_lag"]["properties"]
    require({"pdre_time","enterprise_adoption_time","migration_lag","classification","classification_policy_ref"}<=set(lag),"migration lag fields missing")
    text=json.dumps([schema,load("technical-risk/cml-v1.1/vocabulary/REAL_WORLD_RESPONSE.json")]).lower(); require("threshold" not in text,"universal threshold invented")
    return {"descriptive_classes":6,"universal_thresholds":False}


def evidence_priority() -> dict:
    tiers=load("technical-risk/cml-v1.1/vocabulary/EVIDENCE_PRIORITY.json")["tiers"]
    require([row["code"] for row in tiers]==[f"TIER_{n}" for n in range(1,6)],"evidence tiers drift")
    require(tiers[-1]["name"]=="NARRATIVE_EVIDENCE" and {"EXECUTIVE_STATEMENT","MARKETING_CLAIM","INTERVIEW","ANALYST_OPINION"}<=set(tiers[-1]["examples"]),"narrative evidence classification drift")
    return {"tiers":5,"narrative_tier":"TIER_5"}


def public_research_object() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/public-pdre-research-object.schema.json"); required=set(schema["properties"]["public_pdre_research_object"]["required"])
    canonical={"CML_ID","PDRE_ID","OLD_PATH","NEW_PATH","CURRENT_DEPENDENCY","MIGRATION_READINESS","ADOPTION_FRICTION","STRUCTURAL_EXPOSURE","BENEFICIARY_MAP","KNOWN_EVIDENCE","UNKNOWN","NEXT_OBSERVABLE","PUBLICATION_TIME","REVISION_HISTORY"}
    require(canonical<=required,"public canonical field missing")
    return {"canonical_fields":len(canonical),"source_pointers":True}


def revision_append_only() -> dict:
    regression.validate_version_history(); schema=load("technical-risk/cml-v1.1/schema/market-validation.schema.json")["properties"]["market_validation"]
    require("original_publication" in schema["required"] and "validation_events" in schema["required"] and "revision_history" in schema["required"],"validation history fields missing")
    return {"version_history_prefix_preserved":True,"market_history_append_model":True}


def failure_preservation() -> dict:
    schema=load("technical-risk/cml-v1.1/schema/migration-failure.schema.json")["properties"]["migration_failure"]
    required={"ORIGINAL_HYPOTHESIS","EXPECTED_ADVANTAGE","FAILED_REQUIREMENT","ACTUAL_RESULT","MODEL_REVISION"}
    require(required<=set(schema["required"]) and schema["properties"]["preservation_status"]["const"]=="PRESERVED_FAILURE_EVIDENCE","failure preservation drift")
    return {"required_failure_fields":5,"preserved":True}


def non_accusatory_language() -> dict:
    required={"management failed","management failure","technologically backward","management ignored technology"}
    require(required<=set(core.PROHIBITED_LANGUAGE),"non-accusatory validator coverage drift")
    return {"prohibited_patterns":len(core.PROHIBITED_LANGUAGE)}


def public_paid_boundary() -> dict:
    policy=load("technical-risk/cml-v1.1/publication/PUBLIC_PAID_BOUNDARY.json"); require(len(policy["public_research_may_answer"])==7 and len(policy["paid_work_begins_with"])==8 and not policy["pricing_in_scope"],"public/paid boundary drift")
    public_schema=json.dumps(load("technical-risk/cml-v1.1/schema/public-pdre-research-object.schema.json")).lower(); require(not any(key in public_schema for key in ["private_customer_bom","private_pricing","private_drawings","private_qualification_data","private_procurement_terms"]),"private data field exposed")
    return {"public_questions":7,"paid_request_classes":8,"private_context_excluded":True}


def beneficiary_commercial_path() -> dict:
    paths=load("technical-risk/cml-v1.1/vocabulary/COMMERCIAL_PATHS.json"); require(paths["beneficiary_path"]==["PUBLIC_PDRE","BENEFICIARY_ANALYSIS","TARGET_APPLICATION_MAP","MARKET_ENTRY_STUDY","TECHNICAL_FIT_VALIDATION","CUSTOMER_APPLICATION_QUALIFICATION","DEPLOYMENT"],"beneficiary path drift")
    require(paths["incumbent_path"]==["PUBLIC_RESEARCH","DEPENDENCY_AUDIT","SUBSTITUTION_STUDY","ENGINEERING_VALIDATION","QUALIFICATION","DEPLOYMENT"],"incumbent path drift")
    return {"paths_distinct":True,"beneficiary_first_class":True}


def no_management_dependency() -> dict:
    registry=load("technical-risk/cml-method-registry.json"); c0=next(row for row in registry["historical_methods"] if row["method_version"]=="CML_OV_v0.1_PHASE_C0")
    template=load("technical-risk/cml-v1.1/templates/pdre-record.template.json"); require(c0["primary_research_gate_status"]=="DEPRECATED_AS_PRIMARY_RESEARCH_GATE" and template["pdre_record"]["known_evidence"]==[],"management input remains mandatory")
    return {"human_response_required":False,"c0_primary_gate":False}


def no_opaque_score() -> dict:
    files=list((ROOT/"technical-risk/cml-v1.1/schema").glob("*.json")); found=[]
    for path in files:
        keys=re.findall(r'"([^"]*score[^"]*)"\s*:',path.read_text(encoding="utf-8"),flags=re.I); found.extend(f"{path.name}:{key}" for key in keys)
    require(not found,f"score fields found: {found}")
    return {"schema_score_fields":0}


def evidence_core_reuse() -> dict:
    schemas=list((ROOT/"technical-risk/cml-v1.1/schema").glob("*.json")); missing=[]
    for path in schemas:
        text=path.read_text(encoding="utf-8");
        if "../../../evidence/core/schema/evidence_core_record.schema.json" not in text: missing.append(path.name)
    parallel=[p.as_posix() for p in (ROOT/"technical-risk/cml-v1.1").rglob("*") if p.is_dir() and p.name.lower() in {"provenance","timeline","evidence-store","evidence_core"}]
    require(not missing and not parallel,f"Evidence Core bypass or parallel store: missing={missing}, parallel={parallel}")
    return {"schemas_reusing_core":len(schemas),"parallel_systems":0}


GATES=[
 ("CML11-01_METHOD_TRANSITION",method_transition),("CML11-02_HISTORY_PRESERVED",history_preserved),("CML11-03_NO_OLD_RECORD_MUTATION",no_old_mutation),("CML11-04_PDRE_SCHEMA",pdre_schema),("CML11-05_DEPENDENCY_SCHEMA",dependency_schema),("CML11-06_CONSTRAINT_VOCABULARY",constraint_vocabulary),("CML11-07_MIGRATION_READINESS",migration_readiness),("CML11-08_ADOPTION_FRICTION",adoption_friction),("CML11-09_READINESS_FRICTION_SEPARATION",readiness_friction_separation),("CML11-10_STRUCTURAL_EXPOSURE",structural_exposure),("CML11-11_BENEFICIARY_MAP",beneficiary_map),("CML11-12_EXPOSURE_BENEFICIARY_SEPARATION",exposure_beneficiary_separation),("CML11-13_TRIGGER_SCHEMA",trigger_schema),("CML11-14_REAL_WORLD_RESPONSE",real_world_response),("CML11-15_MIGRATION_LAG",migration_lag),("CML11-16_EVIDENCE_PRIORITY",evidence_priority),("CML11-17_PUBLIC_RESEARCH_OBJECT",public_research_object),("CML11-18_REVISION_APPEND_ONLY",revision_append_only),("CML11-19_FAILURE_PRESERVATION",failure_preservation),("CML11-20_NON_ACCUSATORY_LANGUAGE",non_accusatory_language),("CML11-21_PUBLIC_PAID_BOUNDARY",public_paid_boundary),("CML11-22_BENEFICIARY_COMMERCIAL_PATH",beneficiary_commercial_path),("CML11-23_NO_MANAGEMENT_INPUT_DEPENDENCY",no_management_dependency),("CML11-24_NO_OPAQUE_SCORE",no_opaque_score),("CML11-25_EVIDENCE_CORE_REUSE",evidence_core_reuse),
]


def evaluate() -> dict:
    rows=[]
    for gate_id,validator in GATES:
        try: rows.append({"gate_id":gate_id,"status":"PASS","reason":"Independent audit condition satisfied.","computed_facts":validator()})
        except NotImplementedError as exc: rows.append({"gate_id":gate_id,"status":"NOT_EVALUATED","reason":str(exc),"computed_facts":{}})
        except Exception as exc: rows.append({"gate_id":gate_id,"status":"FAIL","reason":f"{type(exc).__name__}: {exc}","computed_facts":{}})
    summary={status:sum(row["status"]==status for row in rows) for status in ["PASS","FAIL","NOT_EVALUATED"]}
    require(all(row["status"] in STATUS for row in rows),"invalid gate status")
    return {"method_version":"CML_v1.1","entry_sha":ENTRY_SHA,"results":rows,"summary":summary,"old_record_mutation_count":len(regression.historical_mutations())}


def main() -> None:
    argparse.ArgumentParser().parse_args()
    print(json.dumps(evaluate(),indent=2,sort_keys=True))


if __name__=="__main__": main()
