#!/usr/bin/env python3
"""Execution-boundary tests for OIL-GENESIS-001 final outreach."""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTREACH_DIR = ROOT / "data/open-intent-lab/genesis-001/outreach"
BASELINE_PATH = OUTREACH_DIR / "OUTREACH_EXECUTION_BASELINE.json"
EVENTS_PATH = OUTREACH_DIR / "outreach-events.jsonl"
TRACKER_PATH = OUTREACH_DIR / "outreach-tracker.json"
DICTIONARY_PATH = ROOT / "data/open-intent-lab/genesis-001/claim-dictionary.json"
EVIDENCE_MATRIX_PATH = ROOT / "data/open-intent-lab/genesis-001/evidence-request-matrix.json"
REPORT_PATH = ROOT / "docs/open-intent-lab/execution/STAGE_03_FINAL_OUTREACH_EXECUTION_REPORT.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

AUTHORIZED_IDS = [f"OIL-CAND-{index:03d}" for index in range(1, 5)]
ALL_IDS = [*AUTHORIZED_IDS, "OIL-CAND-005"]
EXPECTED_CLAIMS = [f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)]
EXPECTED_CLAIM_SETS = [EXPECTED_CLAIMS, EXPECTED_CLAIMS, EXPECTED_CLAIMS[:6], EXPECTED_CLAIMS[:5]]
DICTIONARY_SHA256 = "e03e5671addcf258959dc9003658a08a4147aac3a59fb8c2668d7a049adff513"
EVIDENCE_MATRIX_SHA256 = "4737a9568baa9de3fd4b2c43179b33ce45720d41c2e37cb5e8ae925c6d30f08c"
FORBIDDEN_EVENT_TYPES = {
    "OUTREACH_SENT",
    "SUPPLIER_RESPONDED",
    "EVIDENCE_SUBMITTED",
    "CLAIM_SCOPE_CORRECTION",
    "CLAIM_WITHDRAWN",
    "EVIDENCE_UNAVAILABLE",
    "CONFIDENTIAL_ONLY",
    "REFUSED_EVIDENCE",
    "REFUSED_ANY_VISIBILITY",
    "TOO_BUSY",
    "NOT_THIS_CAPABILITY",
    "WITHDRAWN",
    "NO_RESPONSE",
}
FORBIDDEN_PRODUCTION_KEYS = {
    "provider_id",
    "verified_capability_fact_id",
    "verified_capability_facts",
    "capability_fact_id",
    "evidence_record_id",
    "demand_id",
    "outcome_id",
    "reuse_record_id",
    "ranking",
    "rank",
    "score",
    "trust_score",
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class FinalOutreachExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_json(BASELINE_PATH)
        cls.tracker = load_json(TRACKER_PATH)
        cls.records = cls.tracker["records"]
        cls.events = load_jsonl(EVENTS_PATH)

    def test_execution_baseline_contains_exactly_four_authorized_candidates(self):
        authorized = self.baseline["authorized_suppliers"]
        self.assertEqual(self.baseline["authorized_count"], 4)
        self.assertEqual([row["candidate_id"] for row in authorized], AUTHORIZED_IDS)
        self.assertNotIn("OIL-CAND-005", {row["candidate_id"] for row in authorized})
        self.assertTrue(self.baseline["human_authorization_timestamp"])
        self.assertEqual(self.baseline["operator"], "CODEX_DESKTOP_LOCAL_AGENT")

    def test_baseline_hashes_match_immutable_message_files(self):
        for row in self.baseline["authorized_suppliers"]:
            message_path = ROOT / row["final_message_path"]
            digest = hashlib.sha256(message_path.read_bytes()).hexdigest()
            self.assertEqual(row["prepared_message_hash"], digest)
            self.assertEqual(row["recalculated_message_hash"], digest)
            self.assertTrue(row["hash_match"])

    def test_authorization_scope_is_four_yes_and_one_hold(self):
        self.assertEqual([record["candidate_id"] for record in self.records], ALL_IDS)
        self.assertEqual([record["send_approval"] for record in self.records], ["YES", "YES", "YES", "YES", "HOLD"])
        if self.tracker.get("lifecycle_status") == "PAUSED":
            self.assertFalse(self.tracker["send_authorized"])
            self.assertEqual(self.tracker["send_authorized_candidate_ids"], [])
            self.assertEqual(self.tracker["approved_for_possible_outreach"], AUTHORIZED_IDS)
            self.assertTrue(all(not record["send_authorized"] for record in self.records))
        else:
            self.assertTrue(self.tracker["send_authorized"])
            self.assertEqual(self.tracker["send_authorized_candidate_ids"], AUTHORIZED_IDS)
            self.assertEqual([record["send_authorized"] for record in self.records], [True, True, True, True, False])

    def test_all_four_authorized_transmissions_are_blocked_not_attempted(self):
        self.assertEqual(self.tracker["attempted_transmissions"], 0)
        self.assertEqual(self.tracker["successful_transmissions"], 0)
        self.assertEqual(self.tracker["blocked_transmissions"], 4)
        self.assertEqual(self.tracker["failed_transmissions"], 0)
        for record in self.records[:4]:
            self.assertEqual(record["actual_send_status"], "EXECUTION_BLOCKED")
            if self.tracker.get("lifecycle_status") == "PAUSED":
                self.assertEqual(record["next_action"], "PAUSED_AWAITING_PARTICIPATION_REDESIGN")
            else:
                self.assertEqual(record["next_action"], "MANUAL_TRANSMISSION_REQUIRED")
            self.assertTrue(record["execution_block_reason"])
            self.assertIsNone(record["confirmation_reference"])

    def test_no_message_sent_and_no_response_window_started(self):
        self.assertEqual(self.tracker["messages_sent"], 0)
        self.assertIsNone(self.tracker["first_reality_boundary_t0"])
        for record in self.records:
            self.assertIsNone(record["sent_at"])
            self.assertIsNone(record["send_timestamp"])
        for record in self.records[:4]:
            self.assertIsNone(record["response_window_end"])
            self.assertEqual(record["current_participation_status"], "OUTREACH_PREPARED")

    def test_event_log_is_append_only_and_contains_only_real_events(self):
        expected_count = 9 if self.tracker.get("lifecycle_status") == "PAUSED" else 8
        self.assertEqual(len(self.events), expected_count)
        ids = [event["outreach_event_id"] for event in self.events]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(event["append_only"] for event in self.events))
        self.assertEqual([event["event_type"] for event in self.events[:4]], ["OUTREACH_EXECUTION_AUTHORIZED"] * 4)
        self.assertEqual([event["event_type"] for event in self.events[4:8]], ["OUTREACH_EXECUTION_BLOCKED"] * 4)
        if self.tracker.get("lifecycle_status") == "PAUSED":
            self.assertEqual(self.events[8]["event_type"], "EXPERIMENT_PAUSED")
            self.assertFalse(self.events[8]["send_authorized"])
        self.assertFalse({event["event_type"] for event in self.events} & FORBIDDEN_EVENT_TYPES)

    def test_block_events_have_complete_unsent_execution_records(self):
        for event, candidate_id, claims in zip(self.events[4:8], AUTHORIZED_IDS, EXPECTED_CLAIM_SETS):
            self.assertEqual(event["candidate_id"], candidate_id)
            self.assertTrue(event["channel"].startswith("OFFICIAL_"))
            self.assertTrue(event["destination_reference"])
            self.assertTrue(event["official_route_source"].startswith("https://"))
            self.assertTrue(event["message_hash"].startswith("sha256:"))
            self.assertEqual(event["claim_ids"], claims)
            self.assertIsNone(event["sent_at"])
            self.assertEqual(event["submission_result"], "EXECUTION_BLOCKED")
            self.assertIsNone(event["confirmation_reference"])
            self.assertTrue(event["confirmation_text_summary"])

    def test_trelleborg_remains_untouched_hold(self):
        held = self.records[4]
        self.assertEqual(held["candidate_id"], "OIL-CAND-005")
        self.assertEqual(held["send_approval"], "HOLD")
        self.assertFalse(held["send_authorized"])
        self.assertIsNone(held["final_recipient_or_channel"])
        self.assertIsNone(held["sent_at"])
        self.assertEqual(held["outreach_events"], [])

    def test_claim_dictionary_and_evidence_requirements_are_unchanged(self):
        self.assertEqual(hashlib.sha256(DICTIONARY_PATH.read_bytes()).hexdigest(), DICTIONARY_SHA256)
        self.assertEqual(hashlib.sha256(EVIDENCE_MATRIX_PATH.read_bytes()).hexdigest(), EVIDENCE_MATRIX_SHA256)

    def test_no_production_records_statuses_or_scores_created(self):
        for payload in (self.baseline, self.tracker, self.events):
            keys = set(walk_keys(payload))
            self.assertFalse(keys & FORBIDDEN_PRODUCTION_KEYS, keys & FORBIDDEN_PRODUCTION_KEYS)
        serialized = json.dumps([self.baseline, self.tracker, self.events])
        for status in ["SUPPORTED", "OBSERVED", "UNKNOWN", "NOT_ESTABLISHED", "CONTRADICTED"]:
            self.assertNotIn(f'"{status}"', serialized)

    def test_no_public_case_change_or_transmission_variant(self):
        completed = subprocess.run(
            ["git", "diff", "--name-only", BASE_SHA, "--", "cases", "claims", "evidence", "docs/cases", "public"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")
        self.assertEqual(list(OUTREACH_DIR.rglob("*transmission*variant*")), [])

    def test_execution_report_truthfully_records_blocked_state(self):
        report = REPORT_PATH.read_text(encoding="utf-8")
        self.assertIn("Status:** `BLOCKED — MANUAL TRANSMISSION REQUIRED`", report)
        self.assertIn("ATTEMPTED_COUNT = 0", report)
        self.assertIn("SUCCESSFUL_TRANSMISSIONS = 0", report)
        self.assertIn("BLOCKED_TRANSMISSIONS = 4", report)
        self.assertIn("FIRST_REALITY_BOUNDARY_T0 = null", report)
        self.assertIn("12/12 PASS", report)
        self.assertIn("NEXT_GATE = STAGE_3_MANUAL_TRANSMISSION_REQUIRED", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
