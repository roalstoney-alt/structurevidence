#!/usr/bin/env python3
"""Tests for the append-only Anthropic publication activation mechanism."""
from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def module():
    path = ROOT / "scripts/prepare_anthropic_publication_activation.py"
    spec = importlib.util.spec_from_file_location("aico_activation", path)
    assert spec and spec.loader
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def fixture() -> dict:
    return {
        "schema_version": "SE-AICO-PUBLICATION-ACTIVATION-EVENT-v0.2",
        "case_id": "SE-AI-COMPUTE-OBLIGATIONS-001",
        "event_id": "SE-AICO-001-PUBLICATION-20990102T030405Z",
        "event_type": "PUBLICATION_ACTIVATION_VERIFIED",
        "owner_decision": "APPROVE_ATOMIC_PUBLICATION_ACTIVATION_AND_AUTO_DEPLOY",
        "owner_authorized_at": "2099-01-02T03:00:00Z",
        "candidate_head_sha": "1" * 40,
        "merge_commit_sha": "2" * 40,
        "publication_event_at": "2099-01-02T03:04:05Z",
        "pages_workflow_run_id": 1001,
        "pages_deployment_id": 1002,
        "pages_deployment_status_id": 1003,
        "pages_deployment_succeeded_at": "2099-01-02T03:04:05Z",
        "pages_source_branch": "main",
        "pages_source_path": "/",
        "pages_trigger": "PUSH_TO_MAIN_AUTOMATIC_PAGES_BUILD",
        "deployment_environment": "github-pages",
        "deployment_status": "success",
        "live_case_url": "https://structurevidence.org/cases/anthropic-compute-obligations/",
        "live_case_http_status": 200,
        "live_case_sha256": "3" * 64,
        "live_index_sha256": "4" * 64,
        "live_claims_sha256": "5" * 64,
        "live_verified_at": "2099-01-02T03:05:00Z",
        "source_sha256": "0c3a6faad0e1bddc30b108054ec318a0ed5ea509b0ff1d6c8f16a8bdf234424b",
        "owner_review_gate": "OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION",
        "test_fixture": True,
    }


class AnthropicPublicationActivationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.activation = module()

    def test_01_current_hold_decision_cannot_activate(self):
        event = fixture()
        event["owner_decision"] = "PR_HEAD_INTEGRITY_ACCEPTED_MERGE_HOLD"
        with self.assertRaisesRegex(ValueError, "separate exact merge"):
            self.activation.validate_event(event, allow_test_fixture=True)

    def test_02_actual_mode_rejects_test_fixture(self):
        with self.assertRaisesRegex(ValueError, "test fixtures"):
            self.activation.validate_event(fixture())

    def test_03_deployment_success_time_is_publication_event(self):
        event = fixture()
        event["publication_event_at"] = "2099-01-02T03:04:04Z"
        with self.assertRaisesRegex(ValueError, "must equal"):
            self.activation.validate_event(event, allow_test_fixture=True)

    def test_04_projection_is_append_only_and_preserves_evidence(self):
        event = fixture()
        original_claims = (ROOT / "cases/anthropic-compute-obligations/claims-v0.2.jsonl").read_bytes()
        original_registry = (ROOT / "cases/anthropic-compute-obligations/source-registry-public-v0.2.json").read_bytes()
        original_events = (ROOT / "cases/anthropic-compute-obligations/events-v0.2.jsonl").read_bytes()
        overlay = self.activation.build_overlay(ROOT, event, allow_test_fixture=True)
        self.assertNotIn("cases/anthropic-compute-obligations/claims-v0.2.jsonl", overlay)
        self.assertNotIn("cases/anthropic-compute-obligations/source-registry-public-v0.2.json", overlay)
        self.assertEqual((ROOT / "cases/anthropic-compute-obligations/claims-v0.2.jsonl").read_bytes(), original_claims)
        self.assertEqual((ROOT / "cases/anthropic-compute-obligations/source-registry-public-v0.2.json").read_bytes(), original_registry)
        projected_events = overlay["cases/anthropic-compute-obligations/events-v0.2.jsonl"]
        self.assertTrue(projected_events.startswith(original_events))
        self.assertEqual(len([x for x in projected_events.splitlines() if x]), 4)

    def test_05_projected_current_state_is_truthful(self):
        event = fixture()
        overlay = self.activation.build_overlay(ROOT, event, allow_test_fixture=True)
        index = json.loads(overlay["cases/anthropic-compute-obligations/index.json"])
        metadata = json.loads(overlay["cases/anthropic-compute-obligations/structured-metadata-v0.2.json"])
        current = json.loads(overlay["cases/anthropic-compute-obligations/publication-current-state-v0.2.json"])
        receipt = json.loads(overlay["cases/anthropic-compute-obligations/publication-receipt-v0.2.json"])
        self.assertEqual(index["deployment_state"], "APPLIED_AND_LIVE_VERIFIED")
        self.assertTrue(index["publication_authorized"])
        self.assertEqual(metadata["creativeWorkStatus"], "PUBLISHED_VERIFIED")
        self.assertEqual(metadata["datePublished"], event["publication_event_at"])
        self.assertEqual(current["status"], "PUBLISHED_AND_LIVE_VERIFIED")
        self.assertEqual(receipt["status"], "ACTUAL_DEPLOYMENT_AND_LIVE_URL_VERIFIED")
        self.assertFalse(receipt["prepublication_history_rewritten"])
        self.assertEqual(receipt["source_sha256"], self.activation.SOURCE_SHA256)

    def test_06_html_and_case_index_no_longer_claim_draft_current_state(self):
        overlay = self.activation.build_overlay(ROOT, fixture(), allow_test_fixture=True)
        html = overlay["cases/anthropic-compute-obligations/index.html"].decode()
        case_index = overlay["cases/index.html"].decode()
        self.assertNotIn("PROPOSED_FINAL_RELEASE_NOT_PUBLISHED", html)
        self.assertNotIn('"value":"NOT_PUBLISHED"', html)
        self.assertIn("PUBLISHED_VERIFIED", html)
        self.assertNotIn("Pending review · OWNER_REVIEW_OF_EXACT_MINIMAL_PR_DIFF", case_index)
        self.assertIn("OWNER_REVIEW_OF_ATOMIC_PUBLICATION_ACTIVATION", case_index)

    def test_07_root_docs_outputs_are_byte_identical(self):
        overlay = self.activation.build_overlay(ROOT, fixture(), allow_test_fixture=True)
        root_paths = [path for path in overlay if not path.startswith("docs/")]
        for path in root_paths:
            self.assertEqual(overlay[path], overlay["docs/" + path], path)

    def test_08_manifest_hashes_every_projection_file(self):
        event = fixture()
        overlay = self.activation.build_overlay(ROOT, event, allow_test_fixture=True)
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "overlay"
            self.activation.write_overlay(out, overlay, event)
            manifest = json.loads((out / "activation-manifest-v0.2.json").read_text())
            self.assertEqual(len(manifest["files"]), len(overlay))
            for row in manifest["files"]:
                self.assertEqual(self.activation.digest_bytes((out / row["path"]).read_bytes()), row["sha256"])

    def test_09_ordering_rejects_verification_before_deployment(self):
        event = copy.deepcopy(fixture())
        event["live_verified_at"] = "2099-01-02T03:03:00Z"
        with self.assertRaisesRegex(ValueError, "out of order"):
            self.activation.validate_event(event, allow_test_fixture=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
