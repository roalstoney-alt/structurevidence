#!/usr/bin/env python3
"""Adversarial and release-candidate checks for the public IREN tracker."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "cases" / "iren-ai-cloud-transition"
BASE_SHA = "a3264420664a5c471fbc33829fc203429ca0f814"


def load(name: str) -> dict:
    return json.loads((CASE / name).read_text(encoding="utf-8"))


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids: set[str] = set()
        self.canonical = None
        self.lang = None
        self.challenge_hrefs: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang")
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")
        if tag == "a" and "Challenge IREN-R" in attrs.get("aria-label", ""):
            self.challenge_hrefs.append(attrs.get("href", ""))
        if tag == "a" and attrs.get("href", "").startswith("https://structevidence.com/verify/?case_id=SE-IREN-AI-CLOUD-001&claim_id="):
            self.challenge_hrefs.append(attrs["href"])


class IrenTrackerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load("tracker-v0.1.json")
        cls.registry = load("source-registry-v0.1.json")
        cls.ledger = load("events-v0.1.json")
        cls.snapshot = load("index.json")
        cls.page = (CASE / "index.html").read_text(encoding="utf-8")
        cls.parser = PageParser()
        cls.parser.feed(cls.page)
        cls.sources = {source["source_id"]: source for source in cls.registry["sources"]}

    def test_four_blocks_and_review_hold_are_visible(self):
        self.assertTrue({"supported", "not-established", "watch", "change-log"} <= self.parser.ids)
        self.assertIn("PENDING HUMAN REVIEW", self.page)
        self.assertIn("not approved for publication", self.page)
        self.assertEqual(self.tracker["publication_status"], "READY_FOR_HUMAN_PUBLICATION_REVIEW")

    def test_all_rows_have_stable_ids_sources_next_checks_and_events(self):
        rows = self.tracker["rows"]
        row_ids = [row["row_id"] for row in rows]
        self.assertEqual(len(row_ids), len(set(row_ids)))
        event_ids = {event["event_id"] for event in self.ledger["events"]}
        for row in rows:
            self.assertRegex(row["row_id"], r"^IREN-R\d{3}$")
            self.assertTrue(row["source_ids"])
            self.assertTrue(set(row["source_ids"]) <= set(self.sources))
            self.assertTrue(row["next_check"])
            self.assertIn(row["last_event_id"], event_ids)
            self.assertIn(f'id="{row["row_id"]}"', self.page)

    def test_supported_rows_are_attributed_and_use_captured_sources(self):
        for row in self.tracker["rows"]:
            if row["state"] != "SUPPORTED_AS_ATTRIBUTED":
                continue
            self.assertRegex(row["claim"], r"^IREN (reported|disclosed|stated)")
            for source_id in row["source_ids"]:
                source = self.sources[source_id]
                self.assertEqual(source["access_state"], "CAPTURED")
                self.assertRegex(source["sha256"], r"^[0-9a-f]{64}$")
                self.assertIn("issuer_authored", source["dependency_class"])

    def test_furnished_exhibits_are_not_mislabeled_filed(self):
        for source_id in ("I-S05", "I-S08", "I-S09", "I-S11"):
            self.assertEqual(self.sources[source_id]["liability"], "furnished_not_filed")

    def test_retrieval_failures_are_not_promoted(self):
        incomplete = {source["source_id"] for source in self.registry["sources"] if "INCOMPLETE" in source["access_state"]}
        self.assertEqual(incomplete, {"I-S01", "I-S06", "I-S07", "I-S10"})
        supported_sources = {
            source_id for row in self.tracker["rows"] if row["state"] == "SUPPORTED_AS_ATTRIBUTED"
            for source_id in row["source_ids"]
        }
        self.assertFalse(incomplete & supported_sources)
        self.assertIn("never evidence of absence", self.page)

    def test_measure_definitions_are_not_conflated(self):
        text = " ".join(row["boundary"] for row in self.tracker["rows"])
        self.assertIn("Contracted ARR, operating ARR, recognized revenue, deferred revenue, prepayments, and cash are different measures", text)
        self.assertIn("ARR is non-GAAP", text)
        self.assertIn("not equivalent to cash expenditure", text)
        self.assertIn("ISSUER ACCEPTANCE CLAIM ≠ CUSTOMER-AUTHORED PROOF", self.page)

    def test_no_securities_recommendation_vocabulary(self):
        lowered = self.page.lower()
        for term in ("buy recommendation", "sell recommendation", "bullish", "bearish", "target price", "undervalued", "overvalued"):
            self.assertNotIn(term, lowered)
        self.assertIn("not a recommendation", lowered)
        self.assertNotRegex(lowered, r"\b(score|grade)\s*[:=]")

    def test_challenge_urls_are_fixed_and_public_safe(self):
        self.assertEqual(len(self.tracker["rows"]), len(self.parser.challenge_hrefs))
        for row in self.tracker["rows"]:
            parsed = urlparse(row["challenge_url"])
            query = parse_qs(parsed.query)
            self.assertEqual(parsed.scheme, "https")
            self.assertEqual(parsed.netloc, "structevidence.com")
            self.assertEqual(parsed.path, "/verify/")
            self.assertEqual(set(query), {"case_id", "claim_id"})
            self.assertEqual(query["case_id"], [self.tracker["case_id"]])
            self.assertEqual(query["claim_id"], [row["row_id"]])
        self.assertFalse(self.tracker["commercial_boundary"]["production_post_authorized"])

    def test_event_chain_and_digests_are_valid(self):
        previous = None
        event_ids = set()
        for event in self.ledger["events"]:
            self.assertNotIn(event["event_id"], event_ids)
            event_ids.add(event["event_id"])
            self.assertEqual(event["previous_event_digest"], previous)
            core = {key: value for key, value in event.items() if key != "event_digest"}
            self.assertEqual(event["event_digest"], "sha256:" + digest(core))
            self.assertRegex(event["evidence_digest"], r"^sha256:[0-9a-f]{64}$")
            previous = event["event_digest"]

    def test_public_export_is_allowlisted_and_private_safe(self):
        allowed_source_keys = {
            "source_id", "publisher", "title", "url", "accession", "publication_date",
            "source_type", "dependency_class", "assurance", "liability", "access_state",
            "capture_utc", "sha256", "review_state",
        }
        for source in self.snapshot["sources"]:
            self.assertTrue(set(source) <= allowed_source_keys)
        serialized = json.dumps(self.snapshot).lower()
        for forbidden in ("se2cases", "priv-iren", "customer_private", "/users/roal", "authorization:", "cookie:"):
            self.assertNotIn(forbidden, serialized)

    def test_generated_snapshot_digest_is_valid(self):
        body = dict(self.snapshot)
        recorded = body.pop("content_digest")
        self.assertEqual(recorded, "sha256:" + digest(body))

    def test_canonical_sitemap_index_and_language(self):
        self.assertEqual(self.parser.lang, "en")
        self.assertEqual(self.parser.canonical, "https://structurevidence.org/cases/iren-ai-cloud-transition/")
        sitemap = (ROOT / "sitemap.xml").read_text()
        ET.fromstring(sitemap)
        self.assertNotIn("https://structurevidence.org/cases/iren-ai-cloud-transition/", sitemap)
        self.assertNotIn("hreflang=\"zh-CN\" href=\"https://structurevidence.org/zh-cn/cases/iren-ai-cloud-transition/", sitemap)
        index = (ROOT / "cases" / "index.html").read_text()
        self.assertNotIn("/cases/iren-ai-cloud-transition/", index)
        self.assertEqual((CASE / "index.html").read_bytes(), (ROOT / "docs" / "cases" / "iren-ai-cloud-transition" / "index.html").read_bytes())

    def test_mobile_and_accessibility_hooks(self):
        css = (ROOT / "assets" / "iren-tracker.css").read_text()
        self.assertIn("@media (max-width: 820px)", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn('class="skip-link"', self.page)
        self.assertIn('aria-label="Dated IREN watch items"', self.page)
        self.assertIn('aria-label="IREN source registry"', self.page)

    def test_no_production_worker_or_historic_case_drift(self):
        names = subprocess.check_output(
            ["git", "diff", "--name-only", BASE_SHA], cwd=ROOT, text=True
        ).splitlines()
        forbidden_prefixes = (
            "deploy/cloudflare-landing/", "private/", "evidence-freeze/",
            "cases/800vdc/", "cases/sodium-ion-bess/", "cases/nsq-nsclc-china/",
        )
        self.assertFalse([name for name in names if name.startswith(forbidden_prefixes)])

    def test_adversarial_states_stop_instead_of_manufacturing_pass(self):
        states = {row["row_id"]: row["state"] for row in self.tracker["rows"]}
        self.assertEqual(states["IREN-R007"], "NOT_ESTABLISHED")
        self.assertEqual(states["IREN-R008"], "NOT_ESTABLISHED")
        self.assertEqual(states["IREN-R009"], "NOT_ESTABLISHED")
        self.assertEqual(states["IREN-R010"], "NOT_ESTABLISHED")
        self.assertEqual(self.tracker["experimental_attributes"]["disclosure_ladder_d0_d4"], "PROPOSED_NOT_APPROVED_AND_NOT_APPLIED_TO_ROWS")


if __name__ == "__main__":
    unittest.main(verbosity=2)
