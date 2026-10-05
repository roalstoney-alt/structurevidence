#!/usr/bin/env python3
"""Boundary tests for OIL-GENESIS-001 Stage 3 human outreach review prep."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = ROOT / "data/open-intent-lab/genesis-001"
OUTREACH_DIR = DATA_ROOT / "outreach"
REVIEW_DIR = OUTREACH_DIR / "review"
PREP_PATH = OUTREACH_DIR / "human-review-prep.json"
TRACKER_PATH = OUTREACH_DIR / "outreach-tracker.json"
DICTIONARY_PATH = DATA_ROOT / "claim-dictionary.json"
CONSOLIDATED_PATH = ROOT / "docs/open-intent-lab/genesis/OIL_GENESIS_001_HUMAN_OUTREACH_REVIEW.md"
REPORT_PATH = ROOT / "docs/open-intent-lab/execution/STAGE_03_HUMAN_OUTREACH_REVIEW_PREP_REPORT.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

EXPECTED_CANDIDATES = [f"OIL-CAND-{index:03d}" for index in range(1, 6)]
EXPECTED_CLAIMS = [f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)]
EXPECTED_COUNTS = [7, 7, 6, 5, 5]
IDENTITY_STATES = {"CONFIRMED", "PARTIAL", "UNRESOLVED"}
CONTACT_STATES = {"CONFIRMED", "USABLE_WITH_LIMITATION", "UNRESOLVED"}
CLAIM_REVIEW_STATES = {"KEEP", "REMOVE", "REWORD_SCOPE", "HOLD"}
THRESHOLD_STATES = {
    "APPROPRIATE",
    "TOO_BROAD",
    "TOO_STRICT",
    "SCOPE_AMBIGUOUS",
    "SOURCE_REQUIREMENT_AMBIGUOUS",
}
REQUIRED_CARD_FIELDS = [
    "CANDIDATE_ID",
    "ENTITY",
    "LEGAL_ENTITY_STATUS",
    "MANUFACTURER_ATTRIBUTION",
    "PRODUCT_FAMILY",
    "OFFICIAL_DOMAIN",
    "CONTACT_ROUTE",
    "CONTACT_ROUTE_STATUS",
    "CLAIMS_CURRENTLY_REQUESTED",
    "CLAIMS_RECOMMENDED_AFTER_REVIEW",
    "CLAIMS_REMOVED_OR_REWORDED",
    "EVIDENCE_THRESHOLD_RESULT",
    "VISIBILITY_MODEL_PRESENT",
    "HISTORICAL_RECORD_NOTICE_RESULT",
    "SUPPLIER_BURDEN",
    "KNOWN_SCOPE_RISKS",
    "KNOWN_CONTACT_RISKS",
    "OPEN_QUESTIONS",
    "CODEX_PREP_RECOMMENDATION",
    "SEND_APPROVAL",
]
FORBIDDEN_PRODUCTION_KEYS = {
    "provider_id",
    "verified_capability_fact_id",
    "verified_capability_facts",
    "capability_fact_id",
    "demand_id",
    "outcome_id",
    "reuse_record_id",
    "evidence_hash",
    "ranking",
    "rank",
    "score",
    "trust_score",
}
FROZEN_DICTIONARY_SHA256 = "e03e5671addcf258959dc9003658a08a4147aac3a59fb8c2668d7a049adff513"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class HumanOutreachReviewPrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prep = load_json(PREP_PATH)
        cls.tracker = load_json(TRACKER_PATH)
        cls.dictionary = load_json(DICTIONARY_PATH)
        cls.cards = sorted(REVIEW_DIR.glob("candidate-*-review.md"))
        cls.candidates = cls.prep["candidates"]

    def test_exactly_five_review_cards_and_frozen_candidates(self):
        self.assertEqual([path.name for path in self.cards], [f"candidate-{i:03d}-review.md" for i in range(1, 6)])
        self.assertEqual([row["candidate_id"] for row in self.candidates], EXPECTED_CANDIDATES)
        self.assertEqual(self.prep["candidate_scope"], EXPECTED_CANDIDATES)

    def test_no_additional_supplier_appears(self):
        provider_files = sorted((DATA_ROOT / "providers").glob("candidate-*.json"))
        provider_ids = [load_json(path)["provider_candidate_id"] for path in provider_files]
        self.assertEqual(provider_ids, EXPECTED_CANDIDATES)
        consolidated = CONSOLIDATED_PATH.read_text(encoding="utf-8")
        mentioned = sorted(set(re.findall(r"OIL-CAND-\d{3}", consolidated)))
        self.assertEqual(mentioned, EXPECTED_CANDIDATES)

    def test_every_candidate_has_legal_identity_and_contact_status(self):
        for candidate in self.candidates:
            self.assertIn(candidate["identity_status"], IDENTITY_STATES)
            self.assertTrue(candidate["legal_entity_name"])
            self.assertTrue(candidate["manufacturing_entity"])
            self.assertTrue(candidate["contracting_entity"])
            self.assertIn(candidate["contact_route"]["status"], CONTACT_STATES)
            for field in ["contact_type", "contact_value_or_reference", "source", "entity_attribution", "region", "business_unit", "confidence_basis"]:
                self.assertTrue(candidate["contact_route"][field])

    def test_claim_ids_and_counts_stay_within_frozen_dictionary(self):
        dictionary_ids = [claim["claim_id"] for claim in self.dictionary["claims"]]
        self.assertEqual(dictionary_ids, EXPECTED_CLAIMS)
        self.assertEqual(self.prep["frozen_claim_scope"], EXPECTED_CLAIMS)
        for candidate, expected_count in zip(self.candidates, EXPECTED_COUNTS):
            self.assertEqual(len(candidate["current_claim_ids"]), expected_count)
            self.assertGreaterEqual(expected_count, 3)
            self.assertLessEqual(expected_count, 7)
            self.assertLessEqual(set(candidate["current_claim_ids"]), set(EXPECTED_CLAIMS))
            self.assertLessEqual(set(candidate["recommended_claim_ids"]), set(EXPECTED_CLAIMS))

    def test_all_thirty_claim_pairs_have_complete_review(self):
        rows = [row for candidate in self.candidates for row in candidate["claim_review"]]
        self.assertEqual(len(rows), 30)
        for candidate in self.candidates:
            self.assertEqual([row["claim_id"] for row in candidate["claim_review"]], candidate["current_claim_ids"])
        for row in rows:
            self.assertTrue(row["current_request"])
            self.assertIn(row["human_review"], CLAIM_REVIEW_STATES)
            self.assertIn(row["evidence_threshold"], THRESHOLD_STATES)
            self.assertTrue(row["scope_match"])
            self.assertTrue(row["evidence_likely_available"])

    def test_every_candidate_reviews_visibility_history_burden_and_risk(self):
        for candidate in self.candidates:
            self.assertTrue(candidate["visibility_model_present"])
            self.assertTrue(candidate["visibility_fail_closed"])
            self.assertTrue(candidate["historical_record_notice_result"])
            self.assertIn(candidate["supplier_burden"], {"LOW", "MODERATE", "HIGH"})
            self.assertTrue(candidate["known_scope_risks"])
            self.assertTrue(candidate["known_contact_risks"])
            self.assertTrue(candidate["open_questions"])
            self.assertIn(candidate["codex_prep_recommendation"], {"READY_FOR_HUMAN_DECISION", "HOLD_FOR_CLARIFICATION"})

    def test_review_cards_have_required_human_fields_and_unset_decision(self):
        for card in self.cards:
            text = card.read_text(encoding="utf-8")
            for field in REQUIRED_CARD_FIELDS:
                self.assertRegex(text, rf"(?m)^{re.escape(field)} = .+")
            self.assertIn("SEND_APPROVAL = UNSET", text)
            self.assertNotIn("SEND_APPROVAL = YES", text)
            self.assertIn("No outreach was sent", text)

    def test_send_approval_and_authorization_remain_fail_closed(self):
        rules = self.prep["review_rules"]
        self.assertFalse(rules["codex_may_set_send_approval_yes"])
        self.assertFalse(rules["send_authorized"])
        self.assertEqual(rules["messages_sent"], 0)
        for candidate in self.candidates:
            self.assertEqual(candidate["send_approval"], "UNSET")
            self.assertEqual(candidate["human_decision"], "UNSET")

    def test_tracker_is_prepared_but_unsent(self):
        self.assertEqual(self.tracker["messages_sent"], 0)
        self.assertEqual(len(self.tracker["records"]), 5)
        if self.tracker["stage"] == "STAGE_3_FINAL_OUTREACH_EXECUTION":
            self.assertTrue(self.tracker["send_authorized"])
            self.assertEqual([record["send_authorized"] for record in self.tracker["records"]], [True, True, True, True, False])
        else:
            self.assertFalse(self.tracker["send_authorized"])
        for index, record in enumerate(self.tracker["records"], start=1):
            self.assertTrue(record["human_review_prepared"])
            self.assertRegex(record["human_review_prepared_at"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertEqual(record["human_review_file"], f"data/open-intent-lab/genesis-001/outreach/review/candidate-{index:03d}-review.md")
            self.assertIn(record["send_approval"], {"UNSET", "YES", "NO", "HOLD"})
            self.assertIsNone(record["sent_at"])
            self.assertEqual(record["response_status"], "OUTREACH_PREPARED")

    def test_no_production_records_truth_statuses_or_scores_are_created(self):
        for payload in (self.prep, self.tracker):
            keys = set(walk_keys(payload))
            self.assertFalse(keys & FORBIDDEN_PRODUCTION_KEYS, keys & FORBIDDEN_PRODUCTION_KEYS)
        serialized = json.dumps(self.prep)
        self.assertNotIn('"SUPPORTED"', serialized)
        self.assertNotIn('"OBSERVED"', serialized)
        self.assertFalse(self.prep["review_rules"]["production_records_created"])
        self.assertFalse(self.prep["review_rules"]["capability_statuses_assigned"])

    def test_frozen_claim_dictionary_and_public_case_boundary(self):
        digest = hashlib.sha256(DICTIONARY_PATH.read_bytes()).hexdigest()
        self.assertEqual(digest, FROZEN_DICTIONARY_SHA256)
        completed = subprocess.run(
            ["git", "diff", "--name-only", BASE_SHA, "--", "cases", "claims", "evidence", "docs/cases", "public"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")

    def test_consolidated_document_and_report_are_complete(self):
        consolidated = CONSOLIDATED_PATH.read_text(encoding="utf-8")
        report = REPORT_PATH.read_text(encoding="utf-8")
        for heading in ["Review objective", "Review method and boundary", "Consolidated review", "Candidate recommendations", "Claims and threshold review", "Supplier-facing safeguards", "Burden summary", "Official-source verification notes", "Human decision gate"]:
            self.assertIn(f"## {heading}", consolidated)
        self.assertIn("SEND_APPROVAL = UNSET FOR ALL FIVE", consolidated)
        self.assertIn("12/12 PASS", report)
        self.assertIn("SEND_AUTHORIZED = NO", report)
        self.assertIn("MESSAGES_SENT = 0", report)
        self.assertIn("NEXT_ALLOWED_STAGE = STAGE_3_HUMAN_SEND_DECISION", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
