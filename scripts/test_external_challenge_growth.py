#!/usr/bin/env python3
"""Safety and integration tests for SE-EXTERNAL-CHALLENGE-GROWTH-PILOT-001."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "growth" / "external-challenge"
CASE = ROOT / "cases" / "iren-ai-cloud-transition"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_digest(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"not a PNG: {path}")
    return struct.unpack(">II", data[16:24])


class ExternalChallengeGrowthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.export = load(BASE / "evidence-exports" / "2026-10-29.json")
        cls.cards = load(BASE / "visuals" / "card-data.json")
        cls.candidates = load(BASE / "challengers" / "candidates.public-safe.json")
        cls.tracker = load(CASE / "tracker-v0.1.json")
        cls.card_manifest = load(BASE / "output" / "cards" / "asset-manifest.json")

    def test_daily_export_is_bounded_and_hash_valid(self):
        self.assertEqual(self.export["status"], "RETRIEVAL_INCOMPLETE")
        self.assertEqual(self.export["qualifying_change_count"], 0)
        self.assertEqual(self.export["changed_conditions"], [])
        self.assertEqual(len(self.export["claims"]), len(self.tracker["rows"]))
        body = dict(self.export)
        recorded = body.pop("content_sha256")
        self.assertEqual(recorded, canonical_digest(body))
        self.assertEqual(self.export["publication_status"], "DO_NOT_PUBLISH_UNTIL_HUMAN_REVIEW")

    def test_claim_export_has_required_provenance(self):
        for claim in self.export["claims"]:
            self.assertRegex(claim["claim_id"], r"^IREN-R\d{3}$")
            self.assertTrue(claim["speaker_attribution"])
            self.assertTrue(claim["source_references"])
            self.assertEqual(set(claim["source_references"]), set(claim["capture_hashes"]))
            self.assertTrue(claim["availability"])
            self.assertEqual(claim["evidence_cutoff"], self.tracker["evidence_cutoff"])
            self.assertEqual(claim["changed_conditions"], [])
            self.assertTrue(claim["what_would_change_it"])

    def test_export_is_public_safe(self):
        text = json.dumps(self.export).lower()
        for forbidden in ("customer_private", "priv-iren", "se2cases", "/users/roal", "cookie:", "authorization:"):
            self.assertNotIn(forbidden, text)
        self.assertNotRegex(text, r"\b(buy|sell|hold)\s+(rating|recommendation)")

    def test_visual_cards_are_review_only_and_source_bounded(self):
        self.assertEqual(len(self.cards["cards"]), 3)
        for card in self.cards["cards"]:
            self.assertEqual(card["publication_status"], "DO_NOT_PUBLISH")
            self.assertTrue(card["source_url"].startswith("https://"))
            self.assertTrue(card["what_would_change_it"])
            self.assertIn(card["claim_id"], {"IREN-R003", "IREN-R004", "IREN-R009"})

    def test_playwright_outputs_have_expected_dimensions_and_hashes(self):
        self.assertEqual(self.card_manifest["publication_status"], "DO_NOT_PUBLISH")
        self.assertEqual(len(self.card_manifest["assets"]), 6)
        for asset in self.card_manifest["assets"]:
            path = ROOT / asset["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(png_dimensions(path), (asset["width"], asset["height"]))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), asset["sha256"])
            self.assertEqual(asset["approval"], "PENDING_HUMAN_REVIEW")

    def test_candidate_research_is_public_safe_and_qualified(self):
        candidates = self.candidates["candidates"]
        self.assertGreaterEqual(len(candidates), 10)
        self.assertLessEqual(len(candidates), 15)
        serialized = json.dumps(candidates)
        self.assertNotIn("@", serialized)
        for candidate in candidates:
            self.assertTrue(candidate["professional_source_url"].startswith("https://"))
            self.assertTrue(candidate["relevance"])
            self.assertTrue(candidate["challenge_question"].endswith("?"))
            self.assertFalse(candidate["contact_details_stored"])

    def test_outreach_is_draft_only_and_not_sent(self):
        drafts = (BASE / "outreach" / "OWNER_REVIEW_DRAFTS.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(re.findall(r"^## Draft \d+", drafts, flags=re.M)), 5)
        self.assertIn("OUTREACH_SENT=0", drafts)
        self.assertNotIn("sent_at:", drafts)

    def test_feedback_ledger_separates_synthetic_and_external(self):
        ledger = (BASE / "feedback-ledger" / "ledger.jsonl").read_text(encoding="utf-8")
        self.assertFalse(ledger.strip())
        fixture = load(BASE / "tests" / "fixtures" / "internal-synthetic.json")
        self.assertEqual(fixture["event_type"], "INTERNAL_SYNTHETIC")
        self.assertEqual(fixture["privacy_class"], "INTERNAL_SYNTHETIC")
        self.assertEqual(fixture["verification_status"], "SYNTHETIC_TEST_ONLY")
        fixture_body = dict(fixture)
        fixture_digest = fixture_body.pop("event_digest")
        self.assertEqual(fixture_digest, canonical_digest(fixture_body))

    def test_feedback_ledger_append_only_chain_and_access_blocked_event(self):
        first = load(BASE / "tests" / "fixtures" / "internal-synthetic.json")
        second = {
            "event_id": "SE-EFL-20261029-002",
            "event_type": "ACCESS_BLOCKED",
            "observed_at": "2026-10-29T00:01:00Z",
            "case_id": "SE-IREN-AI-CLOUD-001",
            "claim_id": "IREN-R003",
            "source_url": None,
            "privacy_class": "PRIVATE_RESTRICTED",
            "verification_status": "ACCESS_BLOCKED",
            "summary": "Synthetic access-blocked fixture; no private channel was read.",
            "previous_event_digest": first["event_digest"],
        }
        second["event_digest"] = canonical_digest(second)
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "synthetic-ledger.jsonl"
            ledger.write_text(
                "\n".join(json.dumps(event, sort_keys=True) for event in (first, second)) + "\n",
                encoding="utf-8",
            )
            events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        previous = None
        for event in events:
            self.assertEqual(event["previous_event_digest"], previous)
            body = dict(event)
            recorded = body.pop("event_digest")
            self.assertEqual(recorded, canonical_digest(body))
            previous = recorded
        self.assertEqual(events[1]["verification_status"], "ACCESS_BLOCKED")
        self.assertNotEqual(events[1]["event_type"], "EXTERNAL_CHALLENGE")

    def test_site_challenge_workbench_and_ddr_are_public_safe(self):
        page = (CASE / "index.html").read_text(encoding="utf-8")
        self.assertIn('id="challenge-workbench"', page)
        self.assertIn("Challenge the boundary—not the person", page)
        self.assertEqual(page.count("Submit a precise challenge"), 3)
        self.assertIn("ddr-sample.html", page)
        ddr = (CASE / "ddr-sample.html").read_text(encoding="utf-8")
        self.assertIn('content="noindex,nofollow"', ddr)
        self.assertIn("Illustrative sample", ddr)
        self.assertIn("not a client record", ddr)
        self.assertIn("IREN-R009", ddr)
        self.assertNotIn("customer name", ddr.lower())
        self.assertEqual(ddr.encode(), (ROOT / "docs" / "cases" / "iren-ai-cloud-transition" / "ddr-sample.html").read_bytes())

    def test_funnel_links_use_only_existing_public_identifiers(self):
        page = (CASE / "index.html").read_text(encoding="utf-8")
        hrefs = re.findall(r'href="(https://structevidence\.com/(?:verify|decision-pack)/\?[^\"]+)"', page)
        self.assertTrue(hrefs)
        for href in hrefs:
            parsed = urlparse(href.replace("&amp;", "&"))
            query = parse_qs(parsed.query)
            self.assertTrue(set(query) <= {"case", "case_id", "claim_id"})
            self.assertNotIn("evidence", query)
            self.assertNotIn("email", query)
            self.assertNotIn("name", query)
        contract = (BASE / "FUNNEL_VERIFICATION.md").read_text(encoding="utf-8")
        self.assertIn("PRODUCTION_POSTS=0", contract)
        self.assertIn("WORKER_CHANGES=0", contract)

    def test_no_worker_migration_or_social_send_changes(self):
        names = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
        self.assertFalse([name for name in names if name.startswith("deploy/cloudflare-landing/")])
        self.assertFalse([name for name in names if name.startswith(".github/workflows/")])

    def test_final_acceptance_report_preserves_human_send_gate(self):
        report = (BASE / "FINAL_ACCEPTANCE_REPORT.md").read_text(encoding="utf-8")
        required = {
            "EVIDENCE_EXPORT = PASS",
            "VISUAL_ENGINE = PASS",
            "FUNNEL_VERIFIED = PASS",
            "CHALLENGERS_RESEARCHED = 13",
            "OUTREACH_DRAFTS_READY = 5",
            "OUTREACH_SENT = 0",
            "EXTERNAL_CHALLENGES_OBSERVED = 0",
            "EXTERNAL_CITATIONS_OBSERVED = 0",
            "INBOUND_DECISION_REQUESTS_OBSERVED = 0",
            "SOCIAL_POSTS_SENT = 0",
            "NEW_REGRESSION_COUNT = 0",
            "READY_FOR_HUMAN_GROWTH_REVIEW = YES",
        }
        for line in required:
            self.assertIn(line, report)
        self.assertIn("not claims of achieved or absent market adoption", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
