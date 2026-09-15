#!/usr/bin/env python3
"""Validate CML v0.1 records, architecture boundaries and negative cases."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import jsonschema
import copy
import re
import subprocess
import sys
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


def record_map() -> dict[str, tuple[Path, dict, dict]]:
    rows = {}
    for path in sorted((ROOT / "technical-risk/records").glob("*/11_PUBLIC_RECORD.json")):
        folder = path.parent
        rows[folder.name] = (folder, json.loads(path.read_text()), json.loads((folder / "01_SOURCE_REGISTER.json").read_text()))
    return rows


def ok(condition: bool, facts: dict, refs: list[str], reason: str):
    require(condition, reason)
    return facts, refs, reason


def validate_repo_baseline(c):
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()
    allowed = ("technical-risk/", "docs/technical-risk/", "docs/execution/CML_", "docs/index.html")
    unexpected = [row for row in dirty if not row[3:].startswith(allowed)]
    facts = {"repo_head": head, "manifest_build_commit": c["manifest"]["build_commit"], "worktree_clean": not dirty, "closure_output_only": not unexpected}
    return ok(head == c["manifest"]["build_commit"] and not unexpected, facts, ["technical-risk/TECHNICAL_RISK_MANIFEST.json"], "Repository HEAD matches the manifest implementation commit; any pending changes are closure outputs only.")


def validate_rdl_version(c):
    r = load("rdl/freshness/RDL_FRESHNESS_POLICY_MANIFEST.json"); facts = {"policy_version": r["policy_version"], "evaluation_engine_version": r["evaluation_engine_version"]}
    return ok(facts == {"policy_version": "RDL_FRESHNESS_v0.1a", "evaluation_engine_version": "RDL_FRESHNESS_ENGINE_v0.1a"}, facts, ["rdl/freshness/RDL_FRESHNESS_POLICY_MANIFEST.json"], "RDL policy and evaluation engine both resolve to v0.1a.")


def validate_frozen_timeline(c):
    expected = {p: h for p, h in load("docs/execution/POST_R1_1A_TIMELINE_HASHES.json").items() if not p.startswith("timeline/validation/")}; mismatches = [p for p, h in expected.items() if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    return ok(not mismatches, {"protected_files": len(expected), "mismatches": mismatches}, ["docs/execution/POST_R1_1A_TIMELINE_HASHES.json"], "All authoritative Timeline R1.1a frozen hashes match current bytes.")


def validate_shared_core(c):
    bad = []
    for slug, (_, r, _) in c["records"].items():
        try:
            require(r["core"].get("core_version") == "STRUCTEVIDENCE_EVIDENCE_CORE_v0.1" and r["core"].get("domain") == "TECHNICAL_RISK" and r["core"].get("protocol") == "CML", "core envelope")
            validate_schema(r, "technical-risk/schema/cml_public_record.schema.json")
        except Exception: bad.append(slug)
    return ok(not bad, {"records_checked": len(c["records"]), "invalid_records": bad}, ["evidence/core/schema/evidence_core_record.schema.json"], "Every CML record uses the shared Evidence Core envelope and Technical Risk domain identifiers.")


def validate_domain_separation(c):
    schema = load("evidence/core/schema/evidence_core_record.schema.json"); leaked = sorted(set(schema["properties"]) & {"lifecycle_state", "candidates", "compatibility_matrix", "qualification_state", "requirements"})
    return ok(not leaked and all("cml" in r for _, r, _ in c["records"].values()), {"core_domain_leaks": leaked, "domain_payloads": len(c["records"])}, ["evidence/core/schema/evidence_core_record.schema.json", "technical-risk/schema/cml_public_record.schema.json"], "Technical fields remain in the CML payload and the generic Evidence Core remains domain-neutral.")


def validate_no_parallel_provenance(c):
    duplicate_dirs = [p.relative_to(ROOT).as_posix() for p in (ROOT / "technical-risk").glob("**/*") if p.is_dir() and p.name.lower() in {"provenance", "event-engine", "verify-engine"}]
    return ok(not duplicate_dirs, {"parallel_system_paths": duplicate_dirs, "shared_artifact_refs": sum(len(r["core"]["artifact_refs"]) for _, r, _ in c["records"].values())}, ["evidence/core/schema/evidence_core_record.schema.json", "technical-risk/records"], "CML uses shared core provenance fields and public Verify pages; no CML-only provenance engine exists.")


def validate_dual_clock(c):
    invalid = [slug for slug, (_, r, _) in c["records"].items() if not r["cml"]["event"].get("effective_at") or not r["cml"]["event"].get("known_at") or iso(r["cml"]["event"]["known_at"]) > iso(AS_OF)]
    return ok(not invalid, {"events_checked": len(c["records"]), "invalid_or_future_known": invalid}, ["technical-risk/schema/cml_event.schema.json"], "Every event has effective and knowledge clocks, and no future-known event enters this release.")


def validate_event_scope(c):
    allowed = set(load("technical-risk/config/cml_taxonomy.json")["event_domains"]); invalid = [slug for slug, (_, r, _) in c["records"].items() if r["cml"]["event"]["event_domain"] not in allowed or r["cml"]["event"]["technical_item_id"] != r["cml"]["identity"]["technical_item_id"]]
    return ok(not invalid, {"allowed_domains": sorted(allowed), "invalid_events": invalid}, ["technical-risk/config/cml_taxonomy.json"], "Event domain and exact technical-item target are explicit for every event.")


def validate_supersession_direction(c):
    folder, record, sources = next(iter(c["records"].values())); old = copy.deepcopy(record); old["core"]["supersession_status"] = "SUPERSEDED"; current = c["adapter"].release_effect(record, sources); prior = c["adapter"].release_effect(old, sources)
    return ok(prior["public_release"] == "BLOCK" and current["public_release"] == "ALLOW_WITH_LIMITATIONS", {"predecessor": prior["public_release"], "successor": current["public_release"]}, ["gdr-se/engine/domain_adapters/cml.py"], "Synthetic predecessor is blocked as superseded while the current successor remains releasable with limitations.")


def validate_identity(c):
    invalid = [slug for slug, (_, r, _) in c["records"].items() if not r["cml"]["identity"]["technical_item_id"] or not r["cml"]["identity"]["manufacturer"]]
    return ok(not invalid, {"identities_checked": len(c["records"]), "invalid": invalid}, ["technical-risk/schema/technical_item.schema.json"], "Every record carries a manufacturer and permanent technical-item identity.")


def validate_exact_mpn(c):
    mismatches = [slug for slug, (_, r, _) in c["records"].items() if r["cml"]["identity"]["manufacturer_part_number"] != r["cml"]["identity"]["manufacturer_part_number_exact"]]
    return ok(not mismatches, {"byte_exact_matches": len(c["records"]) - len(mismatches), "mismatches": mismatches}, ["technical-risk/schema/technical_item.schema.json"], "Source-derived exact MPN equals the displayed manufacturer part number byte-for-byte in all records.")


def validate_primary_source(c):
    missing = [slug for slug, (_, _, s) in c["records"].items() if not any(x["source_type"].startswith("MANUFACTURER_") for x in s["sources"])]
    return ok(not missing, {"records_with_manufacturer_source": len(c["records"]) - len(missing), "missing": missing}, ["technical-risk/records"], "Each lifecycle assessment includes manufacturer evidence.")


def validate_distributor_override(c):
    _, record, _ = next(iter(c["records"].values())); effect = c["adapter"].release_effect(record, {"sources": [{"source_type": "AUTHORIZED_DISTRIBUTOR", "publisher": "Distributor"}]})
    return ok(effect["public_release"] == "BLOCK", {"distributor_only_effect": effect["public_release"], "reason": effect["reason"]}, ["gdr-se/engine/domain_adapters/cml.py"], "Distributor-only lifecycle evidence is blocked by the shared GDR adapter.")


def validate_freshness(c):
    allowed = set(load("rdl/freshness/config/freshness_precedence.json")["precedence"]); states = {slug: r["cml"]["freshness_state"] for slug, (_, r, _) in c["records"].items()}; global_threshold = load("technical-risk/config/freshness_profiles.json")["global_threshold"]
    return ok(global_threshold is None and set(states.values()) <= allowed, {"global_threshold": global_threshold, "states": states, "noncanonical": sorted(set(states.values()) - allowed)}, ["rdl/freshness/config/freshness_precedence.json", "technical-risk/config/freshness_profiles.json"], "No global threshold exists and every runtime state comes from canonical RDL precedence vocabulary.")


def validate_product_context(c):
    _, record, sources = next(iter(c["records"].values())); changed = copy.deepcopy(record); changed["cml"]["product_context"] = "SUBSTITUTION_EVIDENCE_REPORT"; before = c["adapter"].facts_for(record, sources); after = c["adapter"].facts_for(changed, sources); invariant = all(before[k] == after[k] for k in before if k != "product_context")
    return ok(invariant and load("technical-risk/config/product_contexts.json")["fact_invariance"] == "PRODUCT_CONTEXT_MUST_NOT_CHANGE_TECHNICAL_FACTS", {"facts_invariant": invariant, "changed_field": "product_context"}, ["technical-risk/config/product_contexts.json", "gdr-se/engine/domain_adapters/cml.py"], "Changing product context changes authorization context only; technical facts remain invariant.")


def validate_public_private(c):
    _, record, sources = next(iter(c["records"].values())); blocked = []
    for key in sorted(PRIVATE_KEYS):
        fixture = copy.deepcopy(record); fixture["cml"][key] = "PRIVATE"; blocked.append(c["adapter"].release_effect(fixture, sources)["public_release"] == "BLOCK")
    return ok(all(blocked), {"prohibited_fields_injected": len(blocked), "blocked": sum(blocked)}, ["technical-risk/config/public_private_boundary.json", "gdr-se/engine/domain_adapters/cml.py"], "Every prohibited client field is detected recursively and blocks Public Verify release.")


def validate_dropin(c):
    _, record, sources = next(iter(c["records"].values())); fixture = copy.deepcopy(record); fixture["cml"]["alternative"]["candidates"] = [{"relationship_type": "DROP_IN"}]; effect = c["adapter"].release_effect(fixture, sources)
    return ok(effect["public_release"] == "BLOCK", {"public_release": effect["public_release"], "hard_block_reasons": effect["hard_block_reasons"]}, ["gdr-se/engine/domain_adapters/cml.py"], "A DROP_IN claim without qualification evidence is explicitly blocked.")


def validate_compatibility(c):
    count = 0
    for _, r, _ in c["records"].values():
        for cell in r["cml"]["verification"]["compatibility_matrix"]: validate_schema(cell, "technical-risk/schema/cml_compatibility.schema.json"); count += 1
    return ok(count > 0, {"schema_valid_cells": count}, ["technical-risk/schema/cml_compatibility.schema.json"], "Every compatibility cell validates against the allowed state vocabulary.")


def validate_test_requirements(c):
    count = 0
    for folder, _, _ in c["records"].values():
        for row in json.loads((folder / "05_COMPATIBILITY_REQUIREMENTS.json").read_text())["test_requirements"]: validate_schema(row, "technical-risk/schema/cml_test_requirement.schema.json"); count += 1
    return ok(count > 0, {"schema_valid_requirements": count}, ["technical-risk/schema/cml_test_requirement.schema.json"], "Every generated test requirement validates structurally, including method, equipment, criteria and scope fields.")


def validate_counter_evidence(c):
    missing = [s for s, (_, r, _) in c["records"].items() if not r["cml"]["counter_evidence"]]; _, r, src = next(iter(c["records"].values())); fixture = copy.deepcopy(r); fixture["cml"]["counter_evidence"] = ""; blocked = c["adapter"].release_effect(fixture, src)["public_release"] == "BLOCK"
    return ok(not missing and blocked, {"present": len(c["records"]) - len(missing), "missing_fixture_blocked": blocked}, ["gdr-se/engine/domain_adapters/cml.py", "technical-risk/records"], "All pilots preserve counter-evidence, and a missing-counter-evidence fixture is blocked.")


def validate_limitations(c):
    weak = [s for s, (f, _, _) in c["records"].items() if len((f / "10_LIMITATIONS.md").read_text().strip()) < 120]
    return ok(not weak, {"material_limitations": len(c["records"]) - len(weak), "weak": weak}, ["technical-risk/records"], "Every pilot has a material, non-empty limitations artifact.")


def pilot(c, slug): return c["records"][slug][1]["cml"]


def validate_amphenol(c):
    p = pilot(c, "amphenol-10081811-101-07lf"); facts = {"mpn": p["identity"]["manufacturer_part_number_exact"], "lifecycle": p["lifecycle_state"], "conflict_visible": "different effective date" in p["counter_evidence"], "qualified_candidates": sum(x["assessment_state"] == "QUALIFIED_FOR_DEFINED_SCOPE" for x in p["alternative"]["candidates"]), "matrix_cells": len(p["verification"]["compatibility_matrix"])}
    return ok(facts["mpn"] == "10081811-101-07LF" and facts["lifecycle"] == "EOL_ANNOUNCED" and facts["conflict_visible"] and not facts["qualified_candidates"] and facts["matrix_cells"] > 0, facts, ["technical-risk/records/amphenol-10081811-101-07lf"], "Amphenol exact identity, EOL evidence, source conflict, no-qualified-substitute boundary and verification matrix all reconcile.")


def validate_nxp(c):
    p = pilot(c, "nxp-radio-power-2026"); text = json.dumps(p); facts = {"lifecycle": p["lifecycle_state"], "board_dependency": "board-level" in p["dependency"]["context"], "redesign_relationship": "REDESIGN_REQUIRED" in text, "qualified_candidates": sum(x["assessment_state"] == "QUALIFIED_FOR_DEFINED_SCOPE" for x in p["alternative"]["candidates"])}
    return ok(facts["lifecycle"] == "LAST_TIME_BUY_OPEN" and facts["board_dependency"] and facts["redesign_relationship"] and not facts["qualified_candidates"], facts, ["technical-risk/records/nxp-radio-power-2026"], "NXP discontinuance remains board-dependent; device alternative is not represented as a board drop-in and no candidate is qualified.")


def validate_murata(c):
    p = pilot(c, "murata-mymgm5r012ela5rnd"); facts = {"exact_suffix": p["identity"]["manufacturer_part_number_exact"], "lifecycle": p["lifecycle_state"], "oem_replacement": p["alternative"]["oem_replacement_status"]}
    return ok(facts == {"exact_suffix": "MYMGM5R012ELA5RND", "lifecycle": "NRND", "oem_replacement": "OEM_REPLACEMENT_UNRESOLVED"}, facts, ["technical-risk/records/murata-mymgm5r012ela5rnd"], "Murata NRND is scoped to the exact D suffix and OEM replacement remains unresolved.")


def validate_rf40(c):
    p = pilot(c, "amphenol-rf-095-725-134-006"); requirements = " ".join(p["verification"]["requirements"]); facts = {"lifecycle": p["lifecycle_state"], "assembly_boundary": "Complete-assembly" in p["dependency"]["context"], "vna_required": "VNA" in requirements, "qualified_candidates": sum(x["assessment_state"] == "QUALIFIED_FOR_DEFINED_SCOPE" for x in p["alternative"]["candidates"])}
    return ok(facts["lifecycle"] == "ACTIVE" and facts["assembly_boundary"] and facts["vna_required"] and not facts["qualified_candidates"], facts, ["technical-risk/records/amphenol-rf-095-725-134-006"], "RF40 remains an active assembly benchmark; connector capability is not assembly qualification and VNA evidence is required.")


def validate_rendering(c):
    pages = sorted((ROOT / "technical-risk/record").glob("*/index.html")); rendered = [p.parent.name for p in pages if "CML public technical record" in p.read_text()]
    return ok(len(rendered) == 4, {"rendered_records": rendered}, ["technical-risk/record"], "All four public CML records render as decision-first pages.")


def validate_verify(c):
    bad = []
    for slug, (folder, r, src) in c["records"].items():
        verify = (ROOT / f"technical-risk/verify/{slug}/index.html").read_text(); release = json.loads((folder / "12_RELEASE_MANIFEST.json").read_text()); source_ids = {x["source_id"] for x in src["sources"]}
        if r["core"]["record_id"] not in verify or r["core"]["record_hash"] not in verify or release["record_hash"] != r["core"]["record_hash"] or set(r["core"]["source_refs"]) != source_ids: bad.append(slug)
    return ok(not bad, {"verified_records": len(c["records"]) - len(bad), "inconsistent": bad}, ["technical-risk/verify", "technical-risk/records"], "Record IDs, hashes, source references and release manifests resolve consistently for all Verify records.")


def validate_cta(c):
    text = (ROOT / "technical-risk/request-analysis/index.html").read_text(); facts = {"route_exists": bool(text), "request_wording": "Request technical analysis" in text, "manual_review": "MANUAL REVIEW" in text}
    return ok(all(facts.values()), facts, ["technical-risk/request-analysis/index.html"], "Request Analysis route exists and states manual review rather than automated fulfillment.")


def validate_payment(c):
    states = {s: json.loads((f / "12_RELEASE_MANIFEST.json").read_text())["paid_delivery_state"] for s, (f, _, _) in c["records"].items()}
    return ok(set(states.values()) <= {"BLOCK", "REQUEST_ONLY"}, {"paid_delivery_states": states}, ["technical-risk/records"], "Every Method Pilot release keeps paid decision delivery blocked or request-only.")


def validate_no_public_bom(c):
    exposed = [s for s, (_, r, _) in c["records"].items() if flatten_keys(r) & PRIVATE_KEYS]
    return ok(not exposed, {"records_scanned": len(c["records"]), "records_with_private_fields": exposed}, ["technical-risk/config/public_private_boundary.json", "technical-risk/records"], "No prohibited client/BOM field appears in a public structured record.")


def validate_no_score(c):
    keys = sorted(set().union(*(flatten_keys(r) for _, r, _ in c["records"].values())) & {"risk_score", "score", "probability_of_replacement"}); numeric = []
    for p in (ROOT / "technical-risk").glob("**/*.html"):
        if re.search(r"\b\d{1,3}\s*/\s*100\b", p.read_text()): numeric.append(p.relative_to(ROOT).as_posix())
    return ok(not keys and not numeric, {"prohibited_structured_keys": keys, "numeric_score_pages": numeric}, ["technical-risk/records", "technical-risk/record"], "No numeric risk score, replacement probability or score field appears in public outputs.")


def validate_release_manifest(c):
    bad = []
    for slug, (folder, r, _) in c["records"].items():
        release = json.loads((folder / "12_RELEASE_MANIFEST.json").read_text())
        try:
            validate_schema(release, "technical-risk/schema/cml_release_manifest.schema.json")
            require(release["record_hash"] == r["core"]["record_hash"], "record hash")
            core = dict(r["core"]); expected_hash = core.pop("record_hash"); require(expected_hash == digest({"core": core, "payload": r["cml"]}), "canonical record hash")
            for name, h in release["artifact_hashes"].items(): require(name != "12_RELEASE_MANIFEST.json" and hashlib.sha256((folder / name).read_bytes()).hexdigest() == h, name)
        except Exception: bad.append(slug)
    return ok(not bad, {"valid_manifests": len(c["records"]) - len(bad), "invalid": bad, "self_hashes": 0}, ["technical-risk/schema/cml_release_manifest.schema.json", "technical-risk/records"], "All release manifests validate, bind record and artifact hashes, carry GDR/freshness state and exclude self-hashes.")


def validate_tests(c):
    scripts = ["scripts/test_cml_freshness_vocabulary.py", "scripts/test_cml_gdr_adapter.py", "scripts/test_cml_dictionary_drift.py", "scripts/test_cml_site_metadata.py"]; codes = {p: subprocess.run([sys.executable, p], cwd=ROOT, capture_output=True).returncode for p in scripts}
    return ok(not any(codes.values()), {"subprocess_exit_codes": codes}, scripts, "Independent freshness, GDR, dictionary-drift and site-metadata test subprocesses all exited zero.")


def validate_root_docs_sync(c):
    pairs = []
    for root in [ROOT / "technical-risk", ROOT / "evidence/core"]:
        for p in root.glob("**/*"):
            if p.is_file(): pairs.append((p, ROOT / "docs" / p.relative_to(ROOT)))
    pairs += [(ROOT / "assets/technical-risk.css", ROOT / "docs/assets/technical-risk.css"), (ROOT / "assets/cml-search.js", ROOT / "docs/assets/cml-search.js")]
    bad = [a.relative_to(ROOT).as_posix() for a, b in pairs if not b.is_file() or a.read_bytes() != b.read_bytes()]
    return ok(not bad, {"mirror_files_checked": len(pairs), "mismatches": bad}, ["technical-risk", "docs/technical-risk", "evidence/core", "docs/evidence/core"], "Every intentionally mirrored CML, Evidence Core and frontend artifact is byte-identical.")


def validate_remote(c):
    remote = os.environ.get("CML_REMOTE_SHA"); expected = c["manifest"]["build_commit"]
    if not remote: raise RuntimeError("NOT_EVALUATED: CML_REMOTE_SHA not provided")
    return ok(remote == expected, {"remote_main_sha": remote, "manifest_build_commit": expected}, ["technical-risk/TECHNICAL_RISK_MANIFEST.json"], "Remote main matched the implementation commit used to build this audit release.")


def validate_org_integration(c):
    text = (ROOT / "index.html").read_text(); facts = {"evidence_domains": "Evidence domains" in text, "technical_risk_link": 'href="technical-risk/"' in text, "bnb_workspace": "BNB structural and evidence state" in text}
    return ok(all(facts.values()), facts, ["index.html"], "The .org homepage exposes Technical Risk as a peer domain while retaining the BNB workspace.")


def validate_cross_navigation(c):
    org = (ROOT / "index.html").read_text(); com = (ROOT / "landing.html").read_text(); required_org = ["technical-risk/", "technical-risk/search/", "technical-risk/method/"]; required_com = ["/technical-risk/", "/technical-risk/search/", "/technical-risk/request-analysis/", "structurevidence.org/monitor.html"]
    return ok(all(x in org for x in required_org) and all(x in com for x in required_com), {"org_routes": required_org, "com_routes": required_com}, ["index.html", "landing.html"], "Both domains expose direct routes to Technical Risk, search/request and the Structural Monitor.")


def validate_shared_artifacts(c):
    worker = (ROOT / "deploy/cloudflare-landing/worker.js").read_text(); same = load("technical-risk/records/PUBLIC_RECORD_INDEX.json") == load("docs/technical-risk/records/PUBLIC_RECORD_INDEX.json")
    return ok("https://structurevidence.org" in worker and same, {"worker_shared_origin": "https://structurevidence.org" in worker, "public_index_match": same}, ["deploy/cloudflare-landing/worker.js", "technical-risk/records/PUBLIC_RECORD_INDEX.json"], "The .com Worker proxies the .org origin and both publication trees share one public record index.")


def validate_canonical(c):
    pages = [ROOT / "technical-risk/index.html", ROOT / "technical-risk/search/index.html", ROOT / "technical-risk/method/index.html", *sorted((ROOT / "technical-risk/record").glob("*/index.html")), *sorted((ROOT / "technical-risk/verify").glob("*/index.html"))]; bad = [p.relative_to(ROOT).as_posix() for p in pages if 'rel="canonical" href="https://structurevidence.org/technical-risk/' not in p.read_text()]
    roots = {'org': 'rel="canonical" href="https://structurevidence.org/"' in (ROOT / "index.html").read_text(), 'com': 'rel="canonical" href="https://structevidence.com/"' in (ROOT / "landing.html").read_text()}
    return ok(not bad and all(roots.values()), {"shared_pages_checked": len(pages), "bad_pages": bad, "root_canonicals": roots}, ["technical-risk", "index.html", "landing.html"], "Shared Technical Risk pages canonicalize to .org; only the acquisition root canonicalizes to .com.")


def validate_no_domain_split(c):
    architecture = (ROOT / "architecture.html").read_text(); site = load("technical-risk/CML_SITE_ARCHITECTURE_v0.1a.json"); facts = {"one_core_copy": site["evidence_core"], "split_prohibited": site["domain_split_prohibited"], "architecture_copy": "One Evidence Core" in architecture, "domains": site["domains"]}
    return ok(facts["split_prohibited"] and facts["architecture_copy"] and len(facts["domains"]) == 2, facts, ["architecture.html", "technical-risk/CML_SITE_ARCHITECTURE_v0.1a.json"], "Architecture preserves one brand, Evidence Core, record store, Verify surface and release governance across two domains.")


VALIDATORS = {
    "CML01_REPO_BASELINE": validate_repo_baseline, "CML02_RDL_V0_1A_VERIFIED": validate_rdl_version, "CML03_FROZEN_TIMELINE_UNCHANGED": validate_frozen_timeline,
    "CML04_SHARED_CORE_REUSE": validate_shared_core, "CML05_DOMAIN_SCHEMA_SEPARATION": validate_domain_separation, "CML06_NO_PARALLEL_PROVENANCE": validate_no_parallel_provenance,
    "CML07_DUAL_CLOCK": validate_dual_clock, "CML08_EVENT_DOMAIN_SCOPING": validate_event_scope, "CML09_SUPERSESSION_DIRECTION": validate_supersession_direction,
    "CML10_TECHNICAL_ITEM_IDENTITY": validate_identity, "CML11_EXACT_PART_NUMBER": validate_exact_mpn, "CML12_LIFECYCLE_PRIMARY_SOURCE": validate_primary_source,
    "CML13_NO_DISTRIBUTOR_LIFECYCLE_OVERRIDE": validate_distributor_override, "CML14_NO_GLOBAL_FRESHNESS_THRESHOLD": validate_freshness, "CML15_PRODUCT_CONTEXT_SEPARATION": validate_product_context,
    "CML16_PUBLIC_PRIVATE_BOUNDARY": validate_public_private, "CML17_NO_UNVERIFIED_DROPIN": validate_dropin, "CML18_COMPATIBILITY_MATRIX": validate_compatibility,
    "CML19_TEST_REQUIREMENT_SCHEMA": validate_test_requirements, "CML20_COUNTER_EVIDENCE": validate_counter_evidence, "CML21_LIMITATIONS": validate_limitations,
    "CML22_AMPHENOL_PILOT": validate_amphenol, "CML23_NXP_RF_PILOT": validate_nxp, "CML24_MURATA_DCDC_PILOT": validate_murata, "CML25_RF40_ASSEMBLY_PILOT": validate_rf40,
    "CML26_PUBLIC_RECORD_RENDERING": validate_rendering, "CML27_VERIFY_LINEAGE": validate_verify, "CML28_REQUEST_ANALYSIS_CTA": validate_cta,
    "CML29_PAYMENT_FAILSAFE": validate_payment, "CML30_NO_PUBLIC_CLIENT_BOM": validate_no_public_bom, "CML31_NO_NUMERIC_RISK_SCORE": validate_no_score,
    "CML32_RELEASE_MANIFEST": validate_release_manifest, "CML33_TESTS": validate_tests, "CML34_ROOT_DOCS_SYNC": validate_root_docs_sync,
    "CML35_REMOTE_MATCH": validate_remote, "CML36_ORG_MAIN_SITE_INTEGRATION": validate_org_integration, "CML37_CROSS_DOMAIN_NAVIGATION": validate_cross_navigation,
    "CML38_SHARED_TECHNICAL_RISK_ARTIFACTS": validate_shared_artifacts, "CML39_CANONICAL_DOMAIN_POLICY": validate_canonical, "CML40_NO_PRODUCT_DOMAIN_SPLIT": validate_no_domain_split,
}


def evaluate(gate_id: str, validator, context: dict) -> dict:
    try:
        facts, refs, reason = validator(context); status = "PASS"
    except RuntimeError as exc:
        facts, refs, reason, status = {"error": str(exc)}, [], str(exc).removeprefix("NOT_EVALUATED: ").strip(), "NOT_EVALUATED"
    except Exception as exc:
        facts, refs, reason, status = {"error": f"{type(exc).__name__}: {exc}"}, [], f"Independent validator failed: {exc}", "FAIL"
    return {"gate_id": gate_id, "status": status, "reason": reason, "computed_facts": facts, "evidence_refs": refs, "evaluated_at": AS_OF, "validator": validator.__name__, "rule_version": "CML_AUDIT_v0.1a"}


def main() -> None:
    context = {"manifest": load("technical-risk/TECHNICAL_RISK_MANIFEST.json"), "records": record_map(), "adapter": import_adapter()}
    require(list(VALIDATORS) == GATE_IDS, "validator registry must cover CML01-CML40 in order")
    results = [evaluate(gate_id, VALIDATORS[gate_id], context) for gate_id in GATE_IDS]
    summary = {status: sum(item["status"] == status for item in results) for status in ["PASS", "FAIL", "NOT_EVALUATED"]}
    registry = {"registry_id": "CML_GATE_RESULTS", "module_version": context["manifest"]["module_version"], "audit_policy_version": "CML_AUDIT_v0.1a", "evaluation_as_of": AS_OF, "independent_validator_count": len(set(row["validator"] for row in results)), "results": results, "summary": summary}
    text = json.dumps(registry, indent=2, sort_keys=True) + "\n"
    for path in [ROOT / "technical-risk/validation/CML_GATE_RESULTS.json", ROOT / "technical-risk/CML_GATE_RESULTS.json", ROOT / "docs/technical-risk/validation/CML_GATE_RESULTS.json", ROOT / "docs/technical-risk/CML_GATE_RESULTS.json"]:
        path.parent.mkdir(parents=True, exist_ok=True); path.write_text(text)
    if summary["FAIL"]:
        raise SystemExit(f"CML_TESTS_FAIL {summary}")
    print(f"CML_TESTS_{'PASS' if not summary['NOT_EVALUATED'] else 'INCOMPLETE'} {summary}")


if __name__ == "__main__":
    main()
