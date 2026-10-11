#!/usr/bin/env python3
"""Reproducible integrity and negative-control tests for the sample."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from score import load_jsonl, score_submission


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[3]
CONTROLLED_STATES = {
    "SUPPORTED",
    "OBSERVED",
    "UNKNOWN",
    "NOT_ESTABLISHED",
    "CONTRADICTED",
}


def parse_time(value: str) -> datetime:
    if len(value) == 10:
        value = f"{value}T23:59:59+00:00"
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


class TemporalEvalSampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tasks = load_jsonl(HERE / "tasks.jsonl")
        cls.gold = load_jsonl(HERE / "gold.jsonl")
        cls.manifest = json.loads((HERE / "source_manifest.json").read_text())

    def test_exactly_eight_unique_tasks(self):
        self.assertEqual(8, len(self.tasks))
        self.assertEqual(8, len({row["task_id"] for row in self.tasks}))
        self.assertEqual({row["task_id"] for row in self.tasks}, {row["task_id"] for row in self.gold})

    def test_source_hashes_are_frozen(self):
        for record in self.manifest["records"]:
            payload = (REPO_ROOT / record["path"]).read_bytes()
            self.assertEqual(record["sha256"], hashlib.sha256(payload).hexdigest())

    def test_gold_is_canonical_not_model_generated(self):
        by_claim = {row["claim_id"]: row for row in self.gold}
        for record in self.manifest["records"]:
            canonical = json.loads((REPO_ROOT / record["path"]).read_text())
            expected = by_claim[record["claim_id"]]
            self.assertEqual(canonical["state"], expected["state"])
            self.assertEqual(canonical["as_of"], expected["knowledge_cutoff"])

    def test_controlled_state_vocabulary(self):
        for task in self.tasks:
            self.assertEqual(CONTROLLED_STATES, set(task["allowed_states"]))
        for expected in self.gold:
            self.assertIn(expected["state"], CONTROLLED_STATES)

    def test_no_future_evidence_leakage(self):
        for task in self.tasks:
            cutoff = parse_time(task["knowledge_cutoff"])
            for item in task["primary_evidence"] + task["counterevidence_or_limits"]:
                if "source_date" in item:
                    source_date = item["source_date"]
                    if len(source_date) == 10:
                        self.assertLess(
                            datetime.fromisoformat(source_date).date(), cutoff.date()
                        )
                    else:
                        self.assertLessEqual(parse_time(source_date), cutoff)

    def test_public_tasks_do_not_embed_gold_fields(self):
        for task in self.tasks:
            self.assertNotIn("gold", task)
            self.assertNotIn("expected_state", task)
            self.assertNotIn("gold_state", task)

    def test_example_submission_scores_100(self):
        result = score_submission(HERE / "example_submission.jsonl")
        self.assertEqual(1, result["coverage"])
        self.assertEqual([], result["unknown_task_ids"])
        self.assertEqual(100, result["mean_score"])

    def test_overclaim_negative_control_loses_state_credit(self):
        rows = load_jsonl(HERE / "example_submission.jsonl")
        rows[1]["state"] = "SUPPORTED"
        with tempfile.TemporaryDirectory() as directory:
            submission = Path(directory) / "overclaim.jsonl"
            submission.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            result = score_submission(submission)
        self.assertLess(result["mean_score"], 100)
        task = next(row for row in result["results"] if row["task_id"] == "SE-TECP-002")
        self.assertEqual(0, task["components"]["state"])

    def test_release_boundary_is_explicit(self):
        rights = (HERE / "RIGHTS_AND_RELEASE.md").read_text()
        self.assertIn("BLOCKED_PENDING_OWNER_CONFIRMATION", rights)
        self.assertIn("THIRD_PARTY_SOURCE_TEXT_REDISTRIBUTED = `NO`", rights)


if __name__ == "__main__":
    unittest.main()
