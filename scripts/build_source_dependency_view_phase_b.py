#!/usr/bin/env python3
"""Build the grounded Phase B 800VDC source-dependency ledger and view."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from source_dependency_v01 import (
    deterministic_metrics,
    evaluate_qualification,
    load_rules,
    seal_record,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "protocol/source-dependency/qualification-rules-v0.2.json"
BASELINE_PATH = ROOT / "docs/implementation/SE-DUAL-SITE-002-BASELINE-SHA256.json"
REVIEWED_AT = "2026-10-25T02:59:00Z"
EVIDENCE_CUTOFF = "2026-10-22T14:02:00Z"
RUBRIC = "SE-SOURCE-DEPENDENCY-RUBRIC-v0.2"
REVIEWER_ID = "SE-PHASE-B-CODEX-REVIEW-20261025-01"

GAPS = {
    "OEG-CML-001": {
        "slug": "INDEPENDENT-VALIDATION",
        "claim_id": "CML-PDRE-001.INDEPENDENT_VALIDATION",
        "rule_id": "SE-SD-QR-OEG-CML-001-INDEPENDENT-VALIDATION-v0.2",
        "challenge_url": "https://structurevidence.org/gaps/OEG-CML-001/",
    },
    "OEG-CML-002": {
        "slug": "REPLICATION",
        "claim_id": "CML-PDRE-001.MULTI_ENTITY_REPLICATION",
        "rule_id": "SE-SD-QR-OEG-CML-002-REPLICATION-v0.2",
        "challenge_url": "https://structurevidence.org/gaps/OEG-CML-002/",
    },
}

SOURCE_SPECS: list[dict[str, Any]] = [
    {
        "key": "CHINDATA-533",
        "url": "https://www.chindatagroup.com/media/news/533.html",
        "title": "Chindata commercial-operation announcement for Sangyuan campus",
        "publisher_host": "www.chindatagroup.com",
        "packet_path": "e/L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001/index.json",
        "packet_sha256": "57e1ede12822f29e973c66d11db60a2e55a429cd4b7a4fea4bcc44d1c8aa1918",
        "captured_at": "2026-09-20T10:46:47Z",
        "last_checked_at": "2026-10-14T09:59:24Z",
        "originator_id": "ORIGINATOR-CHINDATA",
        "originator_label": "Chindata",
        "originator_role": "OPERATOR",
        "authored_by_evidence": [
            "The accepted atomic evidence record identifies Chindata as publisher and links the Chindata corporate-newsroom URL.",
            "The 2026-10-14 bounded review records the page as the same Chindata operator claim."
        ],
        "relationship_evidence": [
            "The source is the named operator's own publication about its Sangyuan Cloud Computing Campus."
        ],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "This is attributable operator evidence, not independent validation of the operator's own deployment claim.",
        "evidence_level": "E4",
        "evidence_facets": ["NAMED_OPERATOR", "NAMED_SITE", "MATERIALLY_COMPARABLE_ARCHITECTURE", "COMMISSIONED_OR_OPERATING", "EVENT_DATE", "RESPONSIBLE_ORGANIZATION"],
        "evidence_rationale": "The record attributes commercial operation of a materially relevant 10kV AC to SST to 800VDC system to one named operator and campus; it does not contain an attributable observation period, operating conditions, or methodology.",
        "search_run_id": "SE-800V-L1-REVIEW-20260920-01",
        "search_query": "800VDC field deployment",
        "search_inclusion": "The accepted named 800VDC field-deployment record and its October 14 availability check.",
        "search_exclusion": "No general market census and no inference beyond the single operator-reported campus.",
        "blocked_sources": ["No full raw external page capture is stored; the hash covers the bounded atomic evidence record."],
        "lineage_key": None,
    },
    {
        "key": "SIEMENS-REINHAUSEN-2026",
        "url": "https://press.siemens.com/global/en/pressrelease/siemens-and-reinhausen-develop-direct-current-power-solutions-ai-data-centers",
        "title": "Siemens and Reinhausen develop DC power solutions for AI data centers",
        "publisher_host": "press.siemens.com",
        "packet_path": "cases/800vdc/search-review-20261014-01.json",
        "packet_sha256": "8f7827b87ec928420c44e012492416e3f08940d1aeb106f9ce8210014a9a0fdc",
        "captured_at": "2026-10-14T09:59:24Z",
        "last_checked_at": "2026-10-14T09:59:24Z",
        "originator_id": "ORIGINATOR-SIEMENS-REINHAUSEN",
        "originator_label": "Siemens and Maschinenfabrik Reinhausen",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The bounded review identifies an official Siemens press record naming Siemens and Reinhausen."],
        "relationship_evidence": ["The companies developing and industrializing the equipment authored the source record."],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "The source is attributable supplier-authored development evidence and is not an independent operating observation.",
        "evidence_level": "E1",
        "evidence_facets": ["MATERIALLY_COMPARABLE_ARCHITECTURE", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The source describes technology development and industrialization, not a commissioned or operating deployment.",
        "search_run_id": "SE-800V-REVIEW-20261014-01",
        "search_query": "official Siemens Reinhausen 800VDC development deployment",
        "search_inclusion": "Official Siemens/Reinhausen development signals reviewed in the targeted October 14 refresh.",
        "search_exclusion": "No unnamed pipeline, plan, or industrialization statement is treated as field operation.",
        "blocked_sources": ["No source-specific raw file is stored; the hash covers the bounded three-source review packet."],
        "lineage_key": None,
    },
    {
        "key": "VERTIV-DCD-2026",
        "url": "https://www.vertiv.com/en-us/about/news-and-events/events/2026/dcd-power-innovation-day-2026/",
        "title": "Vertiv DCD Power Innovation Day 800VDC architecture topic",
        "publisher_host": "www.vertiv.com",
        "packet_path": "cases/800vdc/search-review-20261014-01.json",
        "packet_sha256": "8f7827b87ec928420c44e012492416e3f08940d1aeb106f9ce8210014a9a0fdc",
        "captured_at": "2026-10-14T09:59:24Z",
        "last_checked_at": "2026-10-14T09:59:24Z",
        "originator_id": "ORIGINATOR-VERTIV",
        "originator_label": "Vertiv",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The bounded review identifies the Vertiv corporate event page and its 800VDC architecture topic."],
        "relationship_evidence": ["The infrastructure supplier hosting the architecture event authored the page."],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "This supplier event page is an attributable architecture signal, not independent deployment evidence.",
        "evidence_level": "E0",
        "evidence_facets": ["MATERIALLY_COMPARABLE_ARCHITECTURE", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The page frames 800VDC as an architecture decision topic and supplies no named operating deployment.",
        "search_run_id": "SE-800V-REVIEW-20261014-01",
        "search_query": "official Vertiv 800VDC deployment event",
        "search_inclusion": "Official Vertiv architecture/deployment signals reviewed in the targeted October 14 refresh.",
        "search_exclusion": "Architecture discussion and future pilots are not counted as commissioning or field operation.",
        "blocked_sources": ["No source-specific raw file is stored; the hash covers the bounded three-source review packet."],
        "lineage_key": None,
    },
    {
        "key": "SOLAREDGE-ORIGIN-20261013",
        "url": "https://solaredge.gcs-web.com/news-releases/news-release-details/solaredge-showcases-mvac-800-vdc-ai-factory-power-technology",
        "title": "SolarEdge MVAC-to-800 VDC technology showcase announcement",
        "publisher_host": "solaredge.gcs-web.com",
        "packet_path": "cases/800vdc/events/solaredge-ocp-2026/snapshot-v1.json",
        "packet_sha256": "34fe5c45ce6eb0f9c29521c6ea7a596ce62a93af4607f56619749733385b0950",
        "captured_at": "2026-10-15T15:28:53Z",
        "last_checked_at": "2026-10-15T15:28:53Z",
        "originator_id": "ORIGINATOR-SOLAREDGE",
        "originator_label": "SolarEdge Technologies, Inc.",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The structured snapshot identifies SolarEdge's investor-relations newsroom as the origin and preserves bounded excerpts."],
        "relationship_evidence": ["SolarEdge authored the announcement about its own development hardware and engineering-lab work."],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "The origin record is supplier-authored; separate PDF and Business Wire URLs reproduce this same originating evidence.",
        "evidence_level": "E2",
        "evidence_facets": ["MATERIALLY_COMPARABLE_ARCHITECTURE", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The record supports engineering-lab work and a showcase model while stating that full-path validation was underway; it is not field deployment.",
        "search_run_id": "SE-800V-REVIEW-20261015-01",
        "search_query": "SolarEdge official MVAC 800 VDC OCP announcement",
        "search_inclusion": "SolarEdge official HTML, official PDF rendering, and explicitly linked Business Wire distribution copy.",
        "search_exclusion": "No broad market census, independent dataset, or named deployment search was performed.",
        "blocked_sources": ["The origin returned HTTP 403 to direct retrieval; only the bounded structured snapshot is stored."],
        "lineage_key": None,
    },
    {
        "key": "SOLAREDGE-PDF-20261013",
        "url": "https://solaredge.gcs-web.com/node/15356/pdf",
        "title": "Official PDF rendering of the SolarEdge OCP announcement",
        "publisher_host": "solaredge.gcs-web.com",
        "packet_path": "cases/800vdc/events/solaredge-ocp-2026/snapshot-v1.json",
        "packet_sha256": "34fe5c45ce6eb0f9c29521c6ea7a596ce62a93af4607f56619749733385b0950",
        "captured_at": "2026-10-15T15:28:53Z",
        "last_checked_at": "2026-10-15T15:28:53Z",
        "originator_id": "ORIGINATOR-SOLAREDGE",
        "originator_label": "SolarEdge Technologies, Inc.",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The October 15 source graph identifies this URL as the official PDF rendering of the SolarEdge origin release."],
        "relationship_evidence": ["The PDF is issued from SolarEdge's investor-relations host and reproduces the origin announcement."],
        "dependency_class": "DERIVED",
        "dependency_rationale": "This is another rendering of the SolarEdge announcement, not an additional observation or originator.",
        "evidence_level": "E2",
        "evidence_facets": ["MATERIALLY_COMPARABLE_ARCHITECTURE", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The PDF carries the same engineering-lab and incomplete-validation content as the origin record.",
        "search_run_id": "SE-800V-REVIEW-20261015-01",
        "search_query": "SolarEdge official MVAC 800 VDC OCP PDF",
        "search_inclusion": "The official PDF rendering explicitly linked from the SolarEdge source review.",
        "search_exclusion": "The rendering is not counted as independent corroboration.",
        "blocked_sources": ["No full raw PDF is stored; the bounded structured snapshot records the review."],
        "lineage_key": "SOLAREDGE-ORIGIN-20261013",
    },
    {
        "key": "SOLAREDGE-BUSINESSWIRE-20261013",
        "url": "https://www.businesswire.com/news/home/20261013444026/en/",
        "title": "Business Wire distribution copy of the SolarEdge announcement",
        "publisher_host": "www.businesswire.com",
        "packet_path": "cases/800vdc/events/solaredge-ocp-2026/snapshot-v1.json",
        "packet_sha256": "34fe5c45ce6eb0f9c29521c6ea7a596ce62a93af4607f56619749733385b0950",
        "captured_at": "2026-10-15T15:28:53Z",
        "last_checked_at": "2026-10-15T15:28:53Z",
        "originator_id": "ORIGINATOR-SOLAREDGE",
        "originator_label": "SolarEdge Technologies, Inc.",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The October 15 source graph identifies Business Wire as a distributed copy whose originator remains SolarEdge."],
        "relationship_evidence": ["Business Wire distributed SolarEdge's release; no separate observation or authorship is recorded."],
        "dependency_class": "DERIVED",
        "dependency_rationale": "A press-distribution host does not create a second evidence lineage; this row depends on the SolarEdge origin.",
        "evidence_level": "E2",
        "evidence_facets": ["MATERIALLY_COMPARABLE_ARCHITECTURE", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The copy carries the same engineering-lab and incomplete-validation claims as the origin release.",
        "search_run_id": "SE-800V-REVIEW-20261015-01",
        "search_query": "SolarEdge Business Wire 800 VDC distribution copy",
        "search_inclusion": "The explicitly linked Business Wire copy in the bounded SolarEdge source graph.",
        "search_exclusion": "Distribution copies are not counted as independent corroboration.",
        "blocked_sources": ["No full raw distribution copy is stored; the bounded structured snapshot records the review."],
        "lineage_key": "SOLAREDGE-ORIGIN-20261013",
    },
    {
        "key": "SUNGROW-1749",
        "url": "https://cn.sungrowpower.com/news/1749.html",
        "title": "Sungrow EnerNeo SST certification announcement",
        "publisher_host": "cn.sungrowpower.com",
        "packet_path": "cases/800vdc/events/sungrow-enerneo-certification-2026/snapshot-v1.json",
        "packet_sha256": "574c58de9d696546fed3f268b9fa02786e4a50ffe4e04616ddd0e06fdaf69f2a",
        "captured_at": "2026-10-17T14:04:05Z",
        "last_checked_at": "2026-10-17T14:04:05Z",
        "originator_id": "ORIGINATOR-SUNGROW",
        "originator_label": "Sungrow / Sungrow AIDC business",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The supplemental source record identifies Sungrow as originator and its corporate newsroom as publisher."],
        "relationship_evidence": ["The equipment supplier authored the certification publicity; the underlying issuer record was not authenticated in the bounded review."],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "The reviewed evidence is Sungrow's own announcement and cannot be treated as an independent TÜV record.",
        "evidence_level": "E2",
        "evidence_facets": ["RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The packet preserves an attributed system/component certification claim but no authenticated certificate, named operating customer, or field dataset.",
        "search_run_id": "SE-800V-REVIEW-20261017-SUPP-PR26-01",
        "search_query": "Sungrow EnerNeo SST certificate and issuer registry",
        "search_inclusion": "Official Sungrow article 1749 plus two bounded issuer/registry queries inherited from the reconciled review.",
        "search_exclusion": "No certificate authenticity, complete scope, customer operation, or reliability claim is inferred.",
        "blocked_sources": ["Fresh retrieval was blocked by network proxy HTTP 403; no matching certificate ID or issuer record was established."],
        "lineage_key": None,
    },
    {
        "key": "PI-IDEAL-SSCB-20261012",
        "url": "https://investors.power.com/news/news-details/2026/Power-Integrations-and-Ideal-Power-Collaborate-on-Efficient-Always-On-Solid-State-Circuit-Breakers-for-800-VDC-AI-Data-Centers/default.aspx",
        "title": "Power Integrations and Ideal Power 800 VDC SSCB collaboration",
        "publisher_host": "investors.power.com",
        "packet_path": "cases/800vdc/source-notes/power-integrations-ideal-power-sscb-20261012/snapshot-v1.json",
        "packet_sha256": "bc53bc00c4a66d044af3e69d461ba6c0d2164a8625939be56e90dc4f6b9c2ed9",
        "captured_at": "2026-10-21T14:08:00Z",
        "last_checked_at": "2026-10-21T14:08:00Z",
        "originator_id": "ORIGINATOR-POWER-INTEGRATIONS-IDEAL-POWER",
        "originator_label": "Power Integrations and Ideal Power",
        "originator_role": "SUPPLIER",
        "authored_by_evidence": ["The structured source note identifies both suppliers as originators and Power Integrations as publisher."],
        "relationship_evidence": ["The collaborating suppliers authored a release about their own working prototype."],
        "dependency_class": "ISSUER_AUTHORED",
        "dependency_rationale": "This is supplier-authored component evidence, not an independently observed system deployment.",
        "evidence_level": "E2",
        "evidence_facets": ["RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "A working solid-state circuit-breaker prototype supports component development only; the packet identifies no customer field deployment or replicated installation.",
        "search_run_id": "SE-SOURCE-CML-PDRE-001-20261012-SSCB",
        "search_query": "800 VDC AI data center solid-state circuit breaker collaboration",
        "search_inclusion": "The public supplier release and its bounded structured source snapshot.",
        "search_exclusion": "Prototype characteristics are not generalized to system commissioning, deployment, or adoption.",
        "blocked_sources": ["Only a structured factual snapshot is stored; no independent performance dataset is included."],
        "lineage_key": None,
    },
    {
        "key": "VANTAGE-HERON-20261021",
        "url": "https://vantage-dc.com/news/vantage-and-heron-power-electronics-announce-gigawatt-scale-800-vdc-agreement-to-accelerate-ai-infrastructure-delivery/",
        "title": "Vantage and Heron 800 VDC manufacturing-capacity agreement",
        "publisher_host": "vantage-dc.com",
        "packet_path": "cases/800vdc/events/vantage-heron-capacity-agreement-2026/snapshot-v1.json",
        "packet_sha256": "69b61c5ea87e5adf9ec8e272e8f07c47bceaccc159600be2854952096a73adda",
        "captured_at": "2026-10-22T14:02:00Z",
        "last_checked_at": "2026-10-22T14:02:00Z",
        "originator_id": "ORIGINATOR-VANTAGE-HERON",
        "originator_label": "Vantage Data Centers and Heron Power Electronics",
        "originator_role": "CUSTOMER",
        "authored_by_evidence": ["The event snapshot records a joint operator/supplier release published by Vantage Data Centers."],
        "relationship_evidence": ["The source discloses a commercial manufacturing-capacity agreement between prospective customer Vantage and supplier Heron."],
        "dependency_class": "PARTIALLY_DEPENDENT",
        "dependency_rationale": "The joint customer/supplier authorship is attributable but commercially dependent; it is not an independent operating observation.",
        "evidence_level": "E0",
        "evidence_facets": ["NAMED_OPERATOR", "RESPONSIBLE_ORGANIZATION", "EVENT_DATE"],
        "evidence_rationale": "The source records future capacity reservation and planned late-2027 production, not delivered equipment, a commissioned campus, or operating history.",
        "search_run_id": "SE-EVENT-CML-PDRE-001-20261021-VANTAGE-HERON",
        "search_query": "Vantage Heron 800 VDC agreement deployment commissioning",
        "search_inclusion": "The joint public announcement and bounded event snapshot.",
        "search_exclusion": "Reserved manufacturing capacity is not treated as produced output, commissioning, procurement completion, or field operation.",
        "blocked_sources": ["The separate factory announcement is summarized in the packet; no delivered-unit or commissioning record is present."],
        "lineage_key": None,
    },
]


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def row_id(gap_id: str, key: str) -> str:
    return f"SE-SOURCE-ROW-CML-PDRE-001-{GAPS[gap_id]['slug']}-{key}-V1"


def build_registry(rules_document: dict[str, Any]) -> dict[str, Any]:
    rules = load_rules(rules_document)
    rows: list[dict[str, Any]] = []
    for gap_id, gap in GAPS.items():
        for spec in SOURCE_SPECS:
            lineage = []
            if spec["lineage_key"]:
                lineage = [row_id(gap_id, spec["lineage_key"])]
            row: dict[str, Any] = {
                "schema_version": "se-source-dependency-row-v0.1",
                "source_row_id": row_id(gap_id, spec["key"]),
                "claim_id": gap["claim_id"],
                "gap_id": gap_id,
                "immutable_source": {
                    "url": spec["url"],
                    "title": spec["title"],
                    "publisher_host": spec["publisher_host"],
                    "capture": {
                        "capture_type": "STRUCTURED_SNAPSHOT",
                        "captured_at": spec["captured_at"],
                        "sha256": spec["packet_sha256"],
                        "failure_reason": "The repository preserves a bounded structured packet, not a complete raw copy of the external publication.",
                    },
                },
                "originator_id": spec["originator_id"],
                "originator_role": spec["originator_role"],
                "authored_by_evidence": spec["authored_by_evidence"],
                "originating_evidence_lineage": lineage,
                "author_issuer_relationship_evidence": spec["relationship_evidence"],
                "dependency_class": spec["dependency_class"],
                "dependency_rationale": spec["dependency_rationale"],
                "evidence_level": spec["evidence_level"],
                "evidence_facets": spec["evidence_facets"],
                "evidence_rationale": spec["evidence_rationale"],
                "qualification_rule_id": gap["rule_id"],
                "qualification_status": "NOT_ASSESSED",
                "qualification_reason": "Pending deterministic rule evaluation.",
                "source_access_status": "READ_PARTIAL",
                "search_run_id": spec["search_run_id"],
                "search_scope": {
                    "query": spec["search_query"],
                    "inclusion_scope": spec["search_inclusion"],
                    "exclusion_scope": spec["search_exclusion"],
                    "blocked_sources": spec["blocked_sources"],
                },
                "evidence_cutoff": EVIDENCE_CUTOFF,
                "last_checked_at": spec["last_checked_at"],
                "reviewed_at": REVIEWED_AT,
                "rubric_version": RUBRIC,
                "reviewers": [{
                    "reviewer_id": REVIEWER_ID,
                    "reviewed_at": REVIEWED_AT,
                    "dependency_class": spec["dependency_class"],
                    "evidence_level": spec["evidence_level"],
                    "qualification_status": "NOT_ASSESSED",
                    "note": "Phase B classification from the cited repository packet. No second reviewer record is claimed.",
                }],
                "reviewer_disagreement": {
                    "detected": False,
                    "fields": [],
                    "resolution_status": "NOT_APPLICABLE",
                    "resolution_note": "One actual Phase B reviewer record; independent second review remains pending.",
                },
                "supersession": {"predecessor_source_row_id": None, "reason": None},
                "event_timestamp": REVIEWED_AT,
                "record_hash": "",
            }
            status, reason = evaluate_qualification(row, rules[gap["rule_id"]])
            row["qualification_status"] = status
            row["qualification_reason"] = reason
            row["reviewers"][0]["qualification_status"] = status
            rows.append(seal_record(row))
    registry = {
        "schema_version": "se-source-dependency-registry-v0.1",
        "rubric_version": RUBRIC,
        "rows": rows,
    }
    validate_registry(registry, rules_document)
    return registry


def build_view(registry: dict[str, Any]) -> dict[str, Any]:
    rows_by_id = {row["source_row_id"]: row for row in registry["rows"]}
    metrics: dict[str, Any] = {}
    for gap_id, gap in GAPS.items():
        gap_registry = {
            "schema_version": registry["schema_version"],
            "rubric_version": registry["rubric_version"],
            "rows": [row for row in registry["rows"] if row["gap_id"] == gap_id],
        }
        metrics[gap_id] = deterministic_metrics(gap_registry, {
            "case_id": "CML-PDRE-001",
            "gap_id": gap_id,
            "claim_id": gap["claim_id"],
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "sample": "Nine actual URLs in the bounded repository source packets; not a market census.",
        })

    sources = []
    for spec in SOURCE_SPECS:
        gap_rows = {gap_id: rows_by_id[row_id(gap_id, spec["key"])] for gap_id in GAPS}
        sources.append({
            "source_key": spec["key"],
            "title": spec["title"],
            "url": spec["url"],
            "originator": spec["originator_label"],
            "originator_role": spec["originator_role"],
            "dependency_class": spec["dependency_class"],
            "dependency_rationale": spec["dependency_rationale"],
            "evidence_level": spec["evidence_level"],
            "evidence_rationale": spec["evidence_rationale"],
            "source_access_status": "READ_PARTIAL",
            "capture_packet_path": spec["packet_path"],
            "capture_sha256": spec["packet_sha256"],
            "search_run_id": spec["search_run_id"],
            "search_scope": gap_rows["OEG-CML-001"]["search_scope"],
            "evidence_cutoff": EVIDENCE_CUTOFF,
            "last_checked_at": spec["last_checked_at"],
            "rubric_version": RUBRIC,
            "gap_assessments": {
                gap_id: {
                    "source_row_id": row["source_row_id"],
                    "qualification_status": row["qualification_status"],
                    "qualification_reason": row["qualification_reason"],
                    "record_hash": row["record_hash"],
                }
                for gap_id, row in gap_rows.items()
            },
        })
    return {
        "schema_version": "se-source-dependency-view-v0.1",
        "project": "SE-DUAL-SITE-UPGRADE-002",
        "phase": "B",
        "case_id": "CML-PDRE-001",
        "canonical_case_url": "https://structurevidence.org/cases/800vdc/",
        "case_state": "HUMAN-REVIEWED SINGLE-INSTANCE EVIDENCE",
        "case_state_as_of": "2026-09-20T10:46:47Z",
        "case_state_changed": False,
        "reviewed_at": REVIEWED_AT,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "rubric_version": RUBRIC,
        "registry_path": "protocol/source-dependency/registry-v0.1.json",
        "active_rules_path": "protocol/source-dependency/qualification-rules-v0.2.json",
        "review_policy": {
            "actual_reviewer_records": 1,
            "second_review_status": "PENDING_HUMAN_REVIEW",
            "reviewer_id": REVIEWER_ID,
        },
        "rule_discrepancy": {
            "status": "RESOLVED_BY_APPEND_ONLY_RULE_VERSION",
            "preserved_rule_path": "protocol/source-dependency/qualification-rules-v0.1.json",
            "active_rule_path": "protocol/source-dependency/qualification-rules-v0.2.json",
            "reason": "The frozen OEG-CML-002 standard requires another operator or independently controlled site. v0.2 adds ADDITIONAL_ENTITY_OR_SITE so the accepted Chindata baseline cannot qualify as its own replication.",
        },
        "metrics": metrics,
        "sources": sources,
        "challenge_routes": {
            gap_id: {
                "url": gap["challenge_url"],
                "status": "OPERATIONAL_REFERENCE_ROUTE",
                "effect": "HUMAN_REVIEW_REQUIRED; NO_AUTOMATIC_STATE_CHANGE",
            }
            for gap_id, gap in GAPS.items()
        },
        "zero_interpretation": "Zero qualifying or independent rows means zero within these nine reviewed URLs and seven originating lineages, not proof that no evidence exists elsewhere.",
        "locales_preserved": ["en", "zh-CN", "es"],
    }


def render_source_dependency_page() -> bytes:
    fragment = (ROOT / "scripts/templates/source-dependency-section-v0.1.html").read_text(encoding="utf-8").rstrip()
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>800V DC Source Dependency View | StructEvidence</title><meta name="description" content="Auditable source lineage, dependency class, E0-E5 evidence level and gap qualification for the public 800V DC evidence packet."><link rel="canonical" href="https://structurevidence.org/cases/800vdc/source-dependency/"><link rel="alternate" type="application/json" href="https://structurevidence.org/cases/800vdc/source-dependency-v0.1.json"><meta property="og:title" content="800V DC Source Dependency View"><meta property="og:description" content="Nine reviewed URLs, seven evidence lineages, and explicit gap-specific qualification results."><meta property="og:type" content="article"><meta property="og:url" content="https://structurevidence.org/cases/800vdc/source-dependency/"><link rel="stylesheet" href="/assets/product.css?v=20261001-gravity"><link rel="stylesheet" href="/assets/source-dependency.css?v=20261025-phase-b"></head><body class="product-site"><a class="skip-link" href="#main">Skip to content</a>
<header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><div class="locale-switcher" aria-label="Language"><a href="/" lang="en">EN</a><a href="/zh-cn/" lang="zh-CN">简中</a><a href="/es/" lang="es">ES</a></div><button class="product-nav-toggle" type="button" aria-expanded="false" aria-controls="product-links" data-product-nav-toggle>Menu</button><div class="product-links" id="product-links"><a aria-current="page" href="/cases/800vdc/">800V DC case</a><a href="/gaps/">Open Evidence Gaps</a><a href="/method.html">Method</a></div></nav></header>
<main class="product-main" id="main"><nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">StructEvidence</a><span>›</span><a href="/cases/">Cases</a><span>›</span><a href="/cases/800vdc/">800V DC</a><span>›</span><span aria-current="page">Source dependency</span></nav><section class="page-hero case-hero" aria-labelledby="page-title"><p class="eyebrow">CML-PDRE-001 · append-only Phase B review</p><h1 id="page-title">800V DC Source Dependency View</h1><p class="lead">An independently checkable ledger of who originated each reviewed record, what evidence level it reaches, and whether it qualifies the two open evidence gaps.</p><div class="actions"><a class="button" href="/cases/800vdc/">Return to preserved case record</a><a class="button secondary" href="/cases/800vdc/source-dependency-v0.1.json">Machine-readable view</a><a class="button secondary" href="/gaps/OEG-CML-001/">Independent-validation gap</a><a class="button secondary" href="/gaps/OEG-CML-002/">Replication gap</a></div></section>
{fragment}
</main><footer class="product-footer"><div class="product-wrap footer-grid"><strong>StructEvidence</strong><a href="/cases/800vdc/">Preserved case record</a><a href="/gaps/">Open Evidence Gaps</a><a href="/method.html">Method</a><a href="/privacy.html">Privacy</a><span>Source lineage is separate from evidence truth and case state.</span></div></footer><script src="/assets/product.js"></script></body></html>
'''
    return page.encode("utf-8")


def build_hash_report(registry_bytes: bytes, view_bytes: bytes, page_bytes: bytes, css_bytes: bytes) -> dict[str, Any]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    current = {path: sha256_file(path) for path in baseline["protected_paths"]}
    changed = [path for path, digest in current.items() if digest != baseline["protected_paths"][path]]
    packet_hashes = {spec["packet_path"]: sha256_file(spec["packet_path"]) for spec in SOURCE_SPECS}
    expected_packet_hashes = {spec["packet_path"]: spec["packet_sha256"] for spec in SOURCE_SPECS}
    packet_mismatches = [path for path, digest in packet_hashes.items() if digest != expected_packet_hashes[path]]
    return {
        "project": "SE-DUAL-SITE-UPGRADE-002",
        "phase": "B",
        "baseline_main_sha": "f89f5dbba30c3f504833418d643786680d5769ca",
        "generated_at": REVIEWED_AT,
        "protected_original_manifest": str(BASELINE_PATH.relative_to(ROOT)),
        "protected_originals_changed": changed,
        "source_packet_sha256": packet_hashes,
        "source_packet_hash_mismatches": packet_mismatches,
        "generated_artifact_sha256": {
            "protocol/source-dependency/registry-v0.1.json": sha256_bytes(registry_bytes),
            "cases/800vdc/source-dependency-v0.1.json": sha256_bytes(view_bytes),
            "cases/800vdc/source-dependency/index.html": sha256_bytes(page_bytes),
            "assets/source-dependency.css": sha256_bytes(css_bytes),
            "protocol/source-dependency/qualification-rules-v0.1.json": sha256_file("protocol/source-dependency/qualification-rules-v0.1.json"),
            "protocol/source-dependency/qualification-rules-v0.2.json": sha256_file("protocol/source-dependency/qualification-rules-v0.2.json"),
        },
    }


def outputs() -> dict[str, bytes]:
    rules_document = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    registry = build_registry(rules_document)
    view = build_view(registry)
    registry_bytes = json_bytes(registry)
    view_bytes = json_bytes(view)
    page_bytes = render_source_dependency_page()
    css_bytes = (ROOT / "assets/source-dependency.css").read_bytes()
    hashes = build_hash_report(registry_bytes, view_bytes, page_bytes, css_bytes)
    return {
        "protocol/source-dependency/registry-v0.1.json": registry_bytes,
        "docs/protocol/source-dependency/registry-v0.1.json": registry_bytes,
        "cases/800vdc/source-dependency-v0.1.json": view_bytes,
        "docs/cases/800vdc/source-dependency-v0.1.json": view_bytes,
        "cases/800vdc/source-dependency/index.html": page_bytes,
        "docs/cases/800vdc/source-dependency/index.html": page_bytes,
        "docs/assets/source-dependency.css": css_bytes,
        "docs/protocol/source-dependency/qualification-rules-v0.1.json": (ROOT / "protocol/source-dependency/qualification-rules-v0.1.json").read_bytes(),
        "docs/protocol/source-dependency/qualification-rules-v0.2.json": RULES_PATH.read_bytes(),
        "docs/protocol/source-dependency/schema-v0.1.json": (ROOT / "protocol/source-dependency/schema-v0.1.json").read_bytes(),
        "docs/implementation/SE-DUAL-SITE-002-PHASE-B-HASHES.json": json_bytes(hashes),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write deterministic artifacts")
    args = parser.parse_args()
    expected = outputs()
    if args.write:
        for relative, content in expected.items():
            path = ROOT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        print(f"SOURCE_DEPENDENCY_BUILD = PASS ({len(expected)} artifacts written)")
        return 0
    mismatches = []
    for relative, content in expected.items():
        path = ROOT / relative
        if not path.exists() or path.read_bytes() != content:
            mismatches.append(relative)
    for relative in mismatches:
        print(f"DRIFT = {relative}")
    print("SOURCE_DEPENDENCY_BUILD = " + ("PASS" if not mismatches else "FAIL"))
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
