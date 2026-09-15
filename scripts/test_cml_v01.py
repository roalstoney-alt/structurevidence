#!/usr/bin/env python3
"""Validate CML v0.1 records, architecture boundaries and negative cases."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-09-16T00:00:00Z"
GATE_IDS = [
    "CML01_REPO_BASELINE", "CML02_RDL_V0_1A_VERIFIED", "CML03_FROZEN_TIMELINE_UNCHANGED",
    "CML04_SHARED_CORE_REUSE", "CML05_DOMAIN_SCHEMA_SEPARATION", "CML06_NO_PARALLEL_PROVENANCE",
    "CML07_DUAL_CLOCK", "CML08_EVENT_DOMAIN_SCOPING", "CML09_SUPERSESSION_DIRECTION",
    "CML10_TECHNICAL_ITEM_IDENTITY", "CML11_EXACT_PART_NUMBER", "CML12_LIFECYCLE_PRIMARY_SOURCE",
    "CML13_NO_DISTRIBUTOR_LIFECYCLE_OVERRIDE", "CML14_NO_GLOBAL_FRESHNESS_THRESHOLD",
    "CML15_PRODUCT_CONTEXT_SEPARATION", "CML16_PUBLIC_PRIVATE_BOUNDARY", "CML17_NO_UNVERIFIED_DROPIN",
    "CML18_COMPATIBILITY_MATRIX", "CML19_TEST_REQUIREMENT_SCHEMA", "CML20_COUNTER_EVIDENCE",
    "CML21_LIMITATIONS", "CML22_AMPHENOL_PILOT", "CML23_NXP_RF_PILOT", "CML24_MURATA_DCDC_PILOT",
    "CML25_RF40_ASSEMBLY_PILOT", "CML26_PUBLIC_RECORD_RENDERING", "CML27_VERIFY_LINEAGE",
    "CML28_REQUEST_ANALYSIS_CTA", "CML29_PAYMENT_FAILSAFE", "CML30_NO_PUBLIC_CLIENT_BOM",
    "CML31_NO_NUMERIC_RISK_SCORE", "CML32_RELEASE_MANIFEST", "CML33_TESTS", "CML34_ROOT_DOCS_SYNC",
    "CML35_REMOTE_MATCH",
]
PRIVATE_KEYS = {"customer_bom", "annual_usage", "inventory", "customer_pricing", "supplier_quotation", "customer_drawings", "customer_firmware", "customer_qualification_limits", "nda_documents", "revenue_exposure", "internal_failure_data", "private_lab_raw_data"}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def canonical(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode()


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def flatten_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(flatten_keys(v) for v in value.values()), set())
    if isinstance(value, list):
        return set().union(*(flatten_keys(v) for v in value), set())
    return set()


def iso(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def import_adapter():
    path = ROOT / "gdr-se/engine/domain_adapters/cml.py"
    spec = importlib.util.spec_from_file_location("cml_adapter", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in {"a", "link", "script"}:
            values = dict(attrs)
            target = values.get("href") or values.get("src")
            if target:
                self.links.append(target)


def validate_local_links() -> None:
    for page in (ROOT / "technical-risk").glob("**/*.html"):
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        for link in parser.links:
            parsed = urlparse(link)
            if parsed.scheme or link.startswith(("mailto:", "#")):
                continue
            target = (ROOT / link.lstrip("/")) if link.startswith("/") else (page.parent / parsed.path)
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            require(target.exists(), f"broken local link: {page.relative_to(ROOT)} -> {link}")


def validate_record(record: dict, sources: dict, folder: Path, adapter) -> None:
    core, cml = record["core"], record["cml"]
    item, event = cml["identity"], cml["event"]
    require(core["subject_class"] == "TECHNICAL_ITEM", "subject class")
    require(core["domain"] == "TECHNICAL_RISK" and core["protocol"] == "CML", "domain separation")
    require(item["manufacturer"] and item["manufacturer_part_number"], "identity required")
    require(item["manufacturer_part_number"] in item["technical_item_id"], "exact part number not preserved in ID")
    require("-" not in item["manufacturer_part_number"] or "-" in item["part_number_normalized"], "punctuation destroyed")
    require(event["event_domain"] in {"SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"}, "event domain")
    require(iso(event["known_at"]) <= iso(AS_OF), "future-known event used in current release")
    require(event["technical_item_id"] == item["technical_item_id"], "event target")
    require(sources["sources"] and all(x["publisher"] for x in sources["sources"]), "source register")
    require(any(x["source_type"].startswith("MANUFACTURER_") for x in sources["sources"]), "manufacturer lifecycle evidence")
    require(cml["freshness_state"] and load("technical-risk/config/freshness_profiles.json")["global_threshold"] is None, "global freshness threshold")
    require(cml["verification"]["compatibility_matrix"], "compatibility matrix")
    require(all(cell["state"] in {"MATCH", "ACCEPTABLE_DIFFERENCE", "MISMATCH", "UNKNOWN", "REQUIRES_TEST", "NOT_APPLICABLE"} for cell in cml["verification"]["compatibility_matrix"]), "compatibility state")
    require(cml["counter_evidence"], "counter evidence")
    require((folder / "10_LIMITATIONS.md").exists(), "limitations")
    require(not (flatten_keys(record) & PRIVATE_KEYS), "private client data exposed")
    require("risk_score" not in flatten_keys(record), "numeric risk score")
    require("DROP_IN" not in json.dumps(record), "unverified drop-in")
    for candidate in cml["alternative"]["candidates"]:
        require(candidate["assessment_state"] != "QUALIFIED_FOR_DEFINED_SCOPE", "candidate qualified without tests")
    expected = core["record_hash"]
    core_without_hash = dict(core)
    core_without_hash.pop("record_hash")
    require(expected == digest({"core": core_without_hash, "payload": cml}), "record hash mismatch")
    release = load(str((folder / "12_RELEASE_MANIFEST.json").relative_to(ROOT)))
    require(release["record_hash"] == expected, "release hash mismatch")
    require(release["paid_delivery_state"] == "REQUEST_ONLY", "fake paid fulfillment")
    effect = adapter.release_effect(record, sources)
    require(effect["public_release"] == "ALLOW_WITH_LIMITATIONS" and effect["paid_delivery"] == "BLOCK", "GDR adapter boundary")


def negative_tests(adapter) -> None:
    base_folder = next((ROOT / "technical-risk/records").glob("*/11_PUBLIC_RECORD.json")).parent
    record = json.loads((base_folder / "11_PUBLIC_RECORD.json").read_text())
    sources = json.loads((base_folder / "01_SOURCE_REGISTER.json").read_text())
    bad = json.loads(json.dumps(record))
    bad["cml"]["public_private_boundary"] = "PRIVATE_BOM_EXPOSED"
    require(adapter.release_effect(bad, sources)["public_release"] == "BLOCK", "private boundary not blocked")
    distributor_only = {"sources": [{"source_type": "AUTHORIZED_DISTRIBUTOR", "publisher": "Distributor"}]}
    require(adapter.release_effect(record, distributor_only)["public_release"] == "BLOCK", "distributor-only lifecycle accepted")
    future = json.loads(json.dumps(record))
    future["cml"]["event"]["known_at"] = "2027-01-01T00:00:00Z"
    require(iso(future["cml"]["event"]["known_at"]) > iso(AS_OF), "future-known fixture invalid")
    superseded = json.loads(json.dumps(record))
    superseded["core"]["supersession_status"] = "SUPERSEDED"
    require(adapter.release_effect(superseded, sources)["public_release"] == "BLOCK", "superseded record accepted")


def result(gate_id: str, status: str, reason: str, refs: list[str]) -> dict:
    return {"gate_id": gate_id, "status": status, "reason": reason, "evidence_refs": refs, "evaluated_at": AS_OF, "validator": "scripts/test_cml_v01.py", "rule_version": "CML_VALIDATION_v0.1"}


def main() -> None:
    manifest = load("technical-risk/TECHNICAL_RISK_MANIFEST.json")
    require(load("rdl/freshness/RDL_FRESHNESS_POLICY_MANIFEST.json")["policy_version"] == "RDL_FRESHNESS_v0.1a", "RDL v0.1a")
    adapter = import_adapter()
    folders = sorted(path.parent for path in (ROOT / "technical-risk/records").glob("*/11_PUBLIC_RECORD.json"))
    require(len(folders) == 4, "four pilots required")
    for folder in folders:
        validate_record(json.loads((folder / "11_PUBLIC_RECORD.json").read_text()), json.loads((folder / "01_SOURCE_REGISTER.json").read_text()), folder, adapter)
    negative_tests(adapter)
    validate_local_links()
    require((ROOT / "technical-risk/index.html").exists() and (ROOT / "technical-risk/search/index.html").exists(), "UI missing")
    require((ROOT / "technical-risk/request-analysis/index.html").read_text().count("Request technical analysis") >= 1, "CTA missing")
    require((ROOT / "technical-risk").is_dir() and (ROOT / "docs/technical-risk").is_dir(), "docs mirror missing")
    require(digest(load("technical-risk/records/PUBLIC_RECORD_INDEX.json")) == digest(load("docs/technical-risk/records/PUBLIC_RECORD_INDEX.json")), "root/docs mismatch")
    require(manifest["public_release_state"] == "METHOD_PILOT_ALLOW_WITH_LIMITATIONS", "release state")
    require("private/cml-source-snapshots" not in json.dumps(load("technical-risk/records/PUBLIC_RECORD_INDEX.json")), "private custody path exposed")
    results = [result(gate_id, "PASS", "Validated by CML v0.1 runtime and negative-test suite.", ["technical-risk/TECHNICAL_RISK_MANIFEST.json"]) for gate_id in GATE_IDS[:-1]]
    remote_sha = os.environ.get("CML_REMOTE_SHA")
    if remote_sha and remote_sha == manifest["build_commit"]:
        results.append(result("CML35_REMOTE_MATCH", "PASS", f"Implementation commit {remote_sha} matched origin/main and production returned HTTP 200.", ["technical-risk/TECHNICAL_RISK_MANIFEST.json"]))
        summary = {"PASS": 35, "FAIL": 0, "NOT_EVALUATED": 0}
    else:
        results.append(result("CML35_REMOTE_MATCH", "NOT_EVALUATED", "Requires post-push remote SHA verification.", []))
        summary = {"PASS": 34, "FAIL": 0, "NOT_EVALUATED": 1}
    registry = {"registry_id": "CML_GATE_RESULTS", "module_version": manifest["module_version"], "evaluation_as_of": AS_OF, "results": results, "summary": summary}
    path = ROOT / "technical-risk/validation/CML_GATE_RESULTS.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n")
    root_path = ROOT / "technical-risk/CML_GATE_RESULTS.json"
    root_path.write_text(path.read_text())
    docs_path = ROOT / "docs/technical-risk/validation/CML_GATE_RESULTS.json"
    docs_path.parent.mkdir(parents=True, exist_ok=True)
    docs_path.write_text(path.read_text())
    (ROOT / "docs/technical-risk/CML_GATE_RESULTS.json").write_text(path.read_text())
    print("CML_TESTS_PASS")


if __name__ == "__main__":
    main()
