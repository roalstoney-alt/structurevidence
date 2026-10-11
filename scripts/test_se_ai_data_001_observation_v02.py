#!/usr/bin/env python3
"""Protection tests for SE-AI-DATA-001 continuous observation v0.2."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops/growth/SE_AI_DATA_001/continuous-observation-v0.2"
SAMPLE = ROOT / "ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE"
ALLOWED_OBSERVATION_STATUSES = {
    "NO_MATERIAL_CHANGE",
    "NEW_EVIDENCE_OBSERVED",
    "EVIDENCE_CONFLICT",
    "SOURCE_UNAVAILABLE",
    "INTERPRETATION_REVIEW_REQUIRED",
}


class ContinuousObservationV02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.observations = [
            json.loads(line)
            for line in (BASE / "TASK_OBSERVATION_LEDGER.jsonl").read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

    def test_all_required_deliverables_exist(self):
        required = {
            "TASK_OBSERVATION_LEDGER.jsonl",
            "WEEKLY_EVIDENCE_REPORT.md",
            "X_DRAFTS_FOR_REVIEW.md",
            "ZHIHU_DRAFT_FOR_REVIEW.md",
            "AUDIENCE_DEMAND_LEDGER.csv",
            "RIGHTS_AND_PUBLICATION_GATE.md",
            "WEEKLY_RESEARCH_SUMMARY.md",
        }
        self.assertEqual(required, {path.name for path in BASE.iterdir() if path.is_file()})

    def test_exactly_eight_tasks_and_controlled_statuses(self):
        self.assertEqual(8, len(self.observations))
        self.assertEqual(8, len({row["task_id"] for row in self.observations}))
        self.assertTrue(
            all(row["status"] in ALLOWED_OBSERVATION_STATUSES for row in self.observations)
        )

    def test_expected_bounded_observation_results(self):
        by_task = {row["task_id"]: row for row in self.observations}
        for number in range(1, 7):
            self.assertEqual(
                "NO_MATERIAL_CHANGE", by_task[f"SE-TECP-{number:03d}"]["status"]
            )
        for number in (7, 8):
            row = by_task[f"SE-TECP-{number:03d}"]
            self.assertEqual("NEW_EVIDENCE_OBSERVED", row["status"])
            self.assertEqual("NOT_ESTABLISHED", row["historical_gold_state"])
            self.assertEqual("NOT_ESTABLISHED", row["latest_interpretation"])

    def test_time_dimensions_and_negative_results_are_explicit(self):
        for row in self.observations:
            self.assertTrue(row["observed_at"])
            self.assertTrue(row["event_time"])
            self.assertTrue(row["public_disclosure_time"])
            self.assertIn("search_boundary", row)
            self.assertFalse(row["gold_overwritten"])

    def test_append_only_assessment_does_not_overwrite_history(self):
        assessment = json.loads(
            (BASE / "assessments/SE-IRK-LAB-001_v0.2.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("APPEND_ONLY_POST_CUTOFF_OBSERVATION", assessment["assessment_type"])
        self.assertFalse(assessment["gold_labels_overwritten"])
        self.assertFalse(assessment["original_task_definitions_changed"])

    def test_exactly_two_x_drafts_within_platform_limit(self):
        drafts = (BASE / "X_DRAFTS_FOR_REVIEW.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```text\n(.*?)\n```", drafts, flags=re.DOTALL)
        self.assertEqual(2, len(blocks))
        for block in blocks:
            self.assertLessEqual(len(block), 280, block)
            self.assertIn("Cutoff:", block)
            self.assertIn("Established:", block)
            self.assertTrue(block.endswith("?"))

    def test_audience_demand_ledger_has_no_fabricated_entries(self):
        with (BASE / "AUDIENCE_DEMAND_LEDGER.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual([], rows)

    def test_publication_and_dataset_release_remain_blocked(self):
        gate = (BASE / "RIGHTS_AND_PUBLICATION_GATE.md").read_text(encoding="utf-8")
        self.assertIn("AUTO_PUBLISH_X = `NO`", gate)
        self.assertIn("AUTO_PUBLISH_ZHIHU = `NO`", gate)
        self.assertIn(
            "DATASET_PUBLICATION = `PROHIBITED_WITHOUT_SEPARATE_AUTHORIZATION`", gate
        )
        self.assertIn("OUTREACH_AUTHORIZED = `NO`", gate)

    def test_no_publication_or_feedback_is_claimed(self):
        summary = (BASE / "WEEKLY_RESEARCH_SUMMARY.md").read_text(encoding="utf-8")
        self.assertIn("PUBLICATIONS_MADE = `0`", summary)
        self.assertIn("SUBSTANTIVE_FEEDBACK_ENTRIES = `0`", summary)
        self.assertIn("OUTREACH_SENT = `0`", summary)
        self.assertNotIn("PUBLICATIONS_MADE = `1`", summary)

    def test_frozen_sample_integrity_still_passes(self):
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
