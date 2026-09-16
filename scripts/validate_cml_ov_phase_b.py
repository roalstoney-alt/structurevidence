#!/usr/bin/env python3
"""Wave 1 desk-evidence gates. Read-only unless --write-results is explicit.

PASS means the stated evidence discipline holds, never that an opportunity exists.
NOT_EVALUATED records a substantive gap instead of manufacturing a finding.
"""
import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import jsonschema
from referencing import Registry, Resource

from test_cml_v01 import ROOT, digest, flatten_keys, import_adapter, load

BASE = "ad3206fff3c8d8375b1c9e087df44bd9c7336927"
VERSION = "CML_OV_v0.1_PHASE_B"
SCHEMA = "technical-risk/opportunity-validation/schema/"
TARGETS = {"OV-01": "amphenol-10081811-101-07lf", "OV-03": "amphenol-rf-095-725-134-006"}
FILES = dict(zip(
    ["sources", "usage", "solution", "inefficiency", "counter_evidence", "hypotheses", "tmc", "ttq", "human_targets", "assessment"],
    ["01_SOURCE_REGISTER.json", "02_CURRENT_USAGE_EVIDENCE.json", "03_CURRENT_SOLUTION_MAP.json", "04_INEFFICIENCY_EVIDENCE.json", "05_COUNTER_EVIDENCE.json", "06_IMPROVEMENT_HYPOTHESES.json", "07_TMC_VARIABLE_MAP.json", "08_TTQ_VARIABLE_MAP.json", "09_HUMAN_VALIDATION_TARGETS.json", "10_PHASE_B_ASSESSMENT.json"]))
DIMENSIONS = "UNIT_COST TOTAL_BOM_COST ENGINEERING_HOURS REDESIGN_COST QUALIFICATION_COST TEST_COST TOOLING_COST QUALIFICATION_TIME DESIGN_ITERATION_TIME LEAD_TIME MOQ INVENTORY_REQUIREMENT SUPPLIER_COUNT SINGLE_SOURCE_DEPENDENCY MANUFACTURABILITY ASSEMBLY_COMPLEXITY YIELD RELIABILITY CERTIFICATION_BURDEN SERVICEABILITY REPAIRABILITY FUTURE_LIFECYCLE_RISK".split()
TMC = "PART_COST_DELTA ENGINEERING_COST PROTOTYPE_COST TOOLING_COST TEST_COST QUALIFICATION_COST CERTIFICATION_COST INVENTORY_COST DOWNTIME_RISK CHANGE_MANAGEMENT_COST".split()
TTQ = "CANDIDATE_IDENTIFICATION PAPER_SCREENING DESIGN_ADAPTATION PROTOTYPE BENCH_TEST ENVIRONMENTAL_TEST CERTIFICATION CUSTOMER_VALIDATION PRODUCTION_APPROVAL".split()


class NotEvaluated(Exception):
    pass


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "timezone required")
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folder(target):
    return ROOT / "technical-risk/records" / TARGETS[target] / "opportunity-validation"


def context(target):
    base = folder(target)
    return {"target": target, "folder": base, "record": json.loads((base / f"{target}.v0.2.json").read_text()),
            "package": {k: json.loads((base / "phase-b" / f).read_text()) for k, f in FILES.items()}}


def schema_validate(value, name):
    paths = [ROOT / SCHEMA / "phase-b-package.schema.json", ROOT / SCHEMA / "phase-b-record.schema.json", ROOT / "evidence/core/schema/evidence_core_record.schema.json"]
    registry = Registry()
    for path in paths:
        resource = Resource.from_contents(json.loads(path.read_text()))
        registry = registry.with_resource(path.as_uri(), resource)
    path = ROOT / SCHEMA / name
    schema = json.loads(path.read_text())
    schema["$id"] = path.as_uri()
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema, registry=registry, format_checker=jsonschema.FormatChecker()).validate(value)


def claims(c):
    return [v for k in ["usage", "solution", "inefficiency", "counter_evidence"] for v in c["package"][k]["claims"]]


def sources(c):
    return {s["source_id"]: s for s in c["package"]["sources"]["sources"]}


def frozen_changes():
    return subprocess.check_output(["git", "diff", "--name-only", BASE, "--"], cwd=ROOT, text=True).splitlines()


