#!/usr/bin/env python3
"""Repository protections for SE-GTM-005 FDE experiment v0.2."""

from __future__ import annotations

import csv
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops/growth/SE_GTM_005/fde-v0.2"
REQUIRED = {
    "FDE_MARKET_REALITY_REPORT.md",
    "GTM005_FDE_CANDIDATES.csv",
    "FDE_BUYER_RELATIONSHIP_MATRIX.md",
    "EVIDENCE_BLOCKER_CLASSIFICATION.jsonl",
    "FDE_DECISION_CLEARANCE_PACK_v0.1.md",
    "REUSABLE_EVIDENCE_ASSESSMENT.md",
    "FDE_VERIFICATION_COST_BASELINE.md",
    "COMPETITOR_AND_SUBSTITUTE_ASSESSMENT.md",
    "HUMAN_REVIEW_QUEUE.md",
    "GTM005_V0_2_FINAL_REPORT.md",
}
ALLOWED_CLASSIFICATIONS = {
    "RESEARCH",
    "FIT_HYPOTHESIS",
    "BUYER_PROBLEM_CONFIRMED",
    "PAID_INTENT_CONFIRMED",
    "HOLD",
    "REJECT",
}
ALLOWED_BLOCKERS = {
    "EVIDENCE_RESOLVABLE",
    "TECHNICAL_EXECUTION",
    "COMMERCIAL_BUDGET",
    "ORGANIZATIONAL_APPROVAL",
    "PROCUREMENT_PROCESS",
    "UNKNOWN",
}


class Segtm005V02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with (BASE / "GTM005_FDE_CANDIDATES.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            cls.candidates = list(csv.DictReader(handle))
        cls.blockers = [
            json.loads(line)
            for line in (BASE / "EVIDENCE_BLOCKER_CLASSIFICATION.jsonl")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]

    def test_exact_required_deliverables(self):
        self.assertEqual(REQUIRED, {path.name for path in BASE.iterdir() if path.is_file()})

    def test_eleven_unique_group_b_candidates(self):
        self.assertEqual(11, len(self.candidates))
        self.assertEqual(11, len({row["candidate_id"] for row in self.candidates}))
        self.assertTrue(all(row["fde_service_verified"] == "YES" for row in self.candidates))
        self.assertTrue(all(row["identity_status"] for row in self.candidates))
        self.assertTrue(all(row["verified_contact_route"] for row in self.candidates))

    def test_candidate_states_do_not_overclaim_demand(self):
        self.assertTrue(
            all(row["classification"] in ALLOWED_CLASSIFICATIONS for row in self.candidates)
        )
        self.assertTrue(all(row["buyer_problem_confirmed"] == "NO" for row in self.candidates))
        self.assertTrue(all(row["paid_intent_confirmed"] == "NO" for row in self.candidates))
        self.assertNotIn(
            "BUYER_PROBLEM_CONFIRMED", {row["classification"] for row in self.candidates}
        )
        self.assertNotIn(
            "PAID_INTENT_CONFIRMED", {row["classification"] for row in self.candidates}
        )

    def test_blocker_gate_is_complete_and_unconfirmed(self):
        self.assertEqual(11, len(self.blockers))
        self.assertEqual(
            {row["candidate_id"] for row in self.candidates},
            {row["candidate_id"] for row in self.blockers},
        )
        for row in self.blockers:
            self.assertTrue(set(row["blocker_labels"]).issubset(ALLOWED_BLOCKERS))
            self.assertTrue(row["identifiable_claim"])
            self.assertTrue(row["beneficiary_or_role"])
            self.assertTrue(row["plausible_evidence_deliverable"])
            self.assertTrue(row["observable_insufficiency"])
            self.assertTrue(row["contradiction_or_substitute"])
            self.assertFalse(row["buyer_problem_confirmed"])

    def test_demo_is_explicitly_synthetic_and_nonproduction(self):
        demo = (BASE / "FDE_DECISION_CLEARANCE_PACK_v0.1.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("STATUS = `SYNTHETIC_DEMONSTRATION`", demo)
        self.assertIn("PRODUCTION_USE = `PROHIBITED`", demo)
        self.assertIn("CERTIFICATION_OR_SECURITY_APPROVAL = `NOT_PROVIDED`", demo)
        self.assertIn("No test has been run", demo)

    def test_cost_reduction_is_modeled_not_observed(self):
        cost = (BASE / "FDE_VERIFICATION_COST_BASELINE.md").read_text(encoding="utf-8")
        self.assertIn("OBSERVED_COST_REDUCTION = `NOT_ESTABLISHED`", cost)
        self.assertIn("MODELED_COST_REDUCTION_BASE = `$3,560_PER_ACCEPTANCE_CYCLE`", cost)
        self.assertIn("MODELED_PERCENT_REDUCTION_BASE = `25.7%`", cost)
        self.assertIn("Do not claim CAC reduction", cost)

    def test_exactly_three_drafts_and_no_send_authorization(self):
        queue = (BASE / "HUMAN_REVIEW_QUEUE.md").read_text(encoding="utf-8")
        self.assertEqual(3, len(re.findall(r"```text\n.*?\n```", queue, re.DOTALL)))
        self.assertIn("OUTREACH_AUTHORIZED = `NO`", queue)
        self.assertIn("OUTREACH_SENT = `0`", queue)
        self.assertNotIn("OUTREACH_AUTHORIZED = `YES`", queue)

    def test_existing_baselines_are_explicitly_preserved(self):
        report = (BASE / "GTM005_V0_2_FINAL_REPORT.md").read_text(encoding="utf-8")
        self.assertIn("SE-GTM-002 v0.4 was not modified", report)
        self.assertIn("SE-AI-DATA-001 task, Gold and provenance files were not modified", report)
        self.assertIn("TRUST_BOUNDARY_30D_001 was not modified", report)
        self.assertIn("PRODUCTION_CHANGED = `NO`", report)
        self.assertIn("OUTREACH_SENT = `0`", report)

    def test_group_a_is_preserved_without_new_search(self):
        matrix = (BASE / "FDE_BUYER_RELATIONSHIP_MATRIX.md").read_text(encoding="utf-8")
        self.assertIn("GROUP_A_INDUSTRIAL_SUPPLIERS = `PRESERVED_NO_NEW_SEARCH`", matrix)
        for supplier in (
            "Sodion Energy",
            "Badar Energy",
            "Alfotech",
            "KUNETIC",
            "Bestrings Sealing Solutions",
        ):
            self.assertIn(supplier, matrix)


if __name__ == "__main__":
    unittest.main()
