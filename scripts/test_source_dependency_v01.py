#!/usr/bin/env python3
"""Regression and abuse-case tests for source dependency v0.1."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from source_dependency_v01 import (
    REGISTRY_SCHEMA_VERSION,
    SourceDependencyError,
    assert_append_only,
    deterministic_metrics,
    evaluate_qualification,
    load_rules,
    migrate_registry,
    seal_record,
    validate_registry,
)


ROOT = Path(__file__).resolve().parents[1]
RULES_DOCUMENT = json.loads(
    (ROOT / "protocol/source-dependency/qualification-rules-v0.1.json").read_text(encoding="utf-8")
)
RULES = load_rules(RULES_DOCUMENT)
RULE_ID = "SE-SD-QR-OEG-CML-002-REPLICATION-v0.1"


def registry(*rows):
    return {
        "schema_version": REGISTRY_SCHEMA_VERSION,
        "rubric_version": "SE-SOURCE-DEPENDENCY-RUBRIC-v0.1",
        "rows": list(rows),
    }


def row(
    suffix: str,
    *,
    url: str | None = None,
    originator: str = "ORIGINATOR-OPERATOR-A",
    role: str = "OPERATOR",
    dependency: str = "ISSUER_AUTHORED",
    level: str = "E4",
    status: str = "QUALIFIED",
    access: str = "READ_FULL",
    lineage: list[str] | None = None,
    reviewers: list[dict] | None = None,
    disagreement: dict | None = None,
    facets: list[str] | None = None,
):
    row_id = f"SE-SOURCE-ROW-{suffix}"
    reviewed_at = "2026-10-25T08:00:00Z"
    result = {
        "schema_version": "se-source-dependency-row-v0.1",
        "source_row_id": row_id,
        "claim_id": "CML-PDRE-001.MULTI_ENTITY_REPLICATION",
        "gap_id": "OEG-CML-002",
        "immutable_source": {
            "url": url or f"https://example.invalid/{suffix.lower()}",
            "title": f"Attributable source {suffix}",
            "publisher_host": "example.invalid",
            "capture": {
                "capture_type": "STRUCTURED_SNAPSHOT" if access not in {"UNAVAILABLE", "CORRUPT", "UNKNOWN"} else "REFERENCE_ONLY",
                "captured_at": reviewed_at if access not in {"UNAVAILABLE", "CORRUPT", "UNKNOWN"} else None,
                "sha256": "a" * 64 if access not in {"UNAVAILABLE", "CORRUPT", "UNKNOWN"} else None,
                "failure_reason": None if access not in {"UNAVAILABLE", "CORRUPT", "UNKNOWN"} else "The external document could not be reviewed.",
            },
        },
        "originator_id": originator,
        "originator_role": role,
        "authored_by_evidence": ["Public byline and issuing organization metadata."],
        "originating_evidence_lineage": lineage or [],
        "author_issuer_relationship_evidence": ["The source identifies the originator's role."],
        "dependency_class": dependency,
        "dependency_rationale": "Authorship and evidence lineage were classified only from attributable metadata.",
        "evidence_level": level,
        "evidence_facets": facets if facets is not None else [
            "NAMED_OPERATOR",
            "NAMED_SITE",
            "MATERIALLY_COMPARABLE_ARCHITECTURE",
            "COMMISSIONED_OR_OPERATING",
            "EVENT_DATE",
        ],
        "evidence_rationale": "The record is scoped to the declared evidence level and does not establish truth by itself.",
        "qualification_rule_id": RULE_ID,
        "qualification_status": status,
        "qualification_reason": "The declared status follows the explicit gap rule without changing the case state.",
        "source_access_status": access,
        "search_run_id": "SE-SEARCH-RUN-TEST-001",
        "search_scope": {
            "query": "bounded 800 VDC field deployment query",
            "inclusion_scope": "Attributable public records in the declared sample.",
            "exclusion_scope": "No general market census.",
            "blocked_sources": [],
        },
        "evidence_cutoff": "2026-10-25T00:00:00Z",
        "last_checked_at": reviewed_at,
        "reviewed_at": reviewed_at,
        "rubric_version": "SE-SOURCE-DEPENDENCY-RUBRIC-v0.1",
        "reviewers": reviewers or [
            {
                "reviewer_id": "REVIEWER-A",
                "reviewed_at": reviewed_at,
                "dependency_class": dependency,
                "evidence_level": level,
                "qualification_status": status,
                "note": "Bounded test review.",
            }
        ],
        "reviewer_disagreement": disagreement or {
            "detected": False,
            "fields": [],
            "resolution_status": "NOT_APPLICABLE",
            "resolution_note": None,
        },
        "supersession": {"predecessor_source_row_id": None, "reason": None},
        "event_timestamp": reviewed_at,
        "record_hash": "",
    }
    return seal_record(result)


class SourceDependencyV01Test(unittest.TestCase):
    def assert_invalid(self, document, needle):
        with self.assertRaisesRegex(SourceDependencyError, needle):
            validate_registry(document, RULES_DOCUMENT)

    def test_issuer_authored_document_on_third_party_host_is_not_independent(self):
        item = row("ISSUER-HOSTED", url="https://press-host.invalid/operator-release")
        item["immutable_source"]["publisher_host"] = "press-host.invalid"
        item = seal_record(item)
        validate_registry(registry(item), RULES_DOCUMENT)
        metrics = deterministic_metrics(registry(item), {"gap_id": "OEG-CML-002", "evidence_cutoff": "2026-10-25T00:00:00Z"})
        self.assertEqual(metrics["reviewed_urls"]["value"], 1)
        self.assertEqual(metrics["distinct_originators"]["value"], 1)
        self.assertEqual(metrics["independent_originators"]["value"], 0)

    def test_derived_digest_shares_originating_lineage(self):
        origin = row("ORIGIN")
        digest = row(
            "DIGEST",
            originator="ORIGINATOR-MEDIA-A",
            role="MEDIA",
            dependency="DERIVED",
            level="E3",
            status="NOT_QUALIFIED",
            lineage=[origin["source_row_id"]],
            facets=[],
        )
        validate_registry(registry(origin, digest), RULES_DOCUMENT)
        self.assertEqual(digest["originating_evidence_lineage"], [origin["source_row_id"]])

    def test_supplier_customer_coauthored_record_is_partially_dependent(self):
        item = row("COAUTHORED", dependency="PARTIALLY_DEPENDENT", originator="ORIGINATOR-SUPPLIER-CUSTOMER", role="CUSTOMER")
        item["authored_by_evidence"] = ["Named supplier and customer co-authors are present."]
        item["author_issuer_relationship_evidence"] = ["The paper discloses the commercial collaboration."]
        item = seal_record(item)
        validate_registry(registry(item), RULES_DOCUMENT)
        metrics = deterministic_metrics(registry(item), {"gap_id": "OEG-CML-002"})
        self.assertEqual(metrics["partially_dependent_rows"]["source_row_ids"], [item["source_row_id"]])

    def test_paywalled_abstract_keeps_dependency_unknown(self):
        item = row("PAYWALL", dependency="UNKNOWN", level="E2", status="NOT_QUALIFIED", access="PAYWALLED", facets=[])
        validate_registry(registry(item), RULES_DOCUMENT)
        metrics = deterministic_metrics(registry(item), {"gap_id": "OEG-CML-002"})
        self.assertEqual(metrics["unknown_dependency_rows"]["value"], 1)

    def test_independent_e2_lab_study_does_not_prove_deployment(self):
        item = row("LAB", dependency="INDEPENDENT", originator="ORIGINATOR-LAB", role="RESEARCHER", level="E2", status="NOT_QUALIFIED", facets=["METHODOLOGY"])
        self.assertEqual(evaluate_qualification(item, RULES[RULE_ID])[0], "NOT_QUALIFIED")
        validate_registry(registry(item), RULES_DOCUMENT)

    def test_e4_operator_owned_record_may_qualify_under_explicit_rule(self):
        item = row("OPERATOR-E4")
        self.assertEqual(evaluate_qualification(item, RULES[RULE_ID])[0], "QUALIFIED")
        validate_registry(registry(item), RULES_DOCUMENT)

    def test_missing_provenance_is_rejected(self):
        item = row("MISSING-PROVENANCE")
        item["authored_by_evidence"] = []
        item = seal_record(item)
        self.assert_invalid(registry(item), "authored_by_evidence")

    def test_declared_qualification_must_match_the_rule(self):
        item = row("FALSE-QUALIFICATION", level="E2", status="QUALIFIED", facets=[])
        self.assert_invalid(registry(item), "expected NOT_QUALIFIED")

    def test_reviewer_conflict_must_be_explicit(self):
        reviews = [
            {"reviewer_id": "REVIEWER-A", "reviewed_at": "2026-10-25T08:00:00Z", "dependency_class": "ISSUER_AUTHORED", "evidence_level": "E4", "qualification_status": "QUALIFIED", "note": "First review."},
            {"reviewer_id": "REVIEWER-B", "reviewed_at": "2026-10-25T08:01:00Z", "dependency_class": "PARTIALLY_DEPENDENT", "evidence_level": "E4", "qualification_status": "QUALIFIED", "note": "Second review."},
        ]
        hidden = row("HIDDEN-CONFLICT", reviewers=reviews)
        self.assert_invalid(registry(hidden), "disagreement")
        exposed = row(
            "EXPOSED-CONFLICT",
            reviewers=reviews,
            disagreement={"detected": True, "fields": ["dependency_class"], "resolution_status": "UNRESOLVED", "resolution_note": "Human adjudication remains open."},
        )
        validate_registry(registry(exposed), RULES_DOCUMENT)

    def test_incorrect_or_self_referential_lineage_is_rejected(self):
        missing = row("BAD-LINEAGE", dependency="DERIVED", level="E3", status="NOT_QUALIFIED", lineage=["SE-SOURCE-ROW-NOT-PRESENT"], facets=[])
        self.assert_invalid(registry(missing), "missing source rows")
        self_ref = row("SELF-LINEAGE", dependency="DERIVED", level="E3", status="NOT_QUALIFIED", lineage=["SE-SOURCE-ROW-SELF-LINEAGE"], facets=[])
        self.assert_invalid(registry(self_ref), "depend on itself")
        first = row("CYCLE-A", dependency="DERIVED", level="E3", status="NOT_QUALIFIED", lineage=["SE-SOURCE-ROW-CYCLE-B"], facets=[])
        second = row("CYCLE-B", dependency="DERIVED", level="E3", status="NOT_QUALIFIED", lineage=["SE-SOURCE-ROW-CYCLE-A"], facets=[])
        self.assert_invalid(registry(first, second), "cycle")

    def test_correction_is_append_only_and_prior_row_is_immutable(self):
        original = row("CORRECTION-001")
        previous = registry(original)
        mutated = copy.deepcopy(original)
        mutated["dependency_rationale"] = "Rewritten in place."
        mutated = seal_record(mutated)
        with self.assertRaisesRegex(SourceDependencyError, "changed"):
            assert_append_only(previous, registry(mutated))
        successor = row("CORRECTION-002")
        successor["supersession"] = {"predecessor_source_row_id": original["source_row_id"], "reason": "Append-only classification correction."}
        successor = seal_record(successor)
        current = registry(original, successor)
        validate_registry(current, RULES_DOCUMENT)
        assert_append_only(previous, current)

    def test_registry_migration_is_idempotent_and_never_reclassifies(self):
        legacy_container = {"rows": []}
        once = migrate_registry(legacy_container)
        twice = migrate_registry(once)
        self.assertEqual(once, twice)
        self.assertEqual(once["rows"], [])
        self.assertNotIn("schema_version", legacy_container)

    def test_corrupt_or_unavailable_external_document_cannot_qualify(self):
        for access in ("CORRUPT", "UNAVAILABLE"):
            with self.subTest(access=access):
                item = row(access, access=access, status="INSUFFICIENT_DATA")
                self.assertEqual(evaluate_qualification(item, RULES[RULE_ID])[0], "INSUFFICIENT_DATA")
                validate_registry(registry(item), RULES_DOCUMENT)

    def test_path_sensitive_injection_and_xss_are_rejected(self):
        bad_urls = [
            "javascript:alert(1)",
            "https://example.invalid/%2e%2e/admin",
            "https://example.invalid/ok?q=%3Cscript%3Ealert(1)%3C/script%3E",
            "https://example.invalid/a\\..\\admin",
        ]
        for index, url in enumerate(bad_urls):
            with self.subTest(url=url):
                item = row(f"BAD-URL-{index}", url=url)
                self.assert_invalid(registry(item), "URL|unsafe")
        item = row("BAD-TITLE")
        item["immutable_source"]["title"] = "Evidence <img src=x onerror=alert(1)>"
        item = seal_record(item)
        self.assert_invalid(registry(item), "unsafe markup")

    def test_metrics_deduplicate_urls_and_originators_and_expose_scope(self):
        first = row("METRIC-1", url="https://EXAMPLE.invalid/source#first")
        second = row("METRIC-2", url="https://example.invalid/source#second")
        third = row("METRIC-3", originator="ORIGINATOR-INDEPENDENT", role="RESEARCHER", dependency="INDEPENDENT")
        scope = {"gap_id": "OEG-CML-002", "sample": "three reviewed rows"}
        result = deterministic_metrics(registry(first, second, third), scope)
        self.assertEqual(result["reviewed_urls"]["value"], 2)
        self.assertEqual(result["distinct_evidence_lineages"]["value"], 3)
        self.assertEqual(result["distinct_originators"]["value"], 2)
        self.assertEqual(result["independent_originators"]["value"], 1)
        self.assertEqual(result["qualified_evidence_rows"]["value"], 3)
        self.assertEqual(result["reviewed_urls"]["scope"], scope)
        self.assertEqual(sorted(result["reviewed_urls"]["source_row_ids"]), sorted([first["source_row_id"], second["source_row_id"], third["source_row_id"]]))

    def test_no_denominator_is_insufficient_data_not_zero_percent(self):
        result = deterministic_metrics(registry(), {"gap_id": "OEG-CML-002"})
        self.assertEqual(result["classification_coverage"]["status"], "INSUFFICIENT_DATA")
        self.assertIsNone(result["classification_coverage"]["percentage"])
        self.assertEqual(result["distinct_evidence_lineages"]["value"], 0)


if __name__ == "__main__":
    unittest.main()
