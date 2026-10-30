#!/usr/bin/env python3
"""Safety, provenance and publication-boundary tests for SE-BINANCE-SECURITY-001."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "binance-security-2026"
BASELINE_SHA = "ea1dff9e53725e49d64d595d362b3baa63fe7047"
APPROVED_RESEARCH_HEAD = "07c8c26562f4ea96d20519181d60d02fa8ecc390"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def load(name: str):
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class DraftHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.robots = None
        self.lang = None
        self.canonical = None
        self.og = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if tag == "meta" and attrs.get("name") == "robots":
            self.robots = attrs.get("content")
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "meta" and attrs.get("property", "").startswith("og:"):
            self.og[attrs["property"]] = attrs.get("content")


class BinanceSecurityCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load("baseline-v0.1.json")
        cls.control = load("publication-control.json")
        cls.registry = load("source-registry-v0.1.json")
        cls.claims = load("claims-v0.1.json")
        cls.chain = load("onchain-observations-v0.1.json")
        cls.transitions = load("state-transitions-v0.1.json")
        cls.review = load("source-review-20261030-02.json")
        cls.approval = load("publication-approval-v0.1.json")
        cls.index = load("index.json")
        cls.draft_page = (CASE / "index.draft.html").read_text(encoding="utf-8")
        cls.page = (CASE / "index.html").read_text(encoding="utf-8")

    def test_baseline_was_discovered_and_protected_registry_is_unchanged(self):
        self.assertEqual(self.baseline["baseline_main_sha"], BASELINE_SHA)
        path = ROOT / self.baseline["protected_baseline_registry"]
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), self.baseline["protected_baseline_registry_sha256"])
        protected = json.loads(path.read_text(encoding="utf-8"))["files"]
        self.assertEqual(len(protected), self.baseline["protected_file_count"])
        for relative, expected in protected.items():
            self.assertEqual(hashlib.sha256((ROOT / relative).read_bytes()).hexdigest(), expected, relative)

    def test_source_registry_is_complete_and_hashes_are_well_formed(self):
        sources = self.registry["sources"]
        self.assertEqual(self.registry["source_count"], 8)
        self.assertEqual(len(sources), 8)
        self.assertEqual(len({s["source_id"] for s in sources}), 8)
        self.assertEqual(self.registry["independent_originator_count"], 3)
        for source in sources:
            self.assertTrue(source["canonical_url"].startswith("https://"))
            self.assertRegex(source["content_sha256"], SHA256)
            parse_time(source["observed_at"])
            if source["published_at"]:
                parse_time(source["published_at"])
            self.assertTrue(source["dependency_class"])
            self.assertTrue(source["issuer_role"])
            self.assertTrue(source["public_safe"])

    def test_normalized_capture_hashes_reproduce(self):
        for source in self.registry["sources"]:
            if source["hash_scope"] != "NORMALIZED_PUBLIC_RENDER_CAPTURE":
                continue
            path = ROOT / source["capture_path"]
            self.assertTrue(path.is_file())
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), source["content_sha256"])

    def test_fresh_source_review_is_append_only_and_retains_open_claims(self):
        self.assertTrue(self.review["append_only"])
        self.assertFalse(self.review["prior_records_modified"])
        self.assertFalse(self.review["material_change_detected"])
        self.assertEqual(self.review["supported_claim_count"], 4)
        self.assertEqual(self.review["open_claim_count"], 6)
        self.assertEqual(len(self.review["observations"]), 8)
        self.assertEqual(self.review["evidence_cutoff_utc"], "2026-10-30T08:18:22Z")
        for observation in self.review["observations"]:
            parse_time(observation["observed_at_utc"])
            self.assertRegex(observation["content_sha256"], SHA256)
            if observation.get("capture_path"):
                path = ROOT / observation["capture_path"]
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), observation["content_sha256"])

    def test_v0_1_research_records_match_approved_head(self):
        immutable = [
            "HUMAN_REVIEW_PACK.md", "README.md", "SOCIAL_CANDIDATES.md", "STORYBOARD.md",
            "baseline-v0.1.json", "claims-v0.1.json", "index.draft.html",
            "onchain-observations-v0.1.json", "publication-control.json",
            "source-captures/BSEC-S001.normalized.txt", "source-captures/BSEC-S005.normalized.txt",
            "source-registry-v0.1.json", "state-transitions-v0.1.json",
        ]
        for relative in immutable:
            approved = subprocess.check_output(
                ["git", "show", f"{APPROVED_RESEARCH_HEAD}:cases/binance-security-2026/{relative}"], cwd=ROOT
            )
            self.assertEqual((CASE / relative).read_bytes(), approved, relative)

    def test_claims_are_atomic_attributed_and_bounded(self):
        claims = self.claims["claims"]
        self.assertEqual(len(claims), 10)
        self.assertEqual(self.claims["supported_claim_count"], 4)
        self.assertEqual(self.claims["open_claim_count"], 6)
        self.assertEqual(len({row["claim_id"] for row in claims}), 10)
        source_ids = {s["source_id"] for s in self.registry["sources"]}
        supported = 0
        opened = 0
        for row in claims:
            self.assertRegex(row["claim_id"], r"^BSEC-R\d{3}$")
            self.assertTrue(row["speaker_attribution"])
            self.assertTrue(row["boundary"])
            self.assertTrue(row["closure_test"])
            self.assertTrue(set(row["source_ids"]) <= source_ids)
            supported += row["state"].startswith("SUPPORTED")
            opened += row["state"].startswith("OPEN")
        self.assertEqual(supported, 4)
        self.assertEqual(opened, 6)

    def test_metric_vocabulary_is_not_collapsed(self):
        combined = self.page + json.dumps(self.claims) + json.dumps(self.transitions)
        for token in ("impact", "stolen", "frozen", "recovered", "compensated"):
            self.assertIn(token, combined.lower())
        self.assertIn("IMPACT ≠ STOLEN ≠ FROZEN ≠ RECOVERED ≠ COMPENSATED", self.page)
        self.assertIn("Frozen does not mean recovered, returned, compensated", json.dumps(self.claims))

    def test_chain_observation_is_object_level_only(self):
        self.assertEqual(self.chain["block_number_decimal"], 26300770)
        self.assertEqual(self.chain["block_timestamp"], "2026-10-29T20:24:23Z")
        self.assertEqual(self.chain["receipt_status_hex"], "0x1")
        self.assertEqual(self.chain["receipt_log_count"], 64)
        self.assertIn("Root cause, intent or actor attribution", self.chain["not_verified"])
        for digest in self.chain["raw_response_sha256"].values():
            self.assertRegex(digest, SHA256)

    def test_transitions_are_ordered_and_decision_gap_is_open(self):
        events = self.transitions["events"]
        self.assertEqual([e["sequence"] for e in events], list(range(1, 12)))
        times = [parse_time(e["event_time"]) for e in events]
        self.assertEqual(times, sorted(times))
        self.assertEqual(self.transitions["decision_gap"]["status"], "OPEN_INSUFFICIENT_PUBLIC_EVIDENCE")
        self.assertGreaterEqual(len(self.transitions["decision_gap"]["closure_tests"]), 5)
        self.assertIn("No solvency", self.transitions["decision_gap"]["prohibited_inference"])

    def test_draft_is_preserved_and_production_route_is_public(self):
        self.assertTrue((CASE / "index.draft.html").is_file())
        self.assertTrue((CASE / "index.html").is_file())
        draft = DraftHTMLParser()
        draft.feed(self.draft_page)
        public = DraftHTMLParser()
        public.feed(self.page)
        self.assertEqual(draft.robots, "noindex,nofollow,noarchive")
        self.assertIn("DRAFT · NOT PUBLISHED", self.draft_page)
        self.assertEqual(public.lang, "en")
        self.assertIsNone(public.robots)
        self.assertEqual(public.canonical, "https://structurevidence.org/cases/binance-security-2026/")
        self.assertEqual(public.og["og:url"], public.canonical)
        self.assertIn('type="application/ld+json"', self.page)
        self.assertNotIn("DRAFT · NOT PUBLISHED", self.page)
        self.assertFalse(self.control["public_route_present"])
        for gate in ("production_deployment_authorized", "social_publication_authorized", "external_outreach_authorized", "paid_offering_authorized", "merge_authorized"):
            self.assertFalse(self.control[gate])
        self.assertTrue(self.approval["publication_authorized"])
        self.assertTrue(self.approval["merge_authorized_if_all_gates_pass"])
        self.assertEqual(self.approval["social_publication"], "HUMAN_GATE_REQUIRED")

    def test_case_index_sitemap_and_public_mirror_are_registered(self):
        route = "/cases/binance-security-2026/"
        for relative in ("cases/index.html", "docs/cases/index.html", "sitemap.xml", "docs/sitemap.xml"):
            self.assertIn(route, (ROOT / relative).read_text(encoding="utf-8"))
        mirrored = [
            "index.html", "index.json", "baseline-v0.1.json", "claims-v0.1.json",
            "onchain-observations-v0.1.json", "publication-approval-v0.1.json",
            "source-registry-v0.1.json", "source-review-20261030-02.json", "state-transitions-v0.1.json",
            "source-captures/BSEC-S001.normalized.txt", "source-captures/BSEC-S005.normalized.txt",
            "source-captures/BSEC-S001-20261030T081822Z.normalized.txt",
            "source-captures/BSEC-S005-20261030T081822Z.normalized.txt",
        ]
        for relative in mirrored:
            self.assertEqual((CASE / relative).read_bytes(), (ROOT / "docs/cases/binance-security-2026" / relative).read_bytes(), relative)
        self.assertFalse((ROOT / "docs/cases/binance-security-2026/index.draft.html").exists())
        changed = subprocess.check_output(["git", "diff", "--name-only", BASELINE_SHA], cwd=ROOT, text=True).splitlines()
        forbidden = [name for name in changed if name.startswith(("deploy/", ".github/workflows/"))]
        self.assertEqual(forbidden, [])

    def test_all_visible_timeline_timestamps_are_explicitly_utc(self):
        labels = re.findall(r"<time[^>]*>(.*?)</time>", self.page)
        self.assertGreaterEqual(len(labels), 6)
        self.assertTrue(all("UTC" in label for label in labels), labels)

    def test_lineage_and_open_claim_language_is_public(self):
        self.assertIn("three independent non-operator originators", self.page)
        self.assertIn("one syndicated lineage", self.page)
        self.assertIn("same Binance lineage", self.page)
        for claim_id in ("BSEC-R003", "BSEC-R004", "BSEC-R005", "BSEC-R007", "BSEC-R008", "BSEC-R009"):
            self.assertIn(claim_id, self.page)
        self.assertEqual(self.index["open_claim_count"], 6)
        self.assertEqual(self.index["supported_claim_count"], 4)

    def test_social_candidates_are_human_gated(self):
        social = (CASE / "SOCIAL_CANDIDATES.md").read_text(encoding="utf-8")
        self.assertIn("DO_NOT_PUBLISH", social)
        self.assertIn("after publication only", social)
        self.assertIn("No scheduler or social API is authorized", social)

    def test_public_safe_privacy_and_legal_boundary(self):
        payload = "\n".join(path.read_text(encoding="utf-8") for path in CASE.rglob("*") if path.is_file()).lower()
        for forbidden in ("/users/roal", "cookie:", "authorization:", "api_key", "private key material", "customer_private"):
            self.assertNotIn(forbidden, payload)
        self.assertIn("no solvency", payload)
        self.assertIn("not investment, legal, compliance, accounting, cybersecurity or solvency advice", self.page)

    def test_changes_are_append_only_and_allowlisted(self):
        changed = subprocess.check_output(["git", "diff", "--name-only", BASELINE_SHA], cwd=ROOT, text=True).splitlines()
        allowed = (
            "cases/binance-security-2026/", "docs/cases/binance-security-2026/",
            "cases/index.html", "docs/cases/index.html", "cases/review-status.json", "docs/cases/review-status.json",
            "sitemap.xml", "docs/sitemap.xml", "scripts/export_case_review_status.py",
            "scripts/test_binance_security_candidate.py", "scripts/validate_case_watch.py",
        )
        self.assertFalse([name for name in changed if not name.startswith(allowed)])


if __name__ == "__main__":
    unittest.main(verbosity=2)
