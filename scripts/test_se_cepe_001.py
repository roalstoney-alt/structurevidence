#!/usr/bin/env python3
"""Regression and boundary tests for SE-CEPE-001."""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "ops/research/SE_CEPE_001"
SAMPLE = ROOT / "ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE"
SPEC = importlib.util.spec_from_file_location("se_cepe_runner", ROOT / "scripts/run_se_cepe_001.py")
RUNNER = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(RUNNER)

EXPECTED_GLOBAL_HASHES = {
    "tasks.jsonl": "2db1e1a6cbfe8d9032bfb1059cd81734b715c7b23ed9e43c400845ce066d19fc",
    "gold.jsonl": "972b8f259a149df998b6d3c7dcb04512ab25a27335c87634db14a459927166cf",
    "source_manifest.json": "7ff2f3770f58485548a65d47b49829570b6a6145bcefb44a5b244b3d69a79515",
}
EXPECTED_GOLD = {
    "SE-TECP-001": "SUPPORTED",
    "SE-TECP-002": "NOT_ESTABLISHED",
    "SE-TECP-003": "NOT_ESTABLISHED",
    "SE-TECP-004": "SUPPORTED",
    "SE-TECP-005": "NOT_ESTABLISHED",
    "SE-TECP-006": "NOT_ESTABLISHED",
    "SE-TECP-007": "NOT_ESTABLISHED",
    "SE-TECP-008": "NOT_ESTABLISHED",
}
TRUST_HASHES = {
    "POSITIONING_LOCK.md": "18b1bf1f52df04ce88ce778df9966f24e478e1bbcf9ccd64fc11482c1abdc8b5",
    "CAMPAIGN_STATE.json": "5ce3892780aaac8200b7ae267456c61779e914e25f404563a7d690f4e63e77bb",
}


def jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def temp_base() -> tuple[tempfile.TemporaryDirectory, Path]:
    owner = tempfile.TemporaryDirectory()
    path = Path(owner.name)
    shutil.copy2(BASE / "TASK_REGISTRY.json", path / "TASK_REGISTRY.json")
    return owner, path