def baseline_integrity(c):
    require(not frozen_changes(), "frozen tracked files changed")
    oldpath = c["folder"] / f'{c["target"]}.v0.1.json'
    old = json.loads(oldpath.read_text())
    p = c["record"]["opportunity_validation"]
    require(p["predecessor_record_id"] == old["core"]["record_id"] and p["predecessor_record_hash"] == old["core"]["record_hash"], "directional predecessor mismatch")
    require(p["predecessor_path"] == oldpath.relative_to(ROOT).as_posix(), "predecessor path")
    for key in ["baseline", "problem_persistence", "current_solution_audit", "solution_improvement_potential", "client_scope", "public_private_boundary", "freshness_state", "freshness_reason", "freshness_rule_type"]:
        require(p[key] == old["opportunity_validation"][key], "frozen initialization field changed: " + key)
    for key in ["core_version", "domain", "protocol", "subject_id", "subject_class"]:
        require(c["record"]["core"][key] == old["core"][key], "shared core identity changed")
    require(c["record"]["core"]["record_id"] == f'SE.CML.OV.{c["target"]}.v0.2', "successor ID")
    return {"baseline_commit": BASE, "predecessor_hash": p["predecessor_record_hash"], "tracked_mutations": []}


def source_provenance(c):
    schema_validate(c["package"], "phase-b-package.schema.json")
    schema_validate(c["record"], "phase-b-record.schema.json")
    ss = sources(c)
    all_claims = claims(c)
    ids = {v["claim_id"] for v in all_claims}
    require(len(ss) == len(c["package"]["sources"]["sources"]), "duplicate source ID")
    require(len(ids) == len(all_claims), "duplicate claim ID")
    require(c["package"]["sources"]["target"] == c["target"] == c["package"]["assessment"]["target"], "target mismatch")
    for v in all_claims:
        require(set(v["source_refs"]) <= ss.keys(), "unresolved source reference")
        require(v["claim_type"] == "UNKNOWN" or v["source_refs"], "substantive finding has no evidence")
        if v["customer_pain"] != "UNKNOWN":
            require(v["claim_type"] == "DIRECT_PUBLIC_EVIDENCE" and v["evidence_basis"] == "APPLICATION_DOCUMENT", "pain cannot be inferred from lifecycle")
    for sid, s in ss.items():
        require(s["host"] == urlparse(s["url"]).hostname, "host is not URL host")
        require(s["supports_claims"] == sorted(v["claim_id"] for v in all_claims if sid in v["source_refs"]), "claim/source reciprocity")
        known = timestamp(s["known_at"])
        require(known <= timestamp(s["retrieved_at"]) <= timestamp(c["record"]["core"]["known_at"]), "knowledge/retrieval lookahead")
        if s["publication_date"] is not None:
            require(datetime.fromisoformat(s["publication_date"]).date() <= known.date(), "future source publication")
        if s["artifact_hash"] is None:
            require(s["artifact_path"] is None, "unhashed local artifact")
        else:
            path = (ROOT / s["artifact_path"]).resolve()
            require(path.is_relative_to(ROOT) and sha(path) == s["artifact_hash"], "source artifact hash")
    return {"sources": len(ss), "claims": len(ids), "unarchived_sources": sum(s["artifact_hash"] is None for s in ss.values())}


def source_independence(c):
    ss = list(sources(c).values())
    groups, issuers = {}, {}
    for s in ss:
        underlying = s["underlying_artifact"]
        group = s["independence_group"]
        require(groups.setdefault(underlying, group) == group, "mirrors counted independently")
        require(issuers.setdefault(s["issuer"], group) == group, "same issuer split into independent corroboration")
    expected = sorted({s["independence_group"] + "::" + s["evidence_family"] for s in ss})
    require(c["package"]["sources"]["independent_evidence_families"] == expected, "derived evidence family drift")
    return {"issuer_groups": len(set(issuers.values())), "evidence_families": expected, "demand_inference": False}


