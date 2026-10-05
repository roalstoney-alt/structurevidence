#!/usr/bin/env python3
"""Freeze-boundary tests for the paused OIL-GENESIS-001 handoff."""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTREACH_DIR = ROOT / "data/open-intent-lab/genesis-001/outreach"
HANDOFF_DIR = ROOT / "data/open-intent-lab/genesis-001/handoff"
TRACKER_PATH = OUTREACH_DIR / "outreach-tracker.json"
EVENTS_PATH = OUTREACH_DIR / "outreach-events.jsonl"
MANIFEST_PATH = HANDOFF_DIR / "OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.json"
CHECKSUM_PATH = HANDOFF_DIR / "OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.sha256"
DOCUMENT_PATH = ROOT / "docs/open-intent-lab/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.md"
BASE_SHA = "f81fcbcbcab4891d0043eee8617f0a7b7f632ad2"
APPROVED_IDS = [f"OIL-CAND-{index:03d}" for index in range(1, 5)]
ALL_IDS = [*APPROVED_IDS, "OIL-CAND-005"]
ZERO_PRODUCTION = {
    "provider_created": 0,
    "evidence_ingested": 0,
    "vcf_created": 0,
    "demand_created": 0,
    "outcome_created": 0,
    "reuse_record_created": 0,
}


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PausedHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load_json(TRACKER_PATH)
        cls.records = cls.tracker["records"]
        cls.manifest = load_json(MANIFEST_PATH)
        cls.events = [
            json.loads(line)
            for line in EVENTS_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    def test_pause_control_state_is_exact(self):
        self.assertEqual(self.tracker["stage"], "PAUSED")
        self.assertEqual(self.tracker["lifecycle_status"], "PAUSED")
        self.assertEqual(self.tracker["last_completed_node"], "STAGE_3_HUMAN_SEND_DECISION")
        self.assertEqual(
            self.tracker["next_action"],
            "UNSET — awaiting human redesign of supplier participation approach",
        )

    def test_historical_approvals_and_hold_are_preserved(self):
        self.assertEqual([record["candidate_id"] for record in self.records], ALL_IDS)
        self.assertEqual([record["send_approval"] for record in self.records], ["YES"] * 4 + ["HOLD"])
        self.assertEqual(self.tracker["approved_for_possible_outreach"], APPROVED_IDS)

    def test_pause_suspends_every_current_send_authorization(self):
        self.assertFalse(self.tracker["send_authorized"])
        self.assertEqual(self.tracker["send_authorized_candidate_ids"], [])
        self.assertTrue(all(not record["send_authorized"] for record in self.records))
        self.assertTrue(all(record["authorization_suspended_by_pause"] for record in self.records[:4]))

    def test_reality_boundary_remains_zero_and_null(self):
        self.assertEqual(self.tracker["messages_sent"], 0)
        self.assertEqual(self.tracker["attempted_transmissions"], 0)
        self.assertEqual(self.tracker["successful_transmissions"], 0)
        self.assertIsNone(self.tracker["first_reality_boundary_t0"])
        self.assertEqual(self.tracker["response_windows_started"], 0)
        self.assertTrue(all(record["sent_at"] is None for record in self.records))

    def test_all_production_record_counters_remain_zero(self):
        for key, expected in ZERO_PRODUCTION.items():
            self.assertEqual(self.tracker[key], expected)
            self.assertEqual(self.manifest["production_records"][key], expected)

    def test_append_only_event_history_ends_in_pause(self):
        self.assertEqual(len(self.events), 9)
        self.assertEqual([event["event_type"] for event in self.events[:4]], ["OUTREACH_EXECUTION_AUTHORIZED"] * 4)
        self.assertEqual([event["event_type"] for event in self.events[4:8]], ["OUTREACH_EXECUTION_BLOCKED"] * 4)
        self.assertEqual(self.events[-1]["event_type"], "EXPERIMENT_PAUSED")
        self.assertEqual(self.events[-1]["last_completed_node"], "STAGE_3_HUMAN_SEND_DECISION")
        self.assertTrue(all(event["append_only"] for event in self.events))

    def test_no_sent_or_response_event_exists(self):
        event_types = {event["event_type"] for event in self.events}
        self.assertNotIn("OUTREACH_SENT", event_types)
        self.assertNotIn("SUPPLIER_RESPONDED", event_types)
        self.assertTrue(all(record.get("confirmation_reference") is None for record in self.records))
        self.assertTrue(all(record.get("response_window_end") is None for record in self.records))

    def test_manifest_matches_authoritative_repository_and_control_state(self):
        repository = self.manifest["authoritative_repository"]
        control = self.manifest["control_state"]
        self.assertEqual(repository["path"], "/Users/roal/Documents/ChatGPT/structevidence-oil-genesis-001")
        self.assertEqual(repository["branch"], "codex/oil-genesis-001")
        self.assertEqual(repository["head_sha"], BASE_SHA)
        self.assertEqual(repository["origin_main_sha"], BASE_SHA)
        self.assertEqual(control["current_status"], "PAUSED")
        self.assertFalse(control["automatic_resume_allowed"])
        self.assertFalse(control["stage_4_allowed"])

    def test_manifest_critical_artifact_hashes_match(self):
        for item in self.manifest["critical_artifacts"]:
            self.assertEqual(sha256(ROOT / item["path"]), item["sha256"], item["path"])

    def test_prepared_message_hashes_match_frozen_files(self):
        for candidate_id, expected in self.manifest["prepared_message_hashes"].items():
            suffix = candidate_id.split("-")[-1]
            path = OUTREACH_DIR / f"candidate-{suffix}" / "final_outreach_message.md"
            self.assertEqual(f"sha256:{sha256(path)}", expected)

    def test_checksum_inventory_matches_every_listed_file(self):
        lines = [line for line in CHECKSUM_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertGreaterEqual(len(lines), 14)
        for line in lines:
            expected, relative_path = line.split("  ", 1)
            self.assertEqual(sha256(ROOT / relative_path), expected, relative_path)

    def test_document_and_git_boundary_are_frozen(self):
        text = DOCUMENT_PATH.read_text(encoding="utf-8")
        self.assertIn("CURRENT_STATUS = PAUSED", text)
        self.assertIn("LAST_COMPLETED_NODE = STAGE_3_HUMAN_SEND_DECISION", text)
        self.assertIn("MESSAGES_ACTUALLY_SENT = 0", text)
        self.assertIn("HUMAN_GATE_REQUIRED = YES", text)
        completed = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.stdout.strip(), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
