#!/usr/bin/env python3
"""Regression tests for the frozen daily-watch/weekly-publication gate."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CaseWatchTest(unittest.TestCase):
    def test_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_case_watch.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_publication_is_blocked(self):
        manifest = json.loads(
            (ROOT / "publication" / "weekly" / "2026-W40-publication-manifest.json").read_text()
        )
        self.assertTrue(manifest["cases"])
        self.assertTrue(all(case["human_decision"] == "PENDING" for case in manifest["cases"]))
        self.assertFalse(any(case["publication_approved"] for case in manifest["cases"]))
        self.assertFalse(any(case["new_version"] for case in manifest["cases"]))

    def test_missing_baseline_stops_nsclc_review(self):
        weekly = json.loads((ROOT / "data" / "case-watch" / "weekly" / "2026-W40.json").read_text())
        medical = next(
            review for review in weekly["reviews"]
            if review["case_id"] == "SE-ONC-NSQNSCLC-CN-001"
        )
        self.assertEqual(medical["proposed_decision"], "RESEARCH_ESCALATION_REQUIRED")
        self.assertEqual(medical["recommended_rdl_level"], "L1_VERIFY")
        self.assertGreaterEqual(len(medical["minimum_missing_evidence"]), 4)

    def test_no_public_case_was_created(self):
        self.assertFalse((ROOT / "cases" / "nsq-nsclc-china").exists())
        self.assertFalse((ROOT / "docs" / "cases" / "nsq-nsclc-china").exists())


if __name__ == "__main__":
    unittest.main()