def application_bridge(c, claim):
    """A publication date alone cannot make historical use contemporary."""
    require(claim['claim_type'] == 'DIRECT_PUBLIC_EVIDENCE' and claim['evidence_basis'] == 'APPLICATION_DOCUMENT', 'direct application evidence required')
    bridge = claim.get('current_bridge', {})
    refs = bridge.get('source_refs', [])
    require(refs and set(refs) <= set(claim['source_refs']), 'missing source-backed current application bridge')
    now = timestamp(c['record']['core']['known_at']).date()
    require(datetime.fromisoformat(bridge['valid_from']).date() <= now <= datetime.fromisoformat(bridge['valid_through']).date(), 'application bridge does not cover research date')
    require(bridge.get('rationale'), 'bridge rationale missing')
    require(all(sources(c)[s]['access_status'] == 'OPENED_CONTENT' and sources(c)[s]['source_type'] in {'OEM_APPLICATION_DOCUMENT', 'SERVICE_DOCUMENT', 'PUBLIC_BOM', 'PUBLIC_PROCESS_STUDY', 'PUBLIC_PROCUREMENT_DOCUMENT'} for s in refs), 'catalog/market listing cannot establish application bridge')


def evidenced_bottleneck(c, claim):
    require(claim['topic'] == 'OBSERVED_BOTTLENECK', 'missing observed bottleneck')
    application_bridge(c, claim)


def current_usage(c):
    p = c["package"]["usage"]
    direct = [v for v in p["claims"] if v["claim_type"] == "DIRECT_PUBLIC_EVIDENCE" and v["scope"] == "EXACT_PART" and v["evidence_basis"] == "APPLICATION_DOCUMENT"]
    for v in p["claims"]:
        if v["current_usage_asserted"]:
            require(v in direct, "stock/family/catalog cannot establish exact current usage")
            application_bridge(c, v)
    if p["signal"] in {"CURRENT_USAGE_DIRECT", "SERVICE_REPAIR_USAGE"}:
        require(direct, "missing current exact application bridge")
        for v in direct:
            application_bridge(c, v)
    if p["signal"] == "CURRENT_USAGE_INDIRECT":
        require(any(v["evidence_basis"] == "MANUFACTURER_CATALOG" for v in p["claims"]), "inventory cannot substitute for manufacturer relevance")
    require(any(x["purpose"] == "USAGE" for x in c["package"]["sources"]["search_log"]), "usage search absent")
    return {"signal": p["signal"], "direct_application_claims": len(direct)}


def current_solution(c):
    p = c["package"]["solution"]
    observed = [v for v in p["paths"] if v["evidence_class"] == "OBSERVED_CURRENT_SOLUTION"]
    for v in p["paths"]:
        require(set(v["source_refs"]) <= sources(c).keys(), "solution source missing")
        if v["evidence_class"] == "OBSERVED_CURRENT_SOLUTION":
            require(v["organization"] and v["adoption_verified"] and v["source_refs"], "unsupported named adoption")
            require(any(x["claim_type"] == "DIRECT_PUBLIC_EVIDENCE" and x["evidence_basis"] == "APPLICATION_DOCUMENT" and set(x["source_refs"]) & set(v["source_refs"]) for x in p["claims"]), "observed solution lacks direct adoption evidence")
            for claim in p['claims']:
                if claim['claim_type'] == 'DIRECT_PUBLIC_EVIDENCE' and set(claim['source_refs']) & set(v['source_refs']):
                    application_bridge(c, claim)
        else:
            require(v["organization"] is None and v["adoption_verified"] is False, "possible path mislabeled as company practice")
    require(p["efficiency_conclusion"] == "UNKNOWN", "efficiency cannot be inferred from a quote or technical operation")
    if not observed:
        raise NotEvaluated("No observed end-user current solution; catalog/method offerings are kept separate.")
    return {"observed_paths": len(observed)}


def inefficiency_discipline(c):
    p = c["package"]["inefficiency"]
    require([v["dimension"] for v in p["dimensions"]] == DIMENSIONS, "inefficiency dimensions incomplete")
    claim_ids = {x["claim_id"] for x in p["claims"]}
    require(p["overall_score"] is None, "no overall opportunity/risk score")
    for v in p["dimensions"]:
        require(v["materiality"] == "UNKNOWN", "customer materiality unverified")
        require(set(v["claim_refs"]) <= claim_ids, "inefficiency claim reference")
        require(bool(v["claim_refs"]) == (v["state"] == "PUBLIC_SIGNAL"), "unsupported inefficiency signal")
    return {"public_signal_dimensions": [v["dimension"] for v in p["dimensions"] if v["state"] == "PUBLIC_SIGNAL"], "materiality": "UNKNOWN"}


def counter_evidence(c):
    p = c["package"]["counter_evidence"]
    require(p["search_performed"] and p["claims"], "missing dedicated counter-evidence")
    require(any(x["purpose"] == "COUNTER_EVIDENCE" for x in c["package"]["sources"]["search_log"]), "no counter-evidence search log")
    require(all(v["source_refs"] for v in p["claims"]), "counter-evidence is unsourced")
    return {"counter_claims": len(p["claims"]), "unresolved_conflicts": p["unresolved_conflicts"]}


