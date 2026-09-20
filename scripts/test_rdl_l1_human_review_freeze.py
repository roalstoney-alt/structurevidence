#!/usr/bin/env python3
"""Tests for the L0 human review freeze of the first controlled L1."""

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORD_DIR = ROOT / "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20"
FREEZE_PATH = RECORD_DIR / "human-review-freeze.json"
CAPITAL_PATH = RECORD_DIR / "research-capital-observation.json"
EVIDENCE_PATH = RECORD_DIR / "field-deployment-evidence.json"
RECORD_PATH = RECORD_DIR / "research-record.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class L1HumanReviewFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze = load(FREEZE_PATH)
        cls.capital = load(CAPITAL_PATH)
        cls.evidence = load(EVIDENCE_PATH)
        cls.record = load(RECORD_PATH)

    def test_a_human_acceptance_and_scope(self):
        decision = self.freeze["human_cml_decision"]
        self.assertEqual(decision["review"], "ACCEPT")
        self.assertEqual(decision["r5_scope"], "ARCHITECTURE_FIELD_DEPLOYED_SINGLE_DEPLOYMENT_EVIDENCE")
        self.assertFalse(decision["pdre_full_validation"])
        self.assertEqual(self.freeze["codex_research_result"]["result"], "QUALIFYING_FIELD_DEPLOYMENT_EVIDENCE_FOUND")

    def test_b_qualifying_evidence_and_provenance_preserved(self):
        self.assertEqual(self.freeze["codex_research_result"]["evidence_id"], "L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001")
        self.assertEqual(self.evidence["evidence"]["evidence_id"], "L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001")
        self.assertEqual(self.evidence["evidence"]["source_class"], "NAMED_DATA_CENTER_OPERATOR_PRIMARY_PUBLICATION")
        self.assertEqual(self.evidence["core"]["verification_status"], "HUMAN_CML_REVIEW_ACCEPTED_SINGLE_INSTANCE")

    def test_c_time_semantics_are_preserved(self):
        timing = self.freeze["time_semantics"]
        self.assertEqual(timing["event_time"], "2026-07-02")
        self.assertEqual(timing["knowledge_time"], "2026-09-20T10:46:47Z")
        self.assertFalse(timing["event_time_equals_knowledge_time"])

    def test_d_credit_observation_is_raw_and_exact(self):
        self.assertEqual(self.capital["credit_balance_before"], 384)
        self.assertEqual(self.capital["credit_balance_after"], 347)
        self.assertEqual(self.capital["account_credit_delta"], 37)
        self.assertEqual(self.capital["measurement_status"], "OBSERVED")
        self.assertEqual(self.capital["measurement_source"], "HUMAN_CHATGPT_USAGE_SCREENSHOTS")
        self.assertEqual(self.capital["attribution_confidence"], "HIGH")
        self.assertFalse(self.capital["currency_conversion_performed"])
        self.assertEqual(self.capital["usd_cost"], "UNKNOWN")
        self.assertEqual(self.capital["model_calls"], "UNKNOWN")
        self.assertEqual(self.capital["token_usage"], "UNKNOWN")
        self.assertEqual(self.capital["scores_calculated"], [])

    def test_e_raw_research_capital_observations(self):
        expected = {
            "authorized_query_budget": 8,
            "queries_used": 4,
            "authorized_deep_review_budget": 5,
            "deep_reviews_used": 1,
            "sources_checked": 9,
            "sources_used": 1,
            "sources_rejected": 8,
            "duplicates": 0,
            "qualifying_evidence": 1,
            "counter_evidence": 2,
            "new_evidence_count": 1,
            "unknowns_resolved": 1,
            "unknowns_remaining": 5,
            "reusable_assets_created": 3,
        }
        self.assertEqual({key: self.capital[key] for key in expected}, expected)

    def test_f_remaining_unknowns_are_not_negative_evidence(self):
        remaining = self.freeze["remaining_uncertainty"]
        self.assertEqual(remaining["operating_history"], "UNKNOWN")
        self.assertEqual(remaining["multi_entity_replication"], "UNKNOWN")
        self.assertEqual(remaining["independent_third_party_validation"], "UNKNOWN")
        self.assertEqual(remaining["repeat_procurement"], "UNKNOWN")
        self.assertEqual(remaining["industry_scale_adoption"], "NOT_ESTABLISHED")
        self.assertEqual(remaining["pdre_status"], "NOT_FULLY_VALIDATED")
        self.assertFalse(remaining["automatic_research_tasks_created"])

    def test_g_canonical_transition_waits_for_existing_governance(self):
        boundary = self.freeze["cml_boundary"]
        self.assertFalse(boundary["canonical_readiness_changed"])
        self.assertFalse(boundary["canonical_case_files_modified"])
        self.assertEqual(boundary["transition_status"], "CML_TRANSITION_PENDING_EXISTING_GOVERNANCE")
        changed = subprocess.check_output(
            ["git", "diff", "--name-only", "HEAD", "--", "technical-risk/cml-v1.1/pdre/CML-PDRE-001"],
            cwd=ROOT,
            text=True,
        ).splitlines()
        self.assertEqual(changed, [])

    def test_h_no_new_research_or_escalation(self):
        self.assertEqual(self.freeze["mode"], "L0_REUSE")
        self.assertFalse(self.freeze["external_research_performed"])
        self.assertFalse(self.freeze["l2_executed"])
        self.assertFalse(self.freeze["l3_executed"])
        self.assertFalse(self.freeze["phase_3_started"])
        self.assertEqual(self.freeze["next_research_authorization"], "NONE")

    def test_i_old_record_mutation_count_is_zero(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import cml_v11_regression

        self.assertEqual(cml_v11_regression.historical_mutations(), [])


if __name__ == "__main__":
    unittest.main()
