#!/usr/bin/env python3
"""Repository-level invariants for SE-AI-DATA-001."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops/growth/SE_AI_DATA_001"
SAMPLE = BASE / "SE_TEMPORAL_EVAL_SAMPLE"


class BuyerValidatedDatasetPilotTest(unittest.TestCase):
    def test_required_deliverables_exist(self):
        required = [
            "MARKET_BUYER_EVIDENCE.md",
            "UNIPAT_COMPETITIVE_CAPABILITY_MATRIX.md",
            "SE_TEMPORAL_EVAL_SAMPLE",
            "DATASET_PROVENANCE_LEDGER.jsonl",
            "BUYER_FIT_CANDIDATES.csv",
            "OUTREACH_DRAFTS_FOR_REVIEW.md",
            "COST_AND_DIFFERENTIATION_REPORT.md",
            "NEXT_HUMAN_DECISION.md",
        ]
        for relative in required:
            self.assertTrue((BASE / relative).exists(), relative)

    def test_provenance_ledger_is_append_only_jsonl_shape(self):
        rows = [json.loads(line) for line in (BASE / "DATASET_PROVENANCE_LEDGER.jsonl").read_text().splitlines() if line]
        self.assertGreaterEqual(len(rows), 15)
        self.assertEqual(len(rows), len({row["ledger_id"] for row in rows}))
        self.assertTrue(all("does_not_establish" in row for row in rows))

    def test_at_most_three_buyer_candidates(self):
        with (BASE / "BUYER_FIT_CANDIDATES.csv").open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        self.assertLessEqual(len(rows), 3)
        self.assertEqual(3, len(rows))
        self.assertEqual("HOLD", rows[1]["status"])
        self.assertEqual("HOLD", rows[2]["status"])

    def test_no_outreach_or_production_authorization(self):
        corpus = "\n".join(
            (BASE / name).read_text()
            for name in [
                "MARKET_BUYER_EVIDENCE.md",
                "OUTREACH_DRAFTS_FOR_REVIEW.md",
                "NEXT_HUMAN_DECISION.md",
            ]
        )
        self.assertIn("OUTREACH_AUTHORIZED = `NO`", corpus)
        self.assertIn("DRAFT_ONLY_DO_NOT_SEND", corpus)
        self.assertNotIn("OUTREACH_AUTHORIZED = `YES`", corpus)

    def test_order_amount_conflict_is_preserved(self):
        report = (BASE / "MARKET_BUYER_EVIDENCE.md").read_text()
        self.assertIn("UNIPAT_ORDER_AMOUNT_STATE = REPORTED_NOT_COMPANY_CONFIRMED", report)
        self.assertIn("attributes approximately USD 30 million of orders to\nHumanlaya", report)
        self.assertIn("Neither amount is treated as audited\nrevenue", report)

    def test_rights_and_buyer_validation_are_not_overclaimed(self):
        report = (BASE / "COST_AND_DIFFERENTIATION_REPORT.md").read_text()
        self.assertIn("EXTERNAL_DISTRIBUTION_RIGHTS = NEEDS_OWNER_CONFIRMATION", report)
        self.assertIn("BUYER_VALIDATED = NO", report)
        self.assertIn("PAID_PILOT_SUPPORTED = NO", report)

    def test_sample_validation_suite(self):
        completed = subprocess.run(
            [sys.executable, "-B", str(SAMPLE / "test_sample.py")],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
