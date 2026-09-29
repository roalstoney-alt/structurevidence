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

    def test_current_nsclc_baseline_supports_no_change(self):
        weekly = json.loads((ROOT / "data" / "case-watch" / "weekly" / "2026-W40.json").read_text())
        medical = next(
            review for review in weekly["reviews"]
            if review["case_id"] == "SE-ONC-NSQNSCLC-CN-001"
        )
        self.assertEqual(medical["previous_version"], "v0.1")
        self.assertEqual(medical["proposed_decision"], "NO_STATE_CHANGE")
        self.assertEqual(medical["recommended_rdl_level"], "NONE")
        self.assertEqual(medical["minimum_missing_evidence"], [])

    def test_current_nsclc_baseline_is_preexisting_and_protected(self):
        baseline = json.loads((ROOT / "data" / "case-watch" / "protected-baseline-sha256.json").read_text())
        self.assertTrue((ROOT / "cases" / "nsq-nsclc-china" / "state-v0.1.json").is_file())
        self.assertTrue((ROOT / "cases" / "nsq-nsclc-china" / "stop-v0.1.html").is_file())
        self.assertIn("cases/nsq-nsclc-china/state-v0.1.json", baseline["files"])
        self.assertIn("cases/nsq-nsclc-china/stop-v0.1.html", baseline["files"])

    def test_snapshot_primitive_gaps_remain_explicit(self):
        registry = json.loads((ROOT / "data" / "case-watch" / "case-registry.json").read_text())
        cases = {case["case_id"]: case["audit"] for case in registry["cases"]}
        self.assertEqual(cases["CML-PDRE-001"]["state_file"], "MISSING_PUBLIC_STATE_SNAPSHOT")
        self.assertEqual(cases["SE-BESS-SODIUM-001"]["publication_control"], "MISSING")
        self.assertEqual(cases["SE-ONC-NSQNSCLC-CN-001"]["publication_control"], "MISSING")


if __name__ == "__main__":
    unittest.main()