def accepted_hypotheses(c):
    return [h for h in c["package"]["hypotheses"]["hypotheses"] if h["status"] == "CONDITIONAL_RESEARCH_HYPOTHESIS"]


def improvement_hypothesis(c):
    evidence = {v["claim_id"]: v for v in c["package"]["inefficiency"]["claims"]}
    for h in accepted_hypotheses(c):
        require(h["bottleneck_claim_refs"] and h["testable"] and not h["benefit_demonstrated"], "unsupported testable improvement")
        require(all(i in evidence and evidence[i]["topic"] == "OBSERVED_BOTTLENECK" and evidence[i]["source_refs"] for i in h["bottleneck_claim_refs"]), "tool capability or measurement requirement is not an evidenced bottleneck")
        for ref in h['bottleneck_claim_refs']:
            evidenced_bottleneck(c, evidence[ref])
        require(h["required_inputs"] and h["unknown_variables"] and h["failure_condition"], "hypothesis not falsifiable")
    if not accepted_hypotheses(c):
        raise NotEvaluated("No accepted evidence-backed bottleneck/improvement hypothesis; rejection retained.")
    return {"accepted_conditional_hypotheses": len(accepted_hypotheses(c))}


def tool_bottleneck_mapping(c):
    for h in c["package"]["hypotheses"]["hypotheses"]:
        require(set(h["tool_source_refs"]) <= sources(c).keys(), "tool source absent")
    for h in accepted_hypotheses(c):
        require(h["tool_source_refs"] and h["bottleneck_claim_refs"] and h["measurable_metric"], "unsupported tool benefit")
        require(any(sources(c)[s]["source_type"] == "TOOL_DOCUMENTATION" for s in h["tool_source_refs"]), "missing documented tool capability")
    if not accepted_hypotheses(c):
        raise NotEvaluated("No justified tool-to-bottleneck-to-effect mapping; capabilities alone confer no benefit.")
    return {"tool_mappings": len(accepted_hypotheses(c))}


def variable_map(c, key, names):
    p = c["package"][key]
    require([v["variable"] for v in p["variables"]] == names, "variable coverage")
    require(p["total"] is None, "no unsupported total savings/cost/duration")
    for v in p["variables"]:
        require(set(v["source_refs"]) <= sources(c).keys(), "variable source missing")
        if v["state"] in {"UNKNOWN", "MODEL_INPUT_REQUIRED"}:
            require(v["value"] is None and not v["source_refs"], "invented unknown input")
        else:
            require(v["value"] is not None and v["unit"] and v["source_refs"], "unbacked numeric input")
            require(all(sources(c)[s]["access_status"] == "OPENED_CONTENT" for s in v["source_refs"]), "cached search signal cannot supply model value")
        if v["variable"] == "PART_COST_DELTA":
            require(v["value"] is None, "one catalog price is not an established migration cost delta")
    return {"variables": len(names), "numeric_inputs": sum(v["value"] is not None for v in p["variables"]), "total": None}


def tmc_discipline(c):
    return variable_map(c, "tmc", TMC)


def ttq_discipline(c):
    return variable_map(c, "ttq", TTQ)


def private_boundary(c):
    prohibited = set(load("technical-risk/config/public_private_boundary.json")["private"]) | {"risk_score", "replacement_probability", "customer_actual_cost", "total_savings", "opportunity_state"}
    require(not (flatten_keys([c["package"], c["record"]]) & prohibited), "private/unsupported decision field")
    p = c["record"]["opportunity_validation"]
    require(p["client_scope"] == "NOT_PROVIDED", "private engagement scope")
    a = c["package"]["assessment"]
    require(a["public_release"] == a["paid_delivery"] == "BLOCK", "Phase B cannot release")
    # Baseline adapter remains authoritative and unchanged; Phase B adds a veto.
    original = load(p["baseline"]["record_path"])
    register = load(str(Path(p["baseline"]["record_path"]).with_name("01_SOURCE_REGISTER.json")))
    effect = import_adapter().release_effect(original, register)
    return {"private_fields": [], "baseline_gdr_effect": effect["public_release"], "phase_b_public_release": "BLOCK", "phase_b_paid_delivery": "BLOCK"}


