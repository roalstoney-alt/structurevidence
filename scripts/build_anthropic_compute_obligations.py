#!/usr/bin/env python3
"""Build and verify the minimal public-safe Anthropic case integration."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "SE-AI-COMPUTE-OBLIGATIONS-001"
BASE_SHA = "64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554"
REVIEWED_FINAL_HEAD = "0fc5f5146eb56c99c1b713c7f0e1470e95b719dd"
SOURCE_SHA256 = "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b"

PUBLIC_HASHES = {
    "agent-discovery/citation-resolvability-se-ai-compute-obligations-001-v0.2.json": "160e9469b31c90bfef6c28ec1676edef9ffeb15d46f1cf110b5cb4e8aeb37133",
    "agent-discovery/corpora/se-ai-compute-obligations-001-v0.2.jsonl": "78ef90685b6561560f9e45c47cba89d79296a71e1d3bf3c4ba736576dbc48c6e",
    "agent-discovery/fixtures/se-ai-compute-obligations-001-black-box-v0.2.json": "6f222cb3a8db4cf90541a43fa43e934f015161d97bfae79f2ce26e6491786989",
    "agent-discovery/fixtures/se-ai-compute-obligations-001-local-smoke-v0.2.json": "641e3a6c9210de3c4f9bf81ebbbae9015ecc578c738b96b1df5507d5be189447",
    "agent-discovery/temporal-semantics-se-ai-compute-obligations-001-v0.2.json": "57f5ee77645af35ad34d91843b7743cd07454af700b33d7e6c950dd6269fb06f",
    "cases/anthropic-compute-obligations/case-seo-v0.2.json": "a79fd50fa2b0c723f50df80c9bbc0e43d23ebc8662c5b9f3139d0a19251bbc3e",
    "cases/anthropic-compute-obligations/claims-v0.2.jsonl": "28c8399b7ee25c1421e0074026a5f7fd622ebd587bb906efb5395676b3e162b9",
    "cases/anthropic-compute-obligations/events-v0.2.jsonl": "f40f00bbe2e0c5ebd193e3d8e0f351d6b449251ea71e83a79fc2e57d83cf0616",
    "cases/anthropic-compute-obligations/index.html": "54cb99f1cca85b8702a816360992f28fc9dbbfd7ea9c50a1b948a036f3fa2400",
    "cases/anthropic-compute-obligations/index.json": "913e4df0dba8e6717db75ad6fec77ca79bd9d1909db7694b205cccf53b2334d9",
    "cases/anthropic-compute-obligations/platform-maintenance-gaps-v0.2.json": "20d2adc6463c57bc1c9f80525234e3048e88cfe60f9f8f7b18e4db73506d0d0f",
    "cases/anthropic-compute-obligations/research-gaps-v0.2.json": "6f468cc301af1cde12aeb53e37836ab0e14367e02c108eadf22e95a65582f14f",
    "cases/anthropic-compute-obligations/source-registry-public-v0.2.json": "a9a3eae19e5aceed36bbf1017c68623f545aec377d761ecbc03603ad68562d4f",
    "cases/anthropic-compute-obligations/structured-metadata-v0.2.json": "91c4501af9e6f53f4460ac224b0eccc3bcd33b2d1590c3d195c19a2d76c11144",
}

AUTHORIZED_CORRECTION_HASHES = {
    "agent-discovery/temporal-semantics-se-ai-compute-obligations-001-v0.2.json": "3bfa84f986fa87c9df1731c281508ec1d3a055466eb85cbad05e4aeac0bada7f",
    "cases/anthropic-compute-obligations/claims-v0.2.jsonl": "8952849a7841a443daee63052649e61aa1d556919205afa3ad5905edb9f5c2b6",
    "cases/anthropic-compute-obligations/index.json": "5c0aeb946e3c91941691827b3c1761fba3ff365d74c7335959e2c14a02505c4e",
    "cases/anthropic-compute-obligations/source-registry-public-v0.2.json": "8683e29fe0ceb0b93973db24ba5739fd07af2166fba4b7f00a02a7aac49f41e1",
}

ACTIVATION_FILES = (
    "cases/anthropic-compute-obligations/activation-projection-v0.2.json",
    "cases/anthropic-compute-obligations/publication-receipt-template-v0.2.json",
    "cases/anthropic-compute-obligations/publication-activation-event-template-v0.2.json",
)

SITEMAP_URLS = [
    "https://structurevidence.org/cases/anthropic-compute-obligations/",
    "https://structurevidence.org/cases/anthropic-compute-obligations/index.json",
    "https://structurevidence.org/cases/anthropic-compute-obligations/claims-v0.2.jsonl",
    "https://structurevidence.org/cases/anthropic-compute-obligations/source-registry-public-v0.2.json",
    "https://structurevidence.org/agent-discovery/corpora/se-ai-compute-obligations-001-v0.2.jsonl",
    "https://structurevidence.org/agent-discovery/citation-resolvability-se-ai-compute-obligations-001-v0.2.json",
]

FORBIDDEN_PUBLIC_PATHS = (
    "cases/anthropic-compute-obligations/source-captures",
    "cases/anthropic-compute-obligations/review",
    "cases/anthropic-compute-obligations/normalized",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_reviewed_files() -> None:
    for relative, expected in PUBLIC_HASHES.items():
        root_path = ROOT / relative
        docs_path = ROOT / "docs" / relative
        if not root_path.is_file():
            raise AssertionError(f"reviewed public file missing: {relative}")
        actual = digest(root_path)
        allowed_hashes = {expected}
        if relative in AUTHORIZED_CORRECTION_HASHES:
            allowed_hashes.add(AUTHORIZED_CORRECTION_HASHES[relative])
        if actual not in allowed_hashes:
            raise AssertionError(f"reviewed public file hash mismatch: {relative}")
        if not docs_path.is_file() or docs_path.read_bytes() != root_path.read_bytes():
            raise AssertionError(f"root/docs mirror mismatch: {relative}")
    for relative in FORBIDDEN_PUBLIC_PATHS:
        if (ROOT / relative).exists() or (ROOT / "docs" / relative).exists():
            raise AssertionError(f"forbidden private material present: {relative}")


def with_sitemap_urls(value: bytes) -> bytes:
    text = value.decode("utf-8")
    additions = "".join(
        f"<url><loc>{url}</loc><lastmod>2026-11-22</lastmod></url>\n"
        for url in SITEMAP_URLS
        if f"<loc>{url}</loc>" not in text
    )
    if "</urlset>" not in text:
        raise AssertionError("sitemap closing element missing")
    return text.replace("</urlset>", additions + "</urlset>").encode("utf-8")


def update_case_index_intro(value: bytes) -> bytes:
    text = value.decode("utf-8")
    replacements = {
        "Six on-site evidence trackers and one separately hosted provisional evidence study, plus an open inquiry and a frozen decision audit, each with explicit evidence boundaries.":
            "Seven on-site evidence trackers and one separately hosted provisional evidence study, plus an open inquiry and a frozen decision audit, each with explicit evidence boundaries.",
        "Six on-site evidence trackers, plus one external research study, one open inquiry, and one decision audit.":
            "Seven on-site evidence trackers, plus one external research study, one open inquiry, and one decision audit.",
        "Explore six on-site evidence trackers, including the owner-authorized IREN AI Cloud and time-bounded Binance security records.":
            "Explore seven on-site evidence trackers, including the issuer-attributed Anthropic compute-obligations case, owner-authorized IREN AI Cloud record, and time-bounded Binance security record.",
        "A seventh evidence research entry, the provisional Figure AI × BMW study, is hosted separately.":
            "An eighth evidence research entry, the provisional Figure AI × BMW study, is hosted separately.",
        "the seventh evidence research entry, not a seventh on-site tracker; it is excluded from the six-tracker review-status feed.":
            "the eighth evidence research entry, not an eighth on-site tracker; it is excluded from the seven-tracker review-status feed.",
    }
    for old, new in replacements.items():
        if old not in text and new not in text:
            raise AssertionError(f"case-index intro source text missing: {old}")
        text = text.replace(old, new)
    return text.encode("utf-8")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def jsonl_bytes(rows: list[dict]) -> bytes:
    return ("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for row in rows) + "\n").encode("utf-8")


def activation_projection() -> dict:
    return {
        "schema_version": "SE-AICO-GATED-ACTIVATION-PROJECTION-v0.2",
        "case_id": CASE_ID,
        "status": "GATED_ACTIVATION_PROJECTION_NOT_APPLIED",
        "current_candidate_state": {
            "creative_work_status": "PROPOSED_FINAL_RELEASE_NOT_PUBLISHED",
            "deployment_state": "NOT_APPLIED",
            "publication_authorized": False,
            "claim_record_published_at": None,
        },
        "activation_preconditions": [
            "OWNER_APPROVES_EXACT_PR_HEAD",
            "MERGE_AUTHORIZED_SEPARATELY",
            "DEPLOYMENT_AUTHORIZED_SEPARATELY",
            "ACTIVATED_COMMIT_LINKED_TO_DEPLOYMENT",
            "LIVE_CANONICAL_URL_RETURNS_EXPECTED_CASE",
        ],
        "proposed_append_only_event": {
            "event_id": None,
            "event_type": "PUBLICATION_ACTIVATION",
            "publication_event_at": None,
            "activated_commit_sha": None,
            "deployment_receipt_url": None,
            "live_case_url": "https://structurevidence.org/cases/anthropic-compute-obligations/",
            "supersedes_prepublication_records": False,
        },
        "activation_writes_only_after_event": {
            "structevidence_date_published": None,
            "claim_record_published_at": None,
            "deployment_state": "AWAIT_ACTUAL_EVENT",
            "publication_authorized": "AWAIT_SEPARATE_OWNER_AUTHORIZATION",
        },
        "history_policy": "APPEND_NEW_EVENT_AND_RECEIPT_DO_NOT_REWRITE_PREPUBLICATION_ROWS",
        "merge_authorized": False,
        "deployment_authorized": False,
        "external_agent_trial_authorized": False,
    }


def publication_receipt_template() -> dict:
    return {
        "schema_version": "SE-AICO-PUBLICATION-RECEIPT-TEMPLATE-v0.2",
        "case_id": CASE_ID,
        "status": "TEMPLATE_NOT_A_PUBLICATION_RECEIPT",
        "receipt_id": None,
        "publication_event_at": None,
        "activated_commit_sha": None,
        "deployment_id": None,
        "live_case_url": "https://structurevidence.org/cases/anthropic-compute-obligations/",
        "live_url_verified_at": None,
        "canonical_verified": False,
        "claim_anchor_count_verified": None,
        "root_docs_hashes_verified": False,
        "prepublication_history_rewritten": False,
        "append_only": True,
        "population_rule": "POPULATE_ONLY_AFTER_SEPARATELY_AUTHORIZED_DEPLOYMENT_AND_LIVE_URL_VERIFICATION",
    }


def publication_activation_event_template() -> dict:
    return {
        "schema_version": "SE-AICO-PUBLICATION-ACTIVATION-EVENT-v0.2",
        "case_id": CASE_ID,
        "event_id": None,
        "event_type": "PUBLICATION_ACTIVATION_VERIFIED",
        "owner_decision": None,
        "owner_authorized_at": None,
        "candidate_head_sha": None,
        "merge_commit_sha": None,
        "publication_event_at": None,
        "pages_workflow_run_id": None,
        "pages_deployment_id": None,
        "pages_deployment_status_id": None,
        "pages_deployment_succeeded_at": None,
        "pages_source_branch": "main",
        "pages_source_path": "/",
        "pages_trigger": "PUSH_TO_MAIN_AUTOMATIC_PAGES_BUILD",
        "deployment_environment": "github-pages",
        "deployment_status": None,
        "live_case_url": "https://structurevidence.org/cases/anthropic-compute-obligations/",
        "live_case_http_status": None,
        "live_case_sha256": None,
        "live_index_sha256": None,
        "live_claims_sha256": None,
        "live_verified_at": None,
        "source_sha256": "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b",
        "owner_review_gate": "OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION",
        "test_fixture": False,
        "template_status": "UNPOPULATED_NOT_AN_ACTIVATION_EVENT",
    }


def write_release_blockers() -> None:
    case = ROOT / "cases/anthropic-compute-obligations"
    snapshot = json.loads((case / "index.json").read_text(encoding="utf-8"))
    snapshot["confirmed_sec_public_filing_date"] = "2026-11-19"
    snapshot["source_document_published_at_legacy_semantics"] = "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
    snapshot["client_source_date_policy"] = {
        "confirmed_public_availability_field": "sec_filed_at",
        "confirmed_public_availability_date": "2026-11-19",
        "legacy_field": "source_document_published_at",
        "legacy_field_alias": "prospectus_dated_at",
        "must_not_infer_public_availability_from_legacy_field": True,
    }
    for claim in snapshot["claims"]:
        claim["confirmed_sec_public_filing_date"] = "2026-11-19"
        claim["source_document_published_at_legacy_semantics"] = "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
        claim["source_published_at_original_v02_semantics"] = "LEGACY_PROSPECTUS_DATE_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
    claims = [json.loads(line) for line in (case / "claims-v0.2.jsonl").read_text(encoding="utf-8").splitlines() if line]
    for claim in claims:
        claim["confirmed_sec_public_filing_date"] = "2026-11-19"
        claim["source_document_published_at_legacy_semantics"] = "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
        claim["source_published_at_original_v02_semantics"] = "LEGACY_PROSPECTUS_DATE_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
    registry = json.loads((case / "source-registry-public-v0.2.json").read_text(encoding="utf-8"))
    source = registry["sources"][0]
    source["confirmed_sec_public_filing_date"] = "2026-11-19"
    source["legacy_source_publication_date_v01_semantics"] = "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY"
    temporal_path = ROOT / "agent-discovery/temporal-semantics-se-ai-compute-obligations-001-v0.2.json"
    temporal = json.loads(temporal_path.read_text(encoding="utf-8"))
    temporal["confirmed_sec_public_filing_date"] = "2026-11-19"
    temporal["legacy_date_alias"] = {
        "field": "source_document_published_at",
        "alias": "prospectus_dated_at",
        "value": "2026-11-18",
        "not_public_availability_evidence": True,
    }
    outputs = {
        "cases/anthropic-compute-obligations/index.json": json_bytes(snapshot),
        "cases/anthropic-compute-obligations/claims-v0.2.jsonl": jsonl_bytes(claims),
        "cases/anthropic-compute-obligations/source-registry-public-v0.2.json": json_bytes(registry),
        "agent-discovery/temporal-semantics-se-ai-compute-obligations-001-v0.2.json": json_bytes(temporal),
        ACTIVATION_FILES[0]: json_bytes(activation_projection()),
        ACTIVATION_FILES[1]: json_bytes(publication_receipt_template()),
        ACTIVATION_FILES[2]: json_bytes(publication_activation_event_template()),
    }
    for relative, content in outputs.items():
        (ROOT / relative).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / relative).write_bytes(content)
        (ROOT / "docs" / relative).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / "docs" / relative).write_bytes(content)


def verify_release_blockers() -> None:
    snapshot = json.loads((ROOT / "cases/anthropic-compute-obligations/index.json").read_text(encoding="utf-8"))
    if snapshot["deployment_state"] != "NOT_APPLIED" or snapshot["publication_authorized"] is not False:
        raise AssertionError("pre-publication snapshot state was activated")
    if snapshot["claim_record_published_at"] is not None or snapshot["structevidence_publication_date"] is not None:
        raise AssertionError("publication timestamp was invented")
    if snapshot["client_source_date_policy"]["confirmed_public_availability_date"] != "2026-11-19":
        raise AssertionError("confirmed SEC public date policy missing")
    if not snapshot["client_source_date_policy"]["must_not_infer_public_availability_from_legacy_field"]:
        raise AssertionError("legacy-date inference guard missing")
    for claim in snapshot["claims"]:
        if claim["source_document_published_at"] != "2026-11-18" or claim["confirmed_sec_public_filing_date"] != "2026-11-19":
            raise AssertionError(f"date alias mismatch: {claim['claim_id']}")
        if claim["source_document_published_at_legacy_semantics"] != "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY":
            raise AssertionError(f"legacy date semantics missing: {claim['claim_id']}")
    metadata = json.loads((ROOT / "cases/anthropic-compute-obligations/structured-metadata-v0.2.json").read_text(encoding="utf-8"))
    if metadata["creativeWorkStatus"] != "PROPOSED_FINAL_RELEASE_NOT_PUBLISHED" or metadata["datePublished"] is not None:
        raise AssertionError("structured metadata no longer represents a draft")
    activation = json.loads((ROOT / ACTIVATION_FILES[0]).read_text(encoding="utf-8"))
    receipt = json.loads((ROOT / ACTIVATION_FILES[1]).read_text(encoding="utf-8"))
    event_template = json.loads((ROOT / ACTIVATION_FILES[2]).read_text(encoding="utf-8"))
    if activation["proposed_append_only_event"]["publication_event_at"] is not None or activation["merge_authorized"]:
        raise AssertionError("activation projection invents an event or authorization")
    if receipt["status"] != "TEMPLATE_NOT_A_PUBLICATION_RECEIPT" or receipt["publication_event_at"] is not None:
        raise AssertionError("receipt template masquerades as a publication receipt")
    if event_template["template_status"] != "UNPOPULATED_NOT_AN_ACTIVATION_EVENT":
        raise AssertionError("activation event template masquerades as an actual event")
    if any(event_template[field] is not None for field in (
        "event_id", "owner_decision", "owner_authorized_at", "candidate_head_sha", "merge_commit_sha",
        "publication_event_at", "pages_workflow_run_id", "pages_deployment_id", "pages_deployment_status_id",
        "pages_deployment_succeeded_at", "deployment_status", "live_case_http_status", "live_case_sha256",
        "live_index_sha256", "live_claims_sha256", "live_verified_at",
    )):
        raise AssertionError("activation event template contains invented event or deployment data")
    for relative in ACTIVATION_FILES:
        if (ROOT / relative).read_bytes() != (ROOT / "docs" / relative).read_bytes():
            raise AssertionError(f"activation root/docs mirror mismatch: {relative}")


def write_outputs() -> None:
    verify_reviewed_files()
    write_release_blockers()
    case_index = update_case_index_intro((ROOT / "cases/index.html").read_bytes())
    (ROOT / "cases/index.html").write_bytes(case_index)
    (ROOT / "docs/cases/index.html").write_bytes(case_index)
    review = load_module("aico_review_status", ROOT / "scripts/export_case_review_status.py")
    review.export(ROOT)
    agent = load_module("aico_agent_discovery", ROOT / "scripts/build_agent_discovery.py")
    for relative, content in agent.build_outputs().items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    sitemap = with_sitemap_urls((ROOT / "sitemap.xml").read_bytes())
    (ROOT / "sitemap.xml").write_bytes(sitemap)
    (ROOT / "docs/sitemap.xml").write_bytes(sitemap)


def check_outputs() -> None:
    verify_reviewed_files()
    verify_release_blockers()
    page = (ROOT / "cases/index.html").read_text(encoding="utf-8")
    if CASE_ID not in page or "/cases/anthropic-compute-obligations/" not in page:
        raise AssertionError("case index integration missing")
    if "Seven on-site evidence trackers" not in page or "seven-tracker review-status feed" not in page:
        raise AssertionError("case-index inventory copy is stale")
    if 'meta name="description" content="Seven on-site evidence trackers' not in page:
        raise AssertionError("case-index SEO description count is stale")
    status = json.loads((ROOT / "cases/review-status.json").read_text(encoding="utf-8"))
    row = next((item for item in status["cases"] if item["case_id"] == CASE_ID), None)
    if not row or row["last_reviewed_at"] is not None or row["period"]["status"] != "NOT_YET_REVIEWED":
        raise AssertionError("truthful review-status projection missing")
    claims_index = json.loads((ROOT / "claims/index.json").read_text(encoding="utf-8"))
    discovery = json.loads((ROOT / ".well-known/structurevidence.json").read_text(encoding="utf-8"))
    if claims_index.get("versioned_adapters", [{}])[0].get("case_id") != CASE_ID:
        raise AssertionError("claims index adapter missing")
    if discovery.get("versioned_case_adapters", [{}])[0].get("case_id") != CASE_ID:
        raise AssertionError("Agent discovery adapter missing")
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    for url in SITEMAP_URLS:
        if f"<loc>{url}</loc>" not in sitemap:
            raise AssertionError(f"sitemap URL missing: {url}")
    mirror_pairs = [
        ("cases/index.html", "docs/cases/index.html"),
        ("cases/review-status.json", "docs/cases/review-status.json"),
        ("claims/index.json", "docs/claims/index.json"),
        (".well-known/structurevidence.json", "docs/.well-known/structurevidence.json"),
        ("sitemap.xml", "docs/sitemap.xml"),
    ]
    for root_relative, docs_relative in mirror_pairs:
        if (ROOT / root_relative).read_bytes() != (ROOT / docs_relative).read_bytes():
            raise AssertionError(f"global root/docs mirror mismatch: {root_relative}")
    agent = load_module("aico_agent_discovery_check", ROOT / "scripts/build_agent_discovery.py")
    for relative, content in agent.build_outputs().items():
        if (ROOT / relative).read_bytes() != content:
            raise AssertionError(f"stale Agent discovery output: {relative}")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.write:
        write_outputs()
        check_outputs()
        print("PASS: wrote minimal public-safe Anthropic integration")
    else:
        check_outputs()
        print("PASS: minimal public-safe Anthropic integration is deterministic and current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
