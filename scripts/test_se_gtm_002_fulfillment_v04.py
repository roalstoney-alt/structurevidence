#!/usr/bin/env python3
"""Boundary and evidence-ledger checks for SE-GTM-002 fulfillment study v0.4."""

import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops" / "growth" / "SE_GTM_002"
STUDY = BASE / "fulfillment-v0.4"
BASE_COMMIT = "eac2258c5cad63ba99f9bcf6e3ef53e1839137d2"


def ledger():
    result = []
    for number, line in enumerate(
        (STUDY / "PROCUREMENT_EVIDENCE_LEDGER.jsonl").read_text().splitlines(), 1
    ):
        if line.strip():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise AssertionError(f"invalid JSONL line {number}: {error}") from error
    return result


class FulfillmentV04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = ledger()
        cls.path_report = (STUDY / "FULFILLMENT_PATH_GODADDY.md").read_text()
        cls.gap_report = (STUDY / "SERVICE_GAP_ASSESSMENT.md").read_text()
        cls.next_decision = (STUDY / "NEXT_DECISION.md").read_text()

    def test_required_deliverables(self):
        expected = {
            "FULFILLMENT_PATH_GODADDY.md",
            "PROCUREMENT_EVIDENCE_LEDGER.jsonl",
            "SERVICE_GAP_ASSESSMENT.md",
            "NEXT_DECISION.md",
        }
        self.assertEqual({path.name for path in STUDY.iterdir()}, expected)

    def test_ledger_identity_and_append_only_state(self):
        ids = [record["ledger_id"] for record in self.records]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(self.records), 18)
        self.assertTrue(all(record["preserves_prior_state"] for record in self.records))

    def test_query_limit_is_exact_and_no_open_procurement_was_inferred(self):
        queries = [record for record in self.records if record["entry_type"] == "QUERY"]
        self.assertEqual(len(queries), 8)
        self.assertTrue(all(not record["provider_named"] for record in queries))
        self.assertTrue(all(not record["open_procurement_found"] for record in queries))

    def test_required_state_determinations(self):
        expected = {
            "LEGAL_OBLIGATION_CONFIRMED = `YES`",
            "PROVIDER_IDENTIFIED = `NO`",
            "PROCUREMENT_OPEN_CONFIRMED = `NO`",
            "SERVICE_GAP_CONFIRMED = `NO`",
            "BUYER_CONFIRMED = `NO`",
        }
        for statement in expected:
            self.assertIn(statement, self.path_report)
        self.assertIn("CONCLUSION = `NO_PUBLIC_PROCUREMENT_EVIDENCE`", self.path_report)

    def test_nonfinding_is_bounded(self):
        entry = next(
            record for record in self.records if record["entry_type"] == "SEARCH_NONFINDING"
        )
        self.assertIn("NO_PUBLIC_PROCUREMENT_EVIDENCE", entry["supports"])
        self.assertIn("NO_PROVIDER_EXISTS", entry["does_not_establish"])
        normalized = " ".join(self.path_report.split())
        self.assertIn("does not mean the assessment is unfulfilled", normalized)

    def test_ancillary_task_does_not_impersonate_assessor(self):
        self.assertIn("time-indexed evidence map", self.gap_report)
        self.assertIn("would not replace the", self.gap_report)
        self.assertIn("SERVICE_GAP_CONFIRMED = `NO`", self.gap_report)
        self.assertIn("HYPOTHESIS", self.gap_report)

    def test_human_gate_and_no_outreach(self):
        self.assertIn("STATUS = `HUMAN_REVIEW_REQUIRED`", self.next_decision)
        self.assertIn("OUTREACH_AUTHORIZED = `NO`", self.next_decision)
        self.assertIn("Do not qualify GoDaddy", self.next_decision)
        self.assertIn("STOP_AND_RETAIN_RESULT", self.next_decision)

    def test_existing_dpal_and_trust_campaign_unchanged(self):
        protected = [
            "ops/growth/TRUST_BOUNDARY_30D_001",
            "ops/growth/SE_GTM_002/dpal-v0.3",
            "ops/growth/SE_GTM_002/CDSP_SCHEMA_v0.1.json",
            "ops/growth/SE_GTM_002/records",
        ]
        changed = subprocess.run(
            ["git", "diff", "--name-only", BASE_COMMIT, "--", *protected],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        self.assertEqual(changed, "")

    def test_official_sources_are_traceable(self):
        sources = [record for record in self.records if record["entry_type"] == "SOURCE"]
        self.assertGreaterEqual(len(sources), 8)
        self.assertTrue(all(record["source_url"].startswith("https://") for record in sources))
        self.assertTrue(any("ftc.gov" in record["source_url"] for record in sources))
        self.assertTrue(any("sec.gov" in record["source_url"] for record in sources))


if __name__ == "__main__":
    unittest.main()