def no_unverified_qualification(c):
    a = c["package"]["assessment"]
    require(a["qualification_state"] == "NOT_ESTABLISHED" and a["solution_development"] == "NOT_AUTHORIZED", "qualification/development promotion")
    for v in claims(c):
        require(v["topic"] not in {"QUALIFIED", "DROP_IN", "FULLY_COMPATIBLE", "SNIPE_SOLUTION_APPROVED"}, "unverified qualification claim")
        require(not re.search(r"(?i)\b(is|are)\s+(a\s+)?(qualified|drop-in|fully compatible|equivalent)\b", v["statement"]), "positive qualification assertion requires unavailable scope evidence")
    return {"qualification": "NOT_ESTABLISHED", "development": "NOT_AUTHORIZED"}


def desk_signal_discipline(c):
    p = c["package"]
    a = p["assessment"]
    require(not a["confirmed_customer_pain"], "desk research is not confirmed customer pain")
    require(set(a["supporting_claim_refs"]) <= {v["claim_id"] for v in claims(c)}, "assessment claim reference")
    if a["desk_opportunity_signal"] == "PUBLIC_EVIDENCE_SUBOPTIMAL_SIGNAL":
        require(any(v["topic"] == "OBSERVED_BOTTLENECK" for v in p["inefficiency"]["claims"]), "unsupported suboptimal signal")
        for claim in p['inefficiency']['claims']:
            if claim['topic'] == 'OBSERVED_BOTTLENECK':
                evidenced_bottleneck(c, claim)
    if a["decision"].startswith("PROCEED_TO_PHASE_C"):
        require(p["usage"]["signal"] in {"CURRENT_USAGE_DIRECT", "CURRENT_USAGE_INDIRECT", "SERVICE_REPAIR_USAGE"}, "Phase C usage criterion")
        require(a["desk_opportunity_signal"] in {"PUBLIC_EVIDENCE_UNRESOLVED_SIGNAL", "PUBLIC_EVIDENCE_SUBOPTIMAL_SIGNAL"} and accepted_hypotheses(c), "Phase C opportunity/hypothesis criterion")
        require(a["human_validation_required"] == "YES", "Phase C needs a material unresolved human fact")
    require(a["decision"] != "PROCEED_TO_PHASE_C_HIGH_PRIORITY" or p["usage"]["signal"] == "CURRENT_USAGE_DIRECT", "high priority cannot be catalog-only")
    return {"desk_signal": a["desk_opportunity_signal"], "decision": a["decision"], "confirmed_customer_pain": False}


def human_validation_boundary(c):
    p = c["package"]["human_targets"]
    require(p["authorization"] == "DISCOVERY_ONLY_NO_OUTREACH" and p["human_validation_required"] == "YES", "human validation boundary")
    require(c["package"]["assessment"]["phase_c_outreach"] == "NOT_AUTHORIZED", "Phase B cannot authorize sending")
    urls = {s["url"] for s in sources(c).values() if s["source_type"] == "PUBLIC_CONTACT_PAGE" and s["access_status"] == "OPENED_CONTENT"}
    for t in p["targets"]:
        require(t["public_source"] in sources(c) and t["public_contact_path"] in urls, "unverified public forwarding path")
        require(not t["outreach_sent"] and t["contact_path_verified"], "contact not authorized")
    return {"future_public_channels": len(p["targets"]), "messages_sent": 0}


