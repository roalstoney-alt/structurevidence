#!/usr/bin/env python3
"""Validate Question-to-Evidence Commerce Protocol v0.1 boundaries."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
ENTRY_SHA = "79b21a0ded70af2a6b8bcd81ae097f81ea256357"
SCHEMAS = [
    "protocol/question-intake/schema-v0.1.json",
    "protocol/claim-match/schema-v0.1.json",
    "protocol/verification-quote/schema-v0.1.json",
    "protocol/publication-eligibility/schema-v0.1.json",
    "protocol/freshness/schema-v0.1.json",
    "protocol/applicability/schema-v0.1.json",
]
PROTECTED = ["cases", "docs/cases", "technical-risk/cml-v1.1", "rdl"]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def changed(*paths: str):
    result = subprocess.run(
        ["git", "diff", "--name-only", ENTRY_SHA, "--", *paths],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    return [line for line in result.stdout.splitlines() if line]


class QuestionEvidenceCommerceProtocolTest(unittest.TestCase):
    def test_a_six_versioned_primitive_schemas_are_valid(self):
        for relative in SCHEMAS:
            schema = load(relative)
            Draft202012Validator.check_schema(schema)
            self.assertTrue(schema["title"].endswith("v0.1"), relative)

    def test_h_method_contract_exposes_versioned_protocol(self):
        method = load("method-contract.json")
        protocol = method["question_protocol"]
        self.assertEqual(protocol["version"], "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1")
        self.assertEqual(protocol["match_classes"], ["EXACT", "ISOMORPHIC", "PARTIAL", "NONE"])
        self.assertEqual(protocol["commerce_boundary"], "PROCESS_BOUGHT_OUTCOME_NOT_BOUGHT")
        self.assertFalse(protocol["automatic_research_authorization"])

    def test_t_u_public_history_and_changes_feed_remain_append_only(self):
        self.assertEqual(changed("changes.json", "docs/changes.json"), [])
        self.assertEqual(load("changes.json")["changes"], [])

    def test_x_public_claims_and_primitives_are_byte_immutable(self):
        self.assertEqual(changed("claims", "docs/claims"), [])
        self.assertEqual(changed(*PROTECTED), [])

    def test_y_case_watch_compatibility(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_case_watch.py")],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_z_commercial_capability_and_no_auto_action(self):
        capabilities_text = (ROOT / "deploy/cloudflare-landing/capabilities.js").read_text(encoding="utf-8")
        capabilities = json.loads(capabilities_text.split(" = ", 1)[1].rsplit(";", 1)[0])
        verify = next(service for service in capabilities["services"] if service["service_id"] == "VERIFY_CLAIM")
        self.assertTrue(verify["supports_question_intake"])
        self.assertTrue(verify["supports_minimum_missing_evidence"])
        self.assertTrue(verify["quote_requires_human_authorization"])
        self.assertFalse(verify["outcome_guaranteed"])
        self.assertFalse(verify["automatic_research_authorization"])

    def test_root_docs_parity_and_generated_outputs(self):
        for relative in ["agent/index.html", "method-contract.json"]:
            self.assertEqual((ROOT / relative).read_bytes(), (ROOT / "docs" / relative).read_bytes())
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/build_agent_discovery.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
