#!/usr/bin/env python3
"""Validate Phase B-R1 targeted research. Writes gates only with --write-results."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import jsonschema
from referencing import Registry, Resource

from test_cml_v01 import ROOT, digest, flatten_keys, load

BASE = "b0459b2b945c78ae650a7e0a6db5b8f206857a46"
VERSION = "CML_OV_v0.1_PHASE_B_R1"
TARGETS = {"OV-01": "amphenol-10081811-101-07lf", "OV-03": "amphenol-rf-095-725-134-006"}
TERMINAL = {"PUBLIC_BOTTLENECK_FOUND", "PUBLIC_EVIDENCE_CEILING", "NO_PLAUSIBLE_CURRENT_APPLICATION", "INSUFFICIENT_AFTER_TARGETED_RESEARCH"}
BOUND_ARTIFACTS = {"01_TARGETED_DISCOVERY.json", "03_LIMITATIONS.md"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(parsed.tzinfo is not None, "timezone required")
    return parsed


def folder(target):
    return ROOT / "technical-risk/records" / TARGETS[target] / "opportunity-validation"


def context(target):
    base = folder(target)
    return {
        "target": target,
        "folder": base,
        "record": json.loads((base / f"{target}.v0.3.json").read_text()),
        "package": json.loads((base / "phase-b-r1/01_TARGETED_DISCOVERY.json").read_text()),
    }


def schema_validate(c):
    package_path = ROOT / "technical-risk/opportunity-validation/schema/phase-b-r1-package.schema.json"
    record_path = ROOT / "technical-risk/opportunity-validation/schema/phase-b-r1-record.schema.json"
    phase_b_path = ROOT / "technical-risk/opportunity-validation/schema/phase-b-record.schema.json"
    core_path = ROOT / "evidence/core/schema/evidence_core_record.schema.json"
    registry = Registry()
    for path in [package_path, record_path, phase_b_path, core_path]:
        schema = json.loads(path.read_text())
        registry = registry.with_resource(path.as_uri(), Resource.from_contents(schema))
    for value, path in [(c["package"], package_path), (c["record"], record_path)]:
        schema = json.loads(path.read_text())
        schema["$id"] = path.as_uri()
        jsonschema.Draft202012Validator.check_schema(schema)
        jsonschema.Draft202012Validator(schema, registry=registry, format_checker=jsonschema.FormatChecker()).validate(value)


def baseline_integrity(c):
    tracked = subprocess.check_output(["git", "diff", "--name-only", BASE, "--"], cwd=ROOT, text=True).splitlines()
    require(not tracked, "accepted Wave 1 tracked baseline changed")
    predecessor = load(c["record"]["opportunity_validation"]["predecessor_path"])
    require(predecessor["core"]["record_id"] == f'SE.CML.OV.{c["target"]}.v0.2', "predecessor is not accepted Wave 1")
    require(c["record"]["opportunity_validation"]["predecessor_record_hash"] == predecessor["core"]["record_hash"], "predecessor hash mismatch")
    require(c["package"]["predecessor_record_id"] == predecessor["core"]["record_id"], "package predecessor mismatch")
    baseline_time = subprocess.check_output(["git", "show", "-s", "--format=%cI", BASE], cwd=ROOT, text=True).strip()
    record_time = c["record"]["core"]["known_at"]
    require(timestamp(record_time) >= timestamp(baseline_time), "B-R1 record predates accepted Wave 1 commit")
    require(timestamp(record_time) >= timestamp(predecessor["core"]["known_at"]), "B-R1 record predates predecessor knowledge")
    event = c["record"]["opportunity_validation"]["research_event"]
    clocks = [c["record"]["core"][key] for key in ["effective_at", "known_at", "created_at", "updated_at"]]
    clocks += [event[key] for key in ["effective_at", "known_at", "created_at"]]
    require(len(set(clocks)) == 1, "B-R1 successor/research-event clock drift")
    return {"baseline_commit": BASE, "baseline_commit_time": baseline_time, "research_time": record_time, "tracked_changes": []}


def provenance(c):
    schema_validate(c)
    sources = {s["source_id"]: s for s in c["package"]["sources"]}
    claims = {v["claim_id"]: v for v in c["package"]["claims"]}
    require(len(sources) == len(c["package"]["sources"]), "duplicate source ID")
    require(len(claims) == len(c["package"]["claims"]), "duplicate claim ID")
    for source in sources.values():
        require(urlparse(source["url"]).hostname == source["host"], "issuer/host provenance error")
        require(timestamp(source["known_at"]) <= timestamp(source["retrieved_at"]) <= timestamp(c["record"]["core"]["known_at"]), "source lookahead")
        expected = sorted(v["claim_id"] for v in claims.values() if source["source_id"] in v["source_refs"])
        require(source["supports_claims"] == expected, "source/claim reciprocity")
    for claim in claims.values():
        require(set(claim["source_refs"]) <= sources.keys(), "unresolved source reference")
        require(claim["claim_type"] == "UNKNOWN" or claim["source_refs"], "substantive claim lacks evidence")
    return {"sources": len(sources), "claims": len(claims), "issuer_groups": len({s['independence_group'] for s in sources.values()})}


def targeted_scope(c):
    purposes = [p["purpose"] for p in c["package"]["passes"]]
    if c["target"] == "OV-01":
        require(purposes == ["CURRENT_APPLICATION", "CURRENT_SOLUTION_WORKFLOW"], "OV-01 must contain exactly two targeted passes")
        text = " ".join(q.lower() for p in c["package"]["passes"] for q in p["queries"])
        require("catalog" not in text and "distributor" not in text, "broad catalog/distributor search repeated")
        require(c["package"]["research_scope"] == "TARGETED_APPLICATION_AND_WORKFLOW", "OV-01 scope drift")
    else:
        require(purposes == ["FORTY_GHZ_PRODUCTION", "FORTY_GHZ_QUALIFICATION", "VNA_WORKFLOW"], "OV-03 workflow passes incomplete")
        require(c["package"]["research_scope"] == "FORTY_GHZ_PRODUCTION_QUALIFICATION_AND_VNA_WORKFLOW", "OV-03 scope drift")
        joined = " ".join(p["result"].lower() for p in c["package"]["passes"])
        require(all(token in joined for token in ["production", "calibrat", "pass/fail"]), "OV-03 production/VNA workflow evidence incomplete")
    return {"passes": purposes}


def terminal_outcome(c):
    assessment = c["package"]["assessment"]
    require(assessment["terminal_outcome"] in TERMINAL, "unapproved terminal outcome")
    require(not assessment["confirmed_customer_pain"], "public evidence promoted to customer pain")
    if assessment["terminal_outcome"] == "PUBLIC_EVIDENCE_CEILING":
        require(not assessment["public_bottleneck"], "evidence ceiling promoted to bottleneck")
        require(assessment["public_evidence_ceiling"] and assessment["facts_requiring_nonpublic_validation"], "ceiling boundary not explicit")
        require(all(not v["observed_customer_workflow"] for v in c["package"]["claims"]), "ceiling conflicts with observed customer workflow")
    if assessment["terminal_outcome"] == "NO_PLAUSIBLE_CURRENT_APPLICATION":
        require(any(v["topic"] == "DIRECT_CURRENT_APPLICATION_NEGATION" and v["claim_type"] == "SOURCE_FACT" for v in c["package"]["claims"]), "no-application outcome requires direct evidence")
    return {"terminal_outcome": assessment["terminal_outcome"], "customer_pain": False}


def bottleneck_discipline(c):
    assessment = c["package"]["assessment"]
    bottlenecks = [v for v in c["package"]["claims"] if v["topic"] == "OBSERVED_PUBLIC_BOTTLENECK"]
    if assessment["terminal_outcome"] == "PUBLIC_BOTTLENECK_FOUND":
        require(assessment["public_bottleneck"] and bottlenecks, "public bottleneck has no direct claim")
        require(all(v["claim_type"] == "SOURCE_FACT" and v["observed_customer_workflow"] and v["source_refs"] for v in bottlenecks), "capability or judgment cannot establish a public bottleneck")
    else:
        require(not assessment["public_bottleneck"] and not bottlenecks, "bottleneck asserted outside terminal outcome")
    return {"public_bottleneck": assessment["public_bottleneck"], "bottleneck_claims": len(bottlenecks)}


def boundary(c):
    b = c["package"]["boundaries"]
    require(not any(b[k] for k in ["contact_attempted", "samples_bought", "quotations_requested", "replacement_designed", "snipe_solution_authorized"]), "B-R1 prohibited action recorded")
    require(b["public_release"] == b["paid_delivery"] == "BLOCK", "internal research release boundary")
    prohibited = {"customer_actual_cost", "total_savings", "opportunity_state", "risk_score", "replacement_probability"}
    require(not (flatten_keys([c["package"], c["record"]]) & prohibited), "private or unsupported decision field")
    return {"contact_attempted": False, "samples_bought": False, "quotations_requested": False, "replacement_designed": False, "snipe_solution_authorized": False}


def target_isolation(c):
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True)
    require("murata-mymgm5r012ela5rnd" not in status and "nxp-radio-power-2026" not in status, "OV-02 or OV-04 changed")
    require(c["target"] in TARGETS and c["package"]["target"] == c["target"], "unauthorized target")
    return {"targets": sorted(TARGETS), "excluded": ["OV-02", "OV-04"]}


def successor_integrity(c):
    record, package = c["record"], c["package"]
    payload = record["opportunity_validation"]
    core = dict(record["core"])
    record_hash = core.pop("record_hash")
    require(core["record_id"] == f'SE.CML.OV.{c["target"]}.v0.3', "successor ID")
    require(core["policy_version"] == VERSION and core["verification_status"] == "TARGETED_PUBLIC_RESEARCH_REVIEWED_WITH_LIMITATIONS", "successor status")
    require(record_hash == digest({"core": core, "payload": payload}), "record hash")
    require(core["input_hash"] == digest({"sources": package["sources"], "payload": payload}), "input hash")
    require(payload["phase_b_r1_assessment"] == package["assessment"], "assessment drift")
    require(set(payload["artifact_hashes"]) == BOUND_ARTIFACTS, "artifact coverage")
    for name, value in payload["artifact_hashes"].items():
        require(sha(c["folder"] / "phase-b-r1" / name) == value, "artifact hash: " + name)
    predecessor = load(payload["predecessor_path"])
    expected_sources = sorted(set(predecessor["core"]["source_refs"]) | {s["source_id"] for s in package["sources"]})
    require(core["source_refs"] == expected_sources, "source lineage")
    require(payload["research_event"]["source_refs"] == [s["source_id"] for s in package["sources"]], "research-event source order")
    return {"record_hash": record_hash, "artifacts_bound": len(BOUND_ARTIFACTS)}


GATES = {
    "OV-R101_ACCEPTED_WAVE1_BASELINE": baseline_integrity,
    "OV-R102_SCHEMA_AND_PROVENANCE": provenance,
    "OV-R103_TARGETED_SCOPE": targeted_scope,
    "OV-R104_TERMINAL_OUTCOME": terminal_outcome,
    "OV-R105_BOTTLENECK_DISCIPLINE": bottleneck_discipline,
    "OV-R106_RESEARCH_BOUNDARY": boundary,
    "OV-R107_TARGET_ISOLATION": target_isolation,
    "OV-R108_SUCCESSOR_INTEGRITY": successor_integrity,
}


def evaluate(c):
    rows = []
    for gate_id, validator in GATES.items():
        try:
            facts = validator(c)
            rows.append({"gate_id": gate_id, "status": "PASS", "reason": "B-R1 discipline satisfied; no customer-pain or solution approval implied.", "computed_facts": facts})
        except Exception as exc:
            rows.append({"gate_id": gate_id, "status": "FAIL", "reason": f"{type(exc).__name__}: {exc}", "computed_facts": {}})
    return {
        "assessment_version": VERSION,
        "target": c["target"],
        "baseline_commit": BASE,
        "record_hash": c["record"]["core"]["record_hash"],
        "validator_sha256": sha(Path(__file__)),
        "results": rows,
        "summary": {state: sum(r["status"] == state for r in rows) for state in ["PASS", "FAIL"]},
        "terminal_outcome": c["package"]["assessment"]["terminal_outcome"],
        "public_release": "BLOCK",
        "paid_delivery": "BLOCK",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-results", action="store_true")
    args = parser.parse_args()
    failed = False
    for target in TARGETS:
        result = evaluate(context(target))
        if args.write_results:
            path = folder(target) / "phase-b-r1/02_B_R1_GATE.json"
            path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(target, result["summary"], result["terminal_outcome"])
        failed |= bool(result["summary"]["FAIL"])
        for row in result["results"]:
            if row["status"] == "FAIL":
                print(row["gate_id"], row["reason"])
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