class SECEPE001Tests(unittest.TestCase):
    def test_exactly_eight_ids_and_immutable_gold(self):
        baseline = RUNNER.validate_baseline(BASE)
        ids = {row["task_id"] for row in baseline["registry"]["tasks"]}
        self.assertEqual(ids, set(EXPECTED_GOLD))
        self.assertEqual({row["task_id"]: row["state"] for row in baseline["gold"]}, EXPECTED_GOLD)
        for name, expected in EXPECTED_GLOBAL_HASHES.items():
            self.assertEqual(RUNNER.sha256_file(SAMPLE / name), expected)

    def test_three_clocks_and_cutoff_are_separate(self):
        registry = json.loads((BASE / "TASK_REGISTRY.json").read_text(encoding="utf-8"))
        for task in registry["tasks"]:
            self.assertIn("event_at", task)
            self.assertIn("public_disclosure_at", task)
            self.assertIn("knowledge_cutoff_at", task)
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        RUNNER.execute(path, "CLOCK-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "no-change")
        for row in jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl"):
            self.assertEqual(row["checked_at"], "2026-10-11T12:00:00+08:00")
            self.assertIsNotNone(row["event_at"])
            self.assertIsNotNone(row["public_disclosure_at"])
            self.assertIsNotNone(row["knowledge_cutoff_at"])
            self.assertNotEqual(row["checked_at"], row["knowledge_cutoff_at"])

    def test_append_only_and_run_id_idempotence(self):
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        first = RUNNER.execute(path, "IDEMPOTENT-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "no-change")
        retry = RUNNER.execute(path, "IDEMPOTENT-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "no-change")
        second = RUNNER.execute(path, "IDEMPOTENT-002", "2026-10-12T12:00:00+08:00", "scheduled", 1, "no-change")
        self.assertEqual(first["status"], "COMPLETE")
        self.assertTrue(retry["idempotent"])
        self.assertEqual(second["status"], "COMPLETE")
        self.assertEqual(len(jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl")), 16)
        self.assertEqual(len(jsonl(path / "SOURCE_CHECK_RUNS.jsonl")), 2)
        self.assertEqual(len((path / "RUN_COST_LEDGER.csv").read_text().splitlines()), 3)

    def test_source_retrieval_is_deduplicated_within_run(self):
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        calls = []

        def fake_fetch(url, timeout):
            calls.append(url)
            return {
                "retrieval_status": "AVAILABLE",
                "http_status": 200,
                "final_url": url,
                "source_content_sha256": RUNNER.sha256_bytes(url.encode()),
                "bytes_hashed": len(url),
                "content_truncated": False,
                "error": None,
            }

        with mock.patch.object(RUNNER, "fetch_public_source", side_effect=fake_fetch):
            RUNNER.execute(path, "DEDUPE-001", "2026-10-11T12:00:00+08:00", "controlled", 1)
        expected_unique_primary_urls = {
            task["source_urls"][0]
            for task in json.loads((path / "TASK_REGISTRY.json").read_text())["tasks"]
        }
        self.assertEqual(set(calls), expected_unique_primary_urls)
        self.assertEqual(len(calls), len(expected_unique_primary_urls))

    def test_unavailable_primary_uses_registered_fallback(self):
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)

        def fallback_fetch(url, timeout):
            available = "apnews.com" not in url
            return {
                "retrieval_status": "AVAILABLE" if available else "SOURCE_UNAVAILABLE",
                "http_status": 200 if available else 403,
                "final_url": url,
                "source_content_sha256": RUNNER.sha256_bytes(url.encode()) if available else None,
                "bytes_hashed": len(url) if available else 0,
                "content_truncated": False,
                "error": None if available else "HTTPError:403",
            }

        with mock.patch.object(RUNNER, "fetch_public_source", side_effect=fallback_fetch):
            result = RUNNER.execute(path, "FALLBACK-001", "2026-10-11T12:00:00+08:00", "controlled", 1)
        row = next(item for item in jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl") if item["task_id"] == "SE-TECP-007")
        self.assertEqual(result["status"], "COMPLETE")
        self.assertEqual(row["retrieval_status"], "AVAILABLE")
        self.assertEqual(len(row["source_attempts"]), 2)
        self.assertEqual(row["source_attempts"][0]["http_status"], 403)
        self.assertEqual(row["source_attempts"][1]["http_status"], 200)

    def test_failures_are_not_no_change(self):
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        result = RUNNER.execute(path, "FAIL-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "failure")
        rows = jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl")
        self.assertEqual(result["status"], "COMPLETE_WITH_OPERATIONAL_EXCEPTIONS")
        self.assertEqual(result["checks_failed"], 8)
        self.assertTrue(all(row["observation_status"] == "CHECK_FAILED" for row in rows))
        self.assertNotIn("NO_MATERIAL_CHANGE", {row["observation_status"] for row in rows})
        report = (path / "EVIDENCE_CHANGE_REPORTS/FAIL-001.md").read_text()
        self.assertIn("OPERATIONAL_EXCEPTION_NOT_A_NULL_RESULT", report)
        self.assertIn("DECISION_CHANGED = `UNKNOWN", report)

    def test_synthetic_change_is_append_only_and_does_not_mutate_gold(self):
        before = {name: RUNNER.sha256_file(SAMPLE / name) for name in EXPECTED_GLOBAL_HASHES}
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        RUNNER.execute(path, "CHANGE-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "change")
        rows = jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl")
        changed = [row for row in rows if row["observation_status"] == "NEW_EVIDENCE_OBSERVED"]
        self.assertEqual([row["task_id"] for row in changed], ["SE-TECP-001"])
        self.assertEqual(before, {name: RUNNER.sha256_file(SAMPLE / name) for name in EXPECTED_GLOBAL_HASHES})

    def test_search_scope_citations_counterevidence_and_hashes_retained(self):
        owner, path = temp_base()
        self.addCleanup(owner.cleanup)
        RUNNER.execute(path, "SCOPE-001", "2026-10-11T12:00:00+08:00", "controlled", 1, "no-change")
        for row in jsonl(path / "TASK_OBSERVATION_LEDGER.jsonl"):
            self.assertEqual(row["observation_scope"], "PRIMARY_SOURCE_AVAILABILITY_AND_RETRIEVAL_HASH_ONLY")
            self.assertTrue(row["evidence_citations"])
            self.assertIn("counterevidence_citations", row)
            self.assertRegex(row["source_content_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(row["record_hash"], r"^[0-9a-f]{64}$")

    def test_rights_and_kill_switches_default_closed(self):
        registry = json.loads((BASE / "TASK_REGISTRY.json").read_text())
        self.assertEqual(registry["controls"]["outreach"], "DENY")
        self.assertEqual(registry["controls"]["production_change"], "DENY")
        self.assertEqual(registry["controls"]["raw_task_redistribution"], "NEEDS_OWNER_CONFIRMATION")
        rights = {row["asset_id"]: row for row in jsonl(BASE / "PUBLICATION_RIGHTS_LEDGER.jsonl")}
        self.assertEqual(rights["SE-AI-DATA-001-RAW-EIGHT-TASK-PACKAGE"]["publication_permission"], "BLOCKED")
        self.assertTrue(rights["SE-CEPE-X-001"]["internal_data_excluded"])
        self.assertTrue(rights["SE-CEPE-ZH-001"]["internal_data_excluded"])

    def test_draft_limits_and_case_allowlist(self):
        x_text = (BASE / "X_DRAFTS_FOR_REVIEW.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```text\n(.*?)\n```", x_text, flags=re.S)
        self.assertEqual(len(blocks), 1)
        self.assertLessEqual(len(blocks[0]), 280)
        self.assertIn("DRAFT_NOT_SENT", x_text)
        zhihu = (BASE / "ZHIHU_DRAFTS_FOR_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("DRAFT_NOT_SENT", zhihu)
        self.assertIn("SE-IRK-LAB-001", (BASE / "PUBLICATION_RIGHTS_LEDGER.jsonl").read_text())

    def test_preserved_programme_states_and_trust_hashes(self):
        baseline = (BASE / "BASELINE_AND_BOUNDARIES.md").read_text(encoding="utf-8")
        self.assertIn("GTM005_STATUS = HOLD", baseline)
        self.assertIn("GTM002_V04_STATUS = STOP_AND_RETAIN_RESULT", baseline)
        trust = ROOT / "ops/growth/TRUST_BOUNDARY_30D_001"
        for name, expected in TRUST_HASHES.items():
            self.assertEqual(RUNNER.sha256_file(trust / name), expected)

    def test_no_site_or_api_change_proposed(self):
        backlog = (BASE / "PRODUCT_ISSUE_BACKLOG.md").read_text(encoding="utf-8")
        self.assertIn("NO_REPRODUCED_PRODUCT_ISSUE", backlog)
        proposal = (BASE / "PRODUCT_CHANGE_PROPOSALS/README.md").read_text(encoding="utf-8")
        self.assertIn("No proposal exists", proposal)


if __name__ == "__main__":
    unittest.main(verbosity=2)
