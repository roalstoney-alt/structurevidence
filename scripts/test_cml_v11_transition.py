#!/usr/bin/env python3
"""Targeted history and integrity tests for CML v1.1 Task V11-1."""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = "a1bb8e442316c48acb0af2aca0c8c269b00340af"
V11_1_SHA = "2baced87c4df494fbbe706b4e73029d767050779"
HISTORY_PATH = "technical-risk/CML_VERSION_HISTORY.jsonl"
ALLOWED_CHANGED = {
    HISTORY_PATH,
    "technical-risk/cml-method-registry.json",
    "technical-risk/cml-v1.1/METHOD_TRANSITION.json",
    "technical-risk/cml-v1.1/history/HISTORICAL_BRANCH_FREEZE.json",
    "docs/architecture/CML_V1_1_ARCHITECTURE.md",
    "scripts/test_cml_v11_transition.py",
}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True)


class CMLV11TransitionTests(unittest.TestCase):
    def test_base_is_ancestor_and_head_matches_origin(self):
        head = git("rev-parse", "HEAD").strip()
        self.assertEqual(head, git("rev-parse", "origin/main").strip())
        subprocess.check_call(["git", "merge-base", "--is-ancestor", BASE_SHA, head], cwd=ROOT)

    def test_method_registry_has_one_active_method(self):
        registry = load("technical-risk/cml-method-registry.json")
        self.assertEqual(registry["active_method"]["method_version"], "CML_v1.1")
        historical = registry["historical_methods"]
        self.assertEqual(len(historical), 5)
        self.assertTrue(all(row["status"] == "HISTORICAL_METHOD_BRANCH" for row in historical))
        c0 = next(row for row in historical if row["method_version"] == "CML_OV_v0.1_PHASE_C0")
        self.assertEqual(c0["primary_research_gate_status"], "DEPRECATED_AS_PRIMARY_RESEARCH_GATE")

    def test_transition_does_not_change_findings_or_history(self):
        transition = load("technical-risk/cml-v1.1/METHOD_TRANSITION.json")
        self.assertEqual(transition["to_method"], "CML_v1.1")
        self.assertFalse(transition["scientific_findings_changed"])
        self.assertFalse(transition["historical_records_rewritten"])
        self.assertEqual(transition["authorization"]["task"], "V11-1_METHOD_TRANSITION")

    def test_version_history_is_prefix_preserving_append_only(self):
        prior = git("show", f"{BASE_SHA}:{HISTORY_PATH}").splitlines()
        current = (ROOT / HISTORY_PATH).read_text(encoding="utf-8").splitlines()
        self.assertEqual(current[: len(prior)], prior)
        self.assertEqual(len(current), len(prior) + 1)
        entry = json.loads(current[-1])
        self.assertEqual(entry["change_type"], "METHOD_TRANSITION")
        self.assertEqual(entry["method_version"], "CML_v1.1")
        self.assertFalse(entry["scientific_findings_changed"])
        self.assertFalse(entry["historical_records_rewritten"])

    def test_no_historical_tracked_file_mutation(self):
        changed = set(git("diff", "--name-only", BASE_SHA, "--").splitlines())
        self.assertEqual(changed - ALLOWED_CHANGED, set())
        self.assertEqual(changed & ALLOWED_CHANGED, ALLOWED_CHANGED)

    def test_historical_freeze_covers_all_branches(self):
        freeze = load("technical-risk/cml-v1.1/history/HISTORICAL_BRANCH_FREEZE.json")
        self.assertEqual(freeze["base_sha"], BASE_SHA)
        self.assertEqual(len(freeze["branches"]), 5)
        self.assertTrue(all(row["status"] == "HISTORICAL_METHOD_BRANCH" for row in freeze["branches"]))

    def test_c0_framework_is_preserved(self):
        required = [
            "technical-risk/opportunity-validation/PHASE_C0_STATUS_VOCABULARY.json",
            "technical-risk/opportunity-validation/schema/phase-c0-response.schema.json",
            "technical-risk/opportunity-validation/templates/phase-c0-response.json",
            "scripts/validate_cml_ov_phase_c0.py",
            "scripts/test_cml_ov_phase_c0.py",
        ]
        for path in required:
            self.assertTrue((ROOT / path).is_file(), path)
            self.assertEqual(git("diff", "--name-only", BASE_SHA, "--", path), "")

    def test_architecture_reuses_evidence_core_and_keeps_separations(self):
        text = (ROOT / "docs/architecture/CML_V1_1_ARCHITECTURE.md").read_text(encoding="utf-8")
        for phrase in [
            "reuses the existing Evidence Core envelope",
            "Structural exposure identifies",
            "beneficiary map identifies",
            "Migration readiness and adoption friction are likewise independent",
            "No opaque aggregate opportunity or risk score",
        ]:
            self.assertIn(phrase, text)

    def test_v11_1_did_not_create_research_schemas(self):
        tree = git("ls-tree", "-r", "--name-only", V11_1_SHA, "--", "technical-risk/cml-v1.1/schema")
        self.assertEqual(tree, "")


if __name__ == "__main__":
    unittest.main()
