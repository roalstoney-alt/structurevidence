#!/usr/bin/env python3
"""Boundary tests for OIL-GENESIS-001 Stage 3 human send decision."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTREACH_DIR = ROOT / "data/open-intent-lab/genesis-001/outreach"
TRACKER_PATH = OUTREACH_DIR / "outreach-tracker.json"
DICTIONARY_PATH = ROOT / "data/open-intent-lab/genesis-001/claim-dictionary.json"
DECISION_PATH = ROOT / "docs/open-intent-lab/genesis/OIL_GENESIS_001_HUMAN_SEND_DECISION.md"
HOLD_PATH = OUTREACH_DIR / "candidate-005-hold-resolution.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

EXPECTED_CANDIDATES = [f"OIL-CAND-{index:03d}" for index in range(1, 6)]
EXPECTED_CLAIMS = [f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)]
EXPECTED_CLAIM_SETS = [
    EXPECTED_CLAIMS,
    EXPECTED_CLAIMS,
    EXPECTED_CLAIMS[:6],
    EXPECTED_CLAIMS[:5],
]
EXPECTED_ROUTES = [
    "info@venair.com",
    "https://www.biopharm.saint-gobain.com/contact-us#Application-Support-or-Quality",
    "compliance@newageindustries.com",
    "https://www.wmfts.com/global/#BioPure-Contact-an-expert",
]
FROZEN_DICTIONARY_SHA256 = "e03e5671addcf258959dc9003658a08a4147aac3a59fb8c2668d7a049adff513"
FORBIDDEN_FUTURE_EVENTS = {
    "OUTREACH_SENT",
    "SUPPLIER_RESPONDED",
    "EVIDENCE_SUBMITTED",
    "NO_RESPONSE",
    "REFUSED_EVIDENCE",
    "REFUSED_ANY_VISIBILITY",
    "TOO_BUSY",
    "NOT_THIS_CAPABILITY",
    "WITHDRAWN",
}
FORBIDDEN_PRODUCTION_KEYS = {
    "provider_id",
    "verified_capability_fact_id",
    "verified_capability_facts",
    "capability_fact_id",
    "evidence_record_id",
    "evidence_hash",
    "demand_id",
    "outcome_id",
    "reuse_record_id",
    "ranking",
    "rank",
    "score",
    "trust_score",
}
FORBIDDEN_PROMOTIONAL_PHRASES = {
    "buyer leads",
    "guaranteed orders",
    "preferred supplier",
    "verified vendor badge",
    "increase your ranking",
    "premium exposure",
    "purchase commitment from us",
}


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


class HumanSendDecisionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_json(TRACKER_PATH)
        cls.records = cls.tracker["records"]
        cls.dictionary = load_json(DICTIONARY_PATH)
        cls.approved = cls.records[:4]

    def test_all_five_human_decisions_are_explicit(self):
        self.assertEqual([record["candidate_id"] for record in self.records], EXPECTED_CANDIDATES)
        self.assertEqual([record["send_approval"] for record in self.records], ["YES", "YES", "YES", "YES", "HOLD"])
        self.assertEqual([record["human_send_approval"] for record in self.records], ["YES", "YES", "YES", "YES", "HOLD"])
        self.assertNotIn("UNSET", {record["send_approval"] for record in self.records})
        self.assertEqual(self.tracker["approved_for_outreach"], 4)
        self.assertEqual(self.tracker["held_for_clarification"], 1)

    def test_approved_records_have_frozen_recipient_message_hash_and_claims(self):
        for record, expected_route, expected_claims in zip(self.approved, EXPECTED_ROUTES, EXPECTED_CLAIM_SETS):
            self.assertEqual(record["final_recipient_or_channel"], expected_route)
            self.assertEqual(record["final_claim_ids"], expected_claims)
            message_path = ROOT / record["final_message_file"]
            self.assertTrue(message_path.is_file())
            digest = hashlib.sha256(message_path.read_bytes()).hexdigest()
            self.assertEqual(record["final_message_hash"], f"sha256:{digest}")

    def test_final_claim_sets_use_only_frozen_stage_one_claims(self):
        dictionary_ids = [claim["claim_id"] for claim in self.dictionary["claims"]]
        self.assertEqual(dictionary_ids, EXPECTED_CLAIMS)
        for record in self.approved:
            self.assertGreaterEqual(len(record["final_claim_ids"]), 3)
            self.assertLessEqual(len(record["final_claim_ids"]), 7)
            self.assertLessEqual(set(record["final_claim_ids"]), set(EXPECTED_CLAIMS))
            self.assertEqual(record["final_claim_ids"], record["claims_requested"])

    def test_final_contact_routes_are_official_and_not_guessed(self):
        self.assertEqual(self.approved[0]["final_recipient_or_channel"], "info@venair.com")
        self.assertEqual(self.approved[2]["final_recipient_or_channel"], "compliance@newageindustries.com")
        for record in (self.approved[1], self.approved[3]):
            route = record["final_recipient_or_channel"]
            self.assertTrue(route.startswith("https://"))
        self.assertIn("saint-gobain.com", self.approved[1]["final_recipient_or_channel"])
        self.assertIn("wmfts.com", self.approved[3]["final_recipient_or_channel"])

    def test_every_final_message_contains_required_outreach_terms(self):
        for record in self.approved:
            text = (ROOT / record["final_message_file"]).read_text(encoding="utf-8")
            lowered = text.lower()
            for phrase in [
                "reusable",
                "predefined claims",
                "existing documents are preferred",
                "no need to create a bespoke report",
                "supplier statements alone do not establish verified capability",
                "scoped and timestamped",
                "future evidence or transaction outcomes",
                "not certification",
                "supplier ranking",
                "marketplace placement",
                "public",
                "authorized_buyer",
                "transaction_private",
                "voluntary",
                "10 business days after receipt",
            ]:
                self.assertIn(phrase, lowered, (record["candidate_id"], phrase))

    def test_messages_contain_no_promotional_or_purchase_promise(self):
        for record in self.approved:
            lowered = (ROOT / record["final_message_file"]).read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PROMOTIONAL_PHRASES:
                self.assertNotIn(phrase, lowered, (record["candidate_id"], phrase))

    def test_trelleborg_remains_hold_with_resolution_record(self):
        held = self.records[4]
        self.assertEqual(held["candidate_id"], "OIL-CAND-005")
        self.assertEqual(held["send_approval"], "HOLD")
        self.assertIsNone(held["final_recipient_or_channel"])
        self.assertIsNone(held["final_message_file"])
        self.assertIsNone(held["final_message_hash"])
        self.assertEqual(held["final_claim_ids"], [])
        text = HOLD_PATH.read_text(encoding="utf-8")
        for field in ["CANDIDATE_ID", "BRAND_BUSINESS_AREA", "KNOWN_PRODUCT_FAMILIES", "CURRENT_PRODUCT_LITERATURE", "POSSIBLE_LEGAL_ENTITIES", "POSSIBLE_MANUFACTURING_SITES", "OFFICIAL_CONTACT_ROUTE", "UNRESOLVED_RELATIONSHIP", "REQUIRED_EVIDENCE_TO_CLEAR_HOLD"]:
            self.assertRegex(text, rf"(?m)^{field} = .+")
        self.assertIn("SEND_APPROVAL = HOLD", text)
        self.assertIn("SEND_AUTHORIZED = NO", text)

    def test_only_actual_human_approval_events_exist(self):
        for record in self.approved:
            events = record["outreach_events"]
            self.assertIn(len(events), {1, 2})
            self.assertEqual(events[0]["event_type"], "HUMAN_SEND_APPROVED")
            self.assertTrue(events[0]["append_only"])
            if len(events) == 2:
                self.assertEqual(events[1]["event_type"], "OUTREACH_EXECUTION_BLOCKED")
                self.assertTrue(events[1]["append_only"])
        self.assertEqual(self.records[4]["outreach_events"], [])
        all_events = {event["event_type"] for record in self.records for event in record["outreach_events"]}
        self.assertFalse(all_events & FORBIDDEN_FUTURE_EVENTS)

    def test_no_message_is_marked_sent_and_authorization_scope_is_exact(self):
        if self.tracker["stage"] == "STAGE_3_FINAL_OUTREACH_EXECUTION":
            self.assertTrue(self.tracker["send_authorized"])
            self.assertEqual([record["send_authorized"] for record in self.records], [True, True, True, True, False])
        else:
            self.assertFalse(self.tracker["send_authorized"])
        self.assertEqual(self.tracker["messages_sent"], 0)
        for record in self.records:
            self.assertIsNone(record["send_timestamp"])
            self.assertIsNone(record["sent_at"])
            self.assertEqual(record["response_status"], "OUTREACH_PREPARED")

    def test_no_production_records_statuses_or_scores_are_created(self):
        keys = set(walk_keys(self.tracker))
        self.assertFalse(keys & FORBIDDEN_PRODUCTION_KEYS, keys & FORBIDDEN_PRODUCTION_KEYS)
        values = set(re.findall(r'"([A-Z_]+)"', json.dumps(self.tracker)))
        self.assertFalse(values & {"SUPPORTED", "OBSERVED", "UNKNOWN", "NOT_ESTABLISHED", "CONTRADICTED"})

    def test_claim_dictionary_and_public_case_boundary_remain_frozen(self):
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

    def test_decision_document_records_ready_state_and_no_new_supplier(self):
        text = DECISION_PATH.read_text(encoding="utf-8")
        mentioned = sorted(set(re.findall(r"OIL-CAND-\d{3}", text)))
        self.assertEqual(mentioned, EXPECTED_CANDIDATES)
        self.assertIn("APPROVED_FOR_OUTREACH = 4", text)
        self.assertIn("MESSAGES_ACTUALLY_SENT = 0", text)
        self.assertIn("SEND_AUTHORIZED_FOR_CURRENT_TRANSMISSION = NONE", text)
        self.assertIn("NEXT_ALLOWED_STAGE = STAGE_3_FINAL_OUTREACH_EXECUTION", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
