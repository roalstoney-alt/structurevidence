#!/usr/bin/env python3
"""Stage 3 boundary tests for OIL-GENESIS-001 controlled evidence requests."""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DICTIONARY_PATH = ROOT / "data/open-intent-lab/genesis-001/claim-dictionary.json"
MATRIX_PATH = ROOT / "data/open-intent-lab/genesis-001/evidence-request-matrix.json"
OUTREACH_DIR = ROOT / "data/open-intent-lab/genesis-001/outreach"
TRACKER_PATH = OUTREACH_DIR / "outreach-tracker.json"
GLOBAL_DOC_PATH = (
    ROOT / "docs/open-intent-lab/genesis/OIL_GENESIS_001_EVIDENCE_REQUEST_MATRIX.md"
)
REPORT_PATH = ROOT / "docs/open-intent-lab/execution/STAGE_03_REPORT.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"

EXPECTED_CLAIMS = [f"OIL-CAP-SIL-{index:03d}" for index in range(1, 8)]
EXPECTED_COUNTS = [7, 7, 6, 5, 5]
EXPECTED_PACK_FILES = {
    "supplier_invitation.md",
    "claim_evidence_request.md",
    "claim_evidence_matrix.md",
    "evidence_submission_checklist.md",
    "evidence_visibility_consent.md",
    "historical_record_notice.md",
}
EXPECTED_VISIBILITY = ["PUBLIC", "AUTHORIZED_BUYER", "TRANSACTION_PRIVATE"]
EXPECTED_RESPONSES = [
    "EVIDENCE_ATTACHED",
    "PUBLIC_REFERENCE_PROVIDED",
    "CLAIM_SCOPE_CORRECTION",
    "CLAIM_WITHDRAWN",
    "EVIDENCE_UNAVAILABLE",
    "CONFIDENTIAL_ONLY",
    "NOT_APPLICABLE",
]
EXPECTED_PARTICIPATION = [
    "PENDING_OUTREACH",
    "OUTREACH_PREPARED",
    "OUTREACH_SENT",
    "RESPONDED",
    "EVIDENCE_SUBMITTED",
    "NO_RESPONSE",
    "REFUSED_EVIDENCE",
    "REFUSED_ANY_VISIBILITY",
    "TOO_BUSY",
    "NOT_THIS_CAPABILITY",
    "WITHDRAWN",
]
EXPECTED_CONSISTENCY = [
    "CONFIRMS",
    "CONSISTENT_WITH",
    "PARTIALLY_CONSISTENT",
    "CONTRADICTS",
    "SUPERSEDES_SCOPE",
    "NOT_COMPARABLE",
]
EXPECTED_DISCLOSURE = [
    "MATERIAL_FACT_NEWLY_DISCLOSED",
    "MATERIAL_SCOPE_CLARIFIED",
    "MATERIAL_SCOPE_RESTRICTED",
    "MATERIAL_CLAIM_CONTRADICTED",
    "MATERIAL_OUTCOME_DEVIATION",
    "EVIDENCE_UPDATED",
    "EVIDENCE_WITHDRAWN_BY_SOURCE",
]
FORBIDDEN_OPERATIONAL_KEYS = {
    "provider_id",
    "demand_id",
    "outcome_id",
    "reuse_record_id",
    "verified_capability_fact_id",
    "verified_capability_facts",
    "capability_status",
    "ranking",
    "rank",
    "score",
    "confidence_score",
}
DEFERRED_OR_REMOVED_TERMS = {
    "ID 6 mm",
    "OD 12 mm",
    "25 m continuous",
    "2007/19/EC",
    "AS 2069",
}
PROHIBITED_PROMOTIONAL_PHRASES = {
    "join our marketplace",
    "become certified",
    "get buyer leads",
    "get ranked",
    "premium exposure",
    "supplier rating =",
    "trust score =",
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


class StageThreeEvidenceRequestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dictionary = load_json(DICTIONARY_PATH)
        cls.matrix = load_json(MATRIX_PATH)
        cls.tracker = load_json(TRACKER_PATH)
        cls.requirements = cls.matrix["claim_evidence_requirements"]
        cls.pack_dirs = sorted(path for path in OUTREACH_DIR.glob("candidate-*") if path.is_dir())

    def test_all_and_only_frozen_claims_have_requirements(self):
        dictionary_ids = [claim["claim_id"] for claim in self.dictionary["claims"]]
        request_ids = [row["claim_id"] for row in self.requirements]
        self.assertEqual(dictionary_ids, EXPECTED_CLAIMS)
        self.assertEqual(request_ids, EXPECTED_CLAIMS)

    def test_each_claim_has_bounded_acceptable_and_nonqualifying_rules(self):
        evidence_types = set(self.dictionary["evidence_type_enum"])
        required_stops = {
            "QUALIFYING_DOCUMENT",
            "TWO_INDEPENDENT_SOURCES",
            "INSUFFICIENT_EVIDENCE",
            "MAX_VERIFICATION_TIME",
        }
        for row in self.requirements:
            self.assertTrue(row["acceptable_evidence_types"])
            self.assertLessEqual(set(row["acceptable_evidence_types"]), evidence_types)
            self.assertTrue(row["minimum_required_scope"])
            self.assertTrue(row["required_identifiers"])
            self.assertTrue(row["non_qualifying_evidence"])
            self.assertEqual(set(row["verification_stop_condition"]["any_of"]), required_stops)
            self.assertEqual(row["verification_stop_condition"]["maximum_human_hours"], 4)
            self.assertEqual(row["visibility_options"], EXPECTED_VISIBILITY)

    def test_supplier_statement_cannot_assign_capability_status(self):
        rule = self.matrix["supplier_statement_rule"]
        self.assertFalse(rule["supplier_statement_alone_qualifies"])
        self.assertFalse(rule["may_assign_capability_status"])
        self.assertEqual(rule["may_establish"], ["CLAIM_ORIGIN", "SOURCE_ATTRIBUTION"])
        self.assertIn("issuer", rule["formal_manufacturer_declaration_rule"])
        self.assertIn("accountable source", rule["formal_manufacturer_declaration_rule"])

    def test_deferred_and_removed_claims_are_not_reintroduced(self):
        serialized = json.dumps(self.matrix, ensure_ascii=False)
        for term in DEFERRED_OR_REMOVED_TERMS:
            self.assertNotIn(term, serialized)

    def test_controlled_vocabularies_are_exact(self):
        self.assertEqual(self.matrix["visibility_enum"], EXPECTED_VISIBILITY)
        self.assertEqual(self.matrix["supplier_response_options"], EXPECTED_RESPONSES)
        self.assertEqual(self.matrix["participation_status_codes"], EXPECTED_PARTICIPATION)
        self.assertEqual(self.matrix["consistency_relation_vocabulary"], EXPECTED_CONSISTENCY)
        self.assertEqual(self.matrix["disclosure_event_vocabulary"], EXPECTED_DISCLOSURE)

    def test_exactly_five_complete_supplier_packs_exist(self):
        self.assertEqual([path.name for path in self.pack_dirs], [f"candidate-{i:03d}" for i in range(1, 6)])
        for pack_dir in self.pack_dirs:
            actual_files = {path.name for path in pack_dir.iterdir() if path.is_file()}
            self.assertLessEqual(EXPECTED_PACK_FILES, actual_files)
            self.assertLessEqual(actual_files - EXPECTED_PACK_FILES, {"final_outreach_message.md"})

    def test_claims_requested_per_supplier_are_7_7_6_5_5(self):
        records = self.tracker["records"]
        self.assertEqual([len(row["claims_requested"]) for row in records], EXPECTED_COUNTS)
        for record, expected_count in zip(records, EXPECTED_COUNTS):
            self.assertEqual(record["claims_requested"], EXPECTED_CLAIMS[:expected_count])
            pack_number = record["candidate_id"].split("-")[-1]
            matrix_text = (OUTREACH_DIR / f"candidate-{pack_number}" / "claim_evidence_matrix.md").read_text(encoding="utf-8")
            ids = sorted(set(re.findall(r"OIL-CAP-SIL-\d{3}", matrix_text)))
            self.assertEqual(ids, EXPECTED_CLAIMS[:expected_count])

    def test_invitations_are_drafts_without_ranking_or_promotion(self):
        for pack_dir in self.pack_dirs:
            invitation = (pack_dir / "supplier_invitation.md").read_text(encoding="utf-8")
            lowered = invitation.lower()
            self.assertIn("not sent", lowered)
            self.assertIn("human review", lowered)
            self.assertIn("10 business days", lowered)
            self.assertIn("does not certify suppliers", lowered)
            for phrase in PROHIBITED_PROMOTIONAL_PHRASES:
                self.assertNotIn(phrase, lowered)

    def test_outreach_tracker_is_fail_closed_and_unsent(self):
        self.assertEqual(self.tracker["messages_sent"], 0)
        self.assertEqual(len(self.tracker["records"]), 5)
        if self.tracker["stage"] == "STAGE_3_FINAL_OUTREACH_EXECUTION":
            self.assertTrue(self.tracker["send_authorized"])
            self.assertEqual([record["send_authorized"] for record in self.tracker["records"]], [True, True, True, True, False])
        else:
            self.assertFalse(self.tracker["send_authorized"])
            self.assertTrue(all(not record["send_authorized"] for record in self.tracker["records"]))
        for record in self.tracker["records"]:
            self.assertIsNone(record["sent_at"])
            self.assertIsNone(record["last_response_at"])
            self.assertIn(record["human_review_status"], {"PENDING", "DECIDED"})
            self.assertEqual(record["response_status"], "OUTREACH_PREPARED")
            self.assertIn(
                record["next_action"],
                {
                    "HUMAN_REVIEW",
                    "FINAL_OUTREACH_EXECUTION",
                    "MANUAL_TRANSMISSION_REQUIRED",
                    "RESOLVE_HOLD_ATTRIBUTION",
                    "PAUSED_AWAITING_PARTICIPATION_REDESIGN",
                    "PAUSED_HOLD_ATTRIBUTION",
                },
            )

    def test_no_production_records_statuses_scores_or_live_events_exist(self):
        for payload in (self.matrix, self.tracker):
            keys = set(walk_keys(payload))
            self.assertFalse(keys & FORBIDDEN_OPERATIONAL_KEYS, keys & FORBIDDEN_OPERATIONAL_KEYS)
        self.assertIn("No live relation is created", self.matrix["consistency_relation_rule"])
        self.assertIn("No live disclosure event is created", self.matrix["disclosure_event_rule"])

    def test_required_documents_and_report_exist(self):
        document = GLOBAL_DOC_PATH.read_text(encoding="utf-8")
        report = REPORT_PATH.read_text(encoding="utf-8")
        for section in [
            "Operating principle",
            "Shared scope rule",
            "Shared verification stop rule",
            "Claim matrix",
            "Visibility consent model",
            "Supplier response options",
            "Historical record notice",
            "Consistency relation vocabulary — prepared only",
            "Disclosure event vocabulary — prepared only",
            "Stage boundary",
        ]:
            self.assertIn(f"## {section}", document)
        self.assertIn("12/12 PASS", report)
        self.assertIn("SEND_AUTHORIZED = NO", report)
        self.assertIn("MESSAGES_SENT = 0", report)

    def test_no_public_case_changes_from_authoritative_base(self):
        completed = subprocess.run(
            [
                "git",
                "diff",
                "--name-only",
                BASE_SHA,
                "--",
                "cases",
                "claims",
                "evidence",
                "docs/cases",
                "public",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