def successor_hash_integrity(c):
    r, package = c["record"], c["package"]
    p = r["opportunity_validation"]
    core = dict(r["core"])
    record_hash = core.pop("record_hash")
    require(record_hash == digest({"core": core, "payload": p}), "successor canonical hash")
    require(core["input_hash"] == digest({"sources": package["sources"], "payload": p}), "successor input hash")
    require(p["phase_b_assessment"] == package["assessment"], "assessment artifact drift")
    expected = set(FILES.values()) | {"11_LIMITATIONS.md"}
    require(set(p["artifact_hashes"]) == expected, "manifest coverage or circular gate/self hash")
    for key, name in FILES.items():
        path = c["folder"] / "phase-b" / name
        require(p["artifact_hashes"][name] == sha(path), "artifact hash mismatch: " + name)
        require(json.loads(path.read_text()) == package[key], "in-memory package/artifact drift")
    require(p["artifact_hashes"]["11_LIMITATIONS.md"] == sha(c["folder"] / "phase-b/11_LIMITATIONS.md"), "limitations integrity")
    old = load(p["predecessor_path"])
    expected_sources = sorted(set(old["core"]["source_refs"]) | sources(c).keys())
    require(core["source_refs"] == expected_sources, "shared source lineage mismatch")
    artifacts = old["core"]["artifact_refs"] + [p["predecessor_path"] + ":" + sha(ROOT / p["predecessor_path"])]
    artifacts += [(c["folder"] / "phase-b" / f).relative_to(ROOT).as_posix() + ":" + h for f, h in sorted(p["artifact_hashes"].items())]
    require(core["artifact_refs"] == artifacts, "shared artifact lineage mismatch")
    event = p["research_event"]
    require(event["source_refs"] == list(sources(c)), "research event scope")
    times = [core[k] for k in ["effective_at", "known_at", "created_at", "updated_at"]] + [event[k] for k in ["effective_at", "known_at", "created_at"]]
    require(len(set(times)) == 1 and timestamp(times[0]) >= timestamp(old["core"]["known_at"]), "research clock/successor chronology")
    require(core["correction_status"] == "NO_CORRECTION_RECORDED" and core["supersession_status"] == "CURRENT", "successor release status cannot be promoted")
    require(core['policy_version'] == VERSION and core['verification_status'] == 'PUBLIC_EVIDENCE_REVIEWED_WITH_LIMITATIONS', 'Phase B core status drift')
    return {"record_hash": record_hash, "artifacts_bound": len(expected), "gate_and_self_hash_excluded": True}


GATES = dict(zip([
    "OV-B01_BASELINE_INTEGRITY", "OV-B02_SOURCE_PROVENANCE", "OV-B03_SOURCE_INDEPENDENCE", "OV-B04_CURRENT_USAGE_EVIDENCE",
    "OV-B05_CURRENT_SOLUTION_EVIDENCE", "OV-B06_INEFFICIENCY_DISCIPLINE", "OV-B07_COUNTER_EVIDENCE", "OV-B08_IMPROVEMENT_HYPOTHESIS",
    "OV-B09_TOOL_BOTTLENECK_MAPPING", "OV-B10_TMC_DISCIPLINE", "OV-B11_TTQ_DISCIPLINE", "OV-B12_PRIVATE_BOUNDARY",
    "OV-B13_NO_UNVERIFIED_QUALIFICATION", "OV-B14_DESK_SIGNAL_DISCIPLINE", "OV-B15_HUMAN_VALIDATION_BOUNDARY", "OV-B16_SUCCESSOR_HASH_INTEGRITY"],
    [baseline_integrity, source_provenance, source_independence, current_usage, current_solution, inefficiency_discipline, counter_evidence, improvement_hypothesis, tool_bottleneck_mapping, tmc_discipline, ttq_discipline, private_boundary, no_unverified_qualification, desk_signal_discipline, human_validation_boundary, successor_hash_integrity]))


def evaluate(c):
    rows = []
    for name, validator in GATES.items():
        try:
            facts = validator(c)
            status, reason = "PASS", "Evidence discipline satisfied; no opportunity or release approval implied."
        except NotEvaluated as exc:
            facts, status, reason = {}, "NOT_EVALUATED", str(exc)
        except Exception as exc:
            facts, status, reason = {}, "FAIL", f"{type(exc).__name__}: {exc}"
        rows.append(dict(gate_id=name, validator=validator.__name__, rule_version=VERSION, status=status, reason=reason, computed_facts=facts))
    return dict(target=c["target"], evaluation_as_of=datetime.now(timezone.utc).isoformat(), baseline_commit=BASE,
                record_hash=c["record"]["core"]["record_hash"], validator_sha256=sha(Path(__file__)),
                results=rows, summary={s: sum(r["status"] == s for r in rows) for s in ["PASS", "FAIL", "NOT_EVALUATED"]}, public_release="BLOCK", paid_delivery="BLOCK")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-results", action="store_true", help="Write only new per-target Phase B gate files")
    args = parser.parse_args()
    failed = False
    for target in TARGETS:
        c = context(target)
        result = evaluate(c)
        if args.write_results:
            (c["folder"] / "phase-b/12_PHASE_B_GATE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(target, result["summary"])
        for row in result["results"]:
            if row["status"] == "FAIL":
                print(row["gate_id"], row["reason"])
        failed |= bool(result["summary"]["FAIL"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
