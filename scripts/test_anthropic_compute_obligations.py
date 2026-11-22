#!/usr/bin/env python3
"""Publication-boundary tests for the minimal Anthropic public integration."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases/anthropic-compute-obligations"
CASE_ID = "SE-AI-COMPUTE-OBLIGATIONS-001"
BASE_SHA = "64bab7e87d51b1a96134a1a0cd74c0f6b1b5e554"
SOURCE_SHA256 = "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def jsonl(relative: str):
    return [json.loads(line) for line in (ROOT / relative).read_text(encoding="utf-8").splitlines() if line]


def builder():
    path = ROOT / "scripts/build_anthropic_compute_obligations.py"
    spec = importlib.util.spec_from_file_location("aico_public_builder", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AnchorParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.canonical = None
        self.robots = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = values.get("href")
        if tag == "meta" and values.get("name") == "robots":
            self.robots = values.get("content")


class AnthropicPublicReleaseTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.snapshot = load("cases/anthropic-compute-obligations/index.json")
        cls.claims = jsonl("cases/anthropic-compute-obligations/claims-v0.2.jsonl")
        cls.registry = load("cases/anthropic-compute-obligations/source-registry-public-v0.2.json")
        cls.html = (CASE / "index.html").read_text(encoding="utf-8")

    def test_01_reviewed_hashes_or_authorized_corrections_and_mirrors(self):
        builder().verify_reviewed_files()

    def test_02_claim_roles_and_count(self):
        self.assertEqual(len(self.claims), 15)
        counts = {}
        for row in self.claims:
            counts[row["claim_role"]] = counts.get(row["claim_role"], 0) + 1
        self.assertEqual(counts, {"ISSUER_DISCLOSURE": 9, "SE_DERIVED_CALCULATION": 1, "REJECTED_OR_UNSUPPORTED_INFERENCE": 5})

    def test_03_source_attribution_and_unaudited_boundary(self):
        self.assertEqual(self.snapshot["source_dependency_policy"], "ISSUER_STATEMENT_SEC_HOSTED_NOT_INDEPENDENTLY_VALIDATED")
        source = self.registry["sources"][0]
        self.assertEqual(source["assurance"], "ISSUER_ATTRIBUTED_UNAUDITED_FINANCIAL_DISCLOSURE")
        self.assertEqual(source["source_authority"], "ISSUER_STATEMENT_SEC_HOSTED_NOT_INDEPENDENTLY_VALIDATED")
        self.assertEqual(source["raw_sha256"], SOURCE_SHA256)
        self.assertIn("unaudited", self.html.lower())

    def test_04_temporal_semantics(self):
        self.assertEqual(self.snapshot["prospectus_dated_at"], "2026-11-18")
        self.assertEqual(self.snapshot["sec_filed_at"], "2026-11-19")
        self.assertIsNone(self.snapshot["structevidence_publication_date"])
        metadata = load("cases/anthropic-compute-obligations/structured-metadata-v0.2.json")
        self.assertIsNone(metadata["datePublished"])
        self.assertEqual(metadata["isBasedOn"]["datePublished"], "2026-11-19")

    def test_04b_legacy_source_date_is_explicitly_aliased(self):
        policy = self.snapshot["client_source_date_policy"]
        self.assertEqual(policy["legacy_field_alias"], "prospectus_dated_at")
        self.assertEqual(policy["confirmed_public_availability_date"], "2026-11-19")
        self.assertTrue(policy["must_not_infer_public_availability_from_legacy_field"])
        for claim in self.claims:
            self.assertEqual(claim["source_document_published_at"], "2026-11-18")
            self.assertEqual(claim["confirmed_sec_public_filing_date"], "2026-11-19")
            self.assertEqual(claim["source_document_published_at_legacy_semantics"], "PROSPECTUS_DATED_AT_NOT_CONFIRMED_PUBLIC_AVAILABILITY")

    def test_05_financial_boundaries(self):
        amounts = {row["amount_usd_billions"] for row in self.registry["sources"][0]["financial_amount_boundaries"]}
        self.assertEqual(amounts, {"319.993", "900.9", "451.6", "70.7"})

    def test_06_html_canonical_indexing_and_anchors(self):
        parser = AnchorParser()
        parser.feed(self.html)
        self.assertEqual(parser.canonical, "https://structurevidence.org/cases/anthropic-compute-obligations/")
        self.assertEqual(parser.robots, "index,follow,max-image-preview:large")
        self.assertTrue({row["claim_id"] for row in self.claims} <= parser.ids)

    def test_07_agent_corpus_separates_claim_and_source_urls(self):
        corpus = jsonl("agent-discovery/corpora/se-ai-compute-obligations-001-v0.2.jsonl")
        self.assertEqual(len(corpus), 15)
        for row in corpus:
            self.assertNotEqual(row["citation"]["claim_url"], row["citation"]["source_url"])
            self.assertEqual(row["citation"]["source_sha256"], SOURCE_SHA256)

    def test_08_global_discovery_uses_versioned_adapter(self):
        claims = load("claims/index.json")
        discovery = load(".well-known/structurevidence.json")
        self.assertEqual(claims["versioned_adapters"][0]["case_id"], CASE_ID)
        self.assertEqual(discovery["versioned_case_adapters"][0], claims["versioned_adapters"][0])
        self.assertIsNone(discovery["versioned_case_adapters"][0]["structevidence_date_published"])

    def test_09_case_index_review_status_and_sitemap(self):
        page = (ROOT / "cases/index.html").read_text(encoding="utf-8")
        self.assertIn(CASE_ID, page)
        self.assertIn('meta name="description" content="Seven on-site evidence trackers', page)
        self.assertNotIn('meta name="description" content="Six on-site evidence trackers', page)
        status = next(row for row in load("cases/review-status.json")["cases"] if row["case_id"] == CASE_ID)
        self.assertIsNone(status["last_reviewed_at"])
        self.assertEqual(status["period"]["status"], "NOT_YET_REVIEWED")
        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for url in builder().SITEMAP_URLS:
            self.assertIn(f"<loc>{url}</loc>", sitemap)

    def test_10_no_private_source_or_review_material(self):
        tracked = set(subprocess.check_output(["git", "diff", "--name-only", BASE_SHA], cwd=ROOT, text=True).splitlines())
        forbidden = ("source-captures/", "/review/", "FINAL_RELEASE_TEST_LOGS", ".env", "credentials")
        self.assertFalse([path for path in tracked if any(token in path for token in forbidden)])
        self.assertFalse((CASE / "source-captures").exists())
        self.assertFalse((CASE / "review").exists())

    def test_11_existing_public_case_histories_unchanged(self):
        protected = ["cases/800vdc", "cases/sodium-ion-bess", "cases/nsq-nsclc-china", "cases/irkutsk-lab-worker-death", "cases/iren-ai-cloud-transition", "cases/binance-security-2026"]
        proc = subprocess.run(["git", "diff", "--exit-code", BASE_SHA, "--", *protected], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_12_diff_is_minimal_and_scoped(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", BASE_SHA], cwd=ROOT, text=True).splitlines()
        allowed = (
            ".well-known/structurevidence.json", "agent-discovery/", "cases/anthropic-compute-obligations/",
            "cases/index.html", "cases/review-status.json", "claims/index.json", "docs/", "scripts/", "sitemap.xml",
        )
        self.assertTrue(changed)
        self.assertFalse([path for path in changed if not any(path == prefix or path.startswith(prefix) for prefix in allowed)])

    def test_13_deterministic_builder_check(self):
        builder().check_outputs()

    def test_14_activation_projection_and_receipt_are_unpopulated(self):
        activation = load("cases/anthropic-compute-obligations/activation-projection-v0.2.json")
        receipt = load("cases/anthropic-compute-obligations/publication-receipt-template-v0.2.json")
        self.assertEqual(activation["status"], "GATED_ACTIVATION_PROJECTION_NOT_APPLIED")
        self.assertIsNone(activation["proposed_append_only_event"]["publication_event_at"])
        self.assertFalse(activation["merge_authorized"])
        self.assertFalse(activation["deployment_authorized"])
        self.assertEqual(receipt["status"], "TEMPLATE_NOT_A_PUBLICATION_RECEIPT")
        self.assertIsNone(receipt["publication_event_at"])
        self.assertTrue(receipt["append_only"])
        self.assertFalse(receipt["prepublication_history_rewritten"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
