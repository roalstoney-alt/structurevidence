#!/usr/bin/env python3
"""Read-only Phase A gates; never writes frozen audit or release artifacts."""
import hashlib
import json
import subprocess
from datetime import datetime

from test_cml_v01 import ROOT, digest, flatten_keys, import_adapter, load, validate_schema

BASE = "19be538447a90672491768d818fa07e3dd3dd377"
PREFIX = "technical-risk/opportunity-validation"
VERSION = "CML_OV_v0.1_PHASE_A"
MAPPING = {
    "OV-01": ("amphenol-10081811-101-07lf", "e665909621d08fe0c1049a1a09775d69e101856ed3b9305c500f887e8c2af51f"),
    "OV-02": ("murata-mymgm5r012ela5rnd", "f18e8d0dd74abd6874d4325af895197e07bb10d331f2e18167891f28a6b3f9dd"),
    "OV-03": ("amphenol-rf-095-725-134-006", "0616350e28fe26de50acc10877a7adf07ac1b033d6403c742dc6e011110e8b57"),
    "OV-04": ("nxp-radio-power-2026", "fad0d50b97e54a61c22078da35b79f63bb8de8e0bed1a0cc38d398977ac409aa"),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def baseline(record):
    slug, expected = MAPPING[record["opportunity_validation"]["ov_id"]]
    folder = f"technical-risk/records/{slug}"
    return folder, load(folder + "/11_PUBLIC_RECORD.json"), expected


def schema_gate(record):
    validate_schema(record, PREFIX + "/schema/record.schema.json")
    return {"schema": PREFIX + "/schema/record.schema.json"}


def baseline_gate(record):
    folder, source, expected = baseline(record)
    b = record["opportunity_validation"]["baseline"]
    c = source["cml"]
    expected_fields = {
        "commit": BASE, "record_path": folder + "/11_PUBLIC_RECORD.json",
        "record_id": source["core"]["record_id"], "record_hash": expected,
        "release_manifest_path": folder + "/12_RELEASE_MANIFEST.json",
        "release_manifest_sha256": sha(folder + "/12_RELEASE_MANIFEST.json"),
        "identity_scope": "FAMILY_EVENT" if record["opportunity_validation"]["ov_id"] == "OV-04" else "EXACT_PART",
        "event_effective_at": c["event"]["effective_at"], "event_known_at": c["event"]["known_at"],
        "lifecycle_state": c["lifecycle_state"], "qualification_state": c["verification"]["qualification_state"],
        "oem_replacement_status": c["alternative"]["oem_replacement_status"],
        "freshness_state": c["freshness_state"], "freshness_reason": c["freshness_reason"],
        "freshness_rule_type": c["freshness_rule_type"], "unknowns": c["evidence"]["unknowns"],
        "counter_evidence": c["counter_evidence"], "limitations_ref": folder + "/10_LIMITATIONS.md",
        "verification_requirements_ref": folder + "/05_COMPATIBILITY_REQUIREMENTS.json",
    }
    require(b == expected_fields, "baseline identity, state or limitation changed")
    core = dict(source["core"])
    require(core.pop("record_hash") == expected == digest({"core": core, "payload": c}), "baseline canonical hash")
    release = load(b["release_manifest_path"])
    require(release["record_hash"] == expected, "baseline release binding")
    paths = [folder + "/" + p for p in release["artifact_hashes"]] + [b["release_manifest_path"]]
    for path in paths:
        original = subprocess.check_output(["git", "show", BASE + ":" + path], cwd=ROOT)
        require((ROOT / path).read_bytes() == original, "frozen baseline changed: " + path)
    for path, hashed in release["artifact_hashes"].items():
        require(sha(folder + "/" + path) == hashed, "release artifact hash mismatch")
    return {"baseline_record_hash": expected, "frozen_artifacts_checked": len(paths)}


def envelope_gate(record):
    _, source, _ = baseline(record)
    core = record["core"]
    for key in ["core_version", "domain", "protocol", "subject_id", "subject_class", "source_refs"]:
        require(core[key] == source["core"][key], "shared envelope mismatch: " + key)
    require(core["record_id"] == "SE.CML.OV." + record["opportunity_validation"]["ov_id"] + ".v0.1", "OV identity")
    for key, value in {"verification_status": "NOT_ASSESSED", "correction_status": "NO_CORRECTION_RECORDED", "supersession_status": "CURRENT", "policy_version": VERSION}.items():
        require(core[key] == value, "initial envelope state: " + key)
    clocks = [datetime.fromisoformat(core[k].replace("Z", "+00:00")) for k in ["effective_at", "known_at", "created_at", "updated_at"]]
    require(all(t.tzinfo is not None for t in clocks) and len(set(clocks)) == 1, "initialization clocks must be equal and timezone-aware")
    require(core["known_at"] == load(PREFIX + "/PHASE_A_MANIFEST.json")["initialized_at"], "manifest clock mismatch")
    b = record["opportunity_validation"]["baseline"]
    artifacts = source["core"]["artifact_refs"] + [b[k] + ":" + sha(b[k]) for k in ["record_path", "release_manifest_path"]]
    require(core["artifact_refs"] == artifacts, "artifact lineage mismatch")
    return {"event_domain": "RESEARCH_EVENT", "source_count": len(core["source_refs"])}


def integrity_gate(record):
    p = record["opportunity_validation"]
    core = dict(record["core"])
    actual = core.pop("record_hash")
    require(core["input_hash"] == digest({"sources": p["baseline"], "payload": p}), "OV input hash")
    require(actual == digest({"core": core, "payload": p}), "OV canonical record hash")
    return {"record_hash": actual}


def unknown_gate(record):
    p = record["opportunity_validation"]
    count = 0

    def walk(node):
        nonlocal count
        if "state" in node:
            require(node == {"state": "NOT_ASSESSED", "value": None, "evidence_refs": []}, "unsupported assessment")
            count += 1
        else:
            for value in node.values():
                walk(value)

    for name in ["problem_persistence", "current_solution_audit", "solution_improvement_potential"]:
        walk(p[name])
    require(count == 34, "missing assessment dimension")
    return {"unassessed_dimensions": count}


def boundary_gate(record):
    prohibited = set(load("technical-risk/config/public_private_boundary.json")["private"])
    prohibited |= {"risk_score", "replacement_probability", "score"}
    require(not (flatten_keys(record) & prohibited), "private data or invented numeric score")
    p = record["opportunity_validation"]
    require(p["client_scope"] == "NOT_PROVIDED" and p["public_private_boundary"] == "PUBLIC_EVIDENCE_ONLY_NO_CLIENT_BOM", "private scope")
    return {"private_fields_detected": [], "client_scope": "NOT_PROVIDED"}


def governance_gate(record):
    folder, source, _ = baseline(record)
    inherited = import_adapter().release_effect(source, load(folder + "/01_SOURCE_REGISTER.json"))
    p = record["opportunity_validation"]
    require(p["governance"] == {
        "public_release": "BLOCK", "paid_delivery": "BLOCK", "solution_development": "NOT_AUTHORIZED",
        "opportunity_qualification": "NOT_ASSESSED", "reason": "PHASE_A_INITIALIZATION_ONLY",
        "gdr_adapter_ref": "gdr-se/engine/domain_adapters/cml.py",
    }, "Phase A cannot grant release or development authority")
    require((p["freshness_state"], p["freshness_reason"], p["freshness_rule_type"]) == ("POLICY_NOT_CONFIGURED", "OV_ASSESSMENT_CADENCE_NOT_CONFIGURED", "UNCONFIGURED"), "OV freshness cannot inherit technical snapshot freshness")
    return {"baseline_gdr_public_release": inherited["public_release"], "baseline_gdr_reasons": inherited["hard_block_reasons"], "ov_public_release": "BLOCK", "ov_paid_delivery": "BLOCK"}


GATES = {
    "OV-A01_SCHEMA": schema_gate,
    "OV-A02_BASELINE": baseline_gate,
    "OV-A03_SHARED_ENVELOPE": envelope_gate,
    "OV-A04_HASH_INTEGRITY": integrity_gate,
    "OV-A05_UNASSESSED": unknown_gate,
    "OV-A06_BOUNDARY": boundary_gate,
    "OV-A07_GOVERNANCE": governance_gate,
}


def evaluate(record):
    rows = []
    for gate_id, validator in GATES.items():
        try:
            facts = validator(record)
            status = "PASS"
        except Exception as exc:
            facts, status = {"error": str(exc)}, "FAIL"
        rows.append({"gate_id": gate_id, "validator": validator.__name__, "status": status, "computed_facts": facts, "rule_version": VERSION})
    return rows


def release_effect(record):
    """Phase A is an additional veto, never an alternative to shared GDR."""
    rows = evaluate(record)
    return {"public_release": "BLOCK", "paid_delivery": "BLOCK", "reason": "PHASE_A_INITIALIZATION_ONLY" if all(r["status"] == "PASS" for r in rows) else "PHASE_A_VALIDATION_FAILED", "gates": rows}


def package_gate():
    index = load(PREFIX + "/INDEX.json")
    require(index["version"] == VERSION and index["public_verify_registration"] is False, "index release boundary")
    require([r["ov_id"] for r in index["records"]] == list(MAPPING), "four exact mappings required")
    expected_paths = {PREFIX + "/" + p for p in ["schema/record.schema.json", "templates/phase-a-record.json", "STATUS_VOCABULARY.json", "INDEX.json"]}
    for row in index["records"]:
        slug, expected = MAPPING[row["ov_id"]]
        path = f'technical-risk/records/{slug}/opportunity-validation/{row["ov_id"]}.v0.1.json'
        require(row["path"] == path, "record store path")
        record = load(path)
        require(row["record_hash"] == record["core"]["record_hash"] and row["record_id"] == record["core"]["record_id"] and row["baseline_record_hash"] == expected, "index lineage")
        expected_paths.add(path)
    manifest = load(PREFIX + "/PHASE_A_MANIFEST.json")
    require(set(manifest["artifact_hashes"]) == expected_paths, "manifest coverage; no self hash")
    require(manifest["baseline_commit"] == BASE and manifest["version"] == VERSION and manifest["release_state"] == manifest["paid_delivery_state"] == "BLOCK", "manifest authority")
    for path, hashed in manifest["artifact_hashes"].items():
        require(sha(path) == hashed, "manifest artifact mismatch: " + path)
    for path in expected_paths | {PREFIX + "/PHASE_A_MANIFEST.json"}:
        require((ROOT / path).read_bytes() == (ROOT / "docs" / path).read_bytes(), "mirror drift: " + path)
    template = load(PREFIX + "/templates/phase-a-record.json")
    require(all(r["status"] == "PASS" for r in evaluate(template)), "worked template must validate")
    history_path = "technical-risk/CML_VERSION_HISTORY.jsonl"
    original = subprocess.check_output(["git", "show", BASE + ":" + history_path], cwd=ROOT)
    history = (ROOT / history_path).read_bytes()
    require(history.startswith(original), "history must be append-only")
    require(history == (ROOT / "docs" / history_path).read_bytes(), "history mirror drift")
    entries = [json.loads(line) for line in history[len(original):].splitlines() if line]
    require(len(entries) == 1 and entries[0]["opportunity_validation_version"] == VERSION, "Phase A history entry")
    return {"records": 4, "manifest_artifacts": len(expected_paths), "mirrors": len(expected_paths) + 1, "append_only_history": True}


def main():
    output = {"phase": "PHASE_A", "records": {}, "package": package_gate()}
    for row in load(PREFIX + "/INDEX.json")["records"]:
        result = release_effect(load(row["path"]))
        output["records"][row["ov_id"]] = result
    print(json.dumps(output, indent=2, sort_keys=True))
    if any(g["status"] != "PASS" for r in output["records"].values() for g in r["gates"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
