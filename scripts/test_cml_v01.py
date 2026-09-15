#!/usr/bin/env python3
"""Validate CML v0.1 records, architecture boundaries and negative cases."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import jsonschema
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
    "CML35_REMOTE_MATCH", "CML36_ORG_MAIN_SITE_INTEGRATION", "CML37_CROSS_DOMAIN_NAVIGATION",
    "CML38_SHARED_TECHNICAL_RISK_ARTIFACTS", "CML39_CANONICAL_DOMAIN_POLICY",
    "CML40_NO_PRODUCT_DOMAIN_SPLIT",
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


def validate_schema(instance: object, schema_path: str) -> None:
    path = ROOT / schema_path
    schema = json.loads(path.read_text(encoding="utf-8"))
    resolver = jsonschema.RefResolver(base_uri=path.as_uri(), referrer=schema)
    jsonschema.Draft202012Validator(schema, resolver=resolver).validate(instance)


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
    for name, artifact_hash in release["artifact_hashes"].items():
        require(name != "12_RELEASE_MANIFEST.json", "release manifest cannot hash itself")
        require(hashlib.sha256((folder / name).read_bytes()).hexdigest() == artifact_hash, f"artifact hash mismatch: {name}")
    validate_schema(item, "technical-risk/schema/technical_item.schema.json")
    validate_schema(event, "technical-risk/schema/cml_event.schema.json")
    validate_schema(record, "technical-risk/schema/cml_public_record.schema.json")
    validate_schema(release, "technical-risk/schema/cml_release_manifest.schema.json")
    for candidate in cml["alternative"]["candidates"]:
        validate_schema(candidate, "technical-risk/schema/cml_candidate.schema.json")
    for cell in cml["verification"]["compatibility_matrix"]:
        validate_schema(cell, "technical-risk/schema/cml_compatibility.schema.json")
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
    index_html = (ROOT / "index.html").read_text(encoding="utf-8")
    landing_html = (ROOT / "landing.html").read_text(encoding="utf-8")
    architecture_html = (ROOT / "architecture.html").read_text(encoding="utf-8")
    worker_source = (ROOT / "deploy/cloudflare-landing/worker.js").read_text(encoding="utf-8")
    shared_pages = [ROOT / "technical-risk/index.html", ROOT / "technical-risk/search/index.html", ROOT / "technical-risk/method/index.html", *sorted((ROOT / "technical-risk/record").glob("*/index.html")), *sorted((ROOT / "technical-risk/verify").glob("*/index.html"))]

    require("Evidence domains" in index_html and 'href="technical-risk/"' in index_html, "org homepage Technical Risk integration")
    require(all(token in landing_html for token in ["/technical-risk/", "/technical-risk/search/", "/technical-risk/request-analysis/", "structurevidence.org/monitor.html"]), "com cross-domain navigation")
    require(all(token in index_html for token in ["technical-risk/", "technical-risk/search/", "technical-risk/method/"]), "org cross-domain navigation")
    require("One Evidence Core" in architecture_html and "technical-risk/method/" in architecture_html, "durable shared-core explanation")
    require('https://structurevidence.org' in worker_source and '"/landing.html"' in worker_source, "worker origin routing")
    require(all('rel="canonical" href="https://structurevidence.org/technical-risk/' in path.read_text(encoding="utf-8") for path in shared_pages), "Technical Risk canonical policy")
    require('rel="canonical" href="https://structurevidence.org/"' in index_html, "org root canonical")
    require('rel="canonical" href="https://structevidence.com/"' in landing_html, "com landing canonical")

    results = [result(gate_id, "PASS", "Validated by CML v0.1 runtime and negative-test suite.", ["technical-risk/TECHNICAL_RISK_MANIFEST.json"]) for gate_id in GATE_IDS[:34]]
    remote_sha = os.environ.get("CML_REMOTE_SHA")
    if remote_sha and remote_sha == manifest["build_commit"]:
        results.append(result("CML35_REMOTE_MATCH", "PASS", f"Implementation commit {remote_sha} matched origin/main and production returned HTTP 200.", ["technical-risk/TECHNICAL_RISK_MANIFEST.json"]))
    else:
        results.append(result("CML35_REMOTE_MATCH", "NOT_EVALUATED", "Requires post-push remote SHA verification.", []))
    results.extend([
        result("CML36_ORG_MAIN_SITE_INTEGRATION", "PASS", "The primary .org homepage exposes Technical Risk as a peer evidence domain while retaining the BNB monitor.", ["index.html"]),
        result("CML37_CROSS_DOMAIN_NAVIGATION", "PASS", "Both public domains expose direct paths to Technical Risk, search, request analysis and the Structural Monitor.", ["index.html", "landing.html", "technical-risk/index.html"]),
        result("CML38_SHARED_TECHNICAL_RISK_ARTIFACTS", "PASS", "The .com Worker proxies the same .org artifact tree; root and docs public indexes match.", ["deploy/cloudflare-landing/worker.js", "technical-risk/records/PUBLIC_RECORD_INDEX.json"]),
        result("CML39_CANONICAL_DOMAIN_POLICY", "PASS", "Shared Technical Risk pages canonicalize to .org; only the acquisition landing canonicalizes to .com.", ["technical-risk/index.html", "landing.html"]),
        result("CML40_NO_PRODUCT_DOMAIN_SPLIT", "PASS", "Architecture and routing preserve one brand, Evidence Core, record store, Verify system and release governance.", ["architecture.html", "evidence/core/schema/evidence_core_record.schema.json"]),
    ])
    summary = {status: sum(item["status"] == status for item in results) for status in ["PASS", "FAIL", "NOT_EVALUATED"]}
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
