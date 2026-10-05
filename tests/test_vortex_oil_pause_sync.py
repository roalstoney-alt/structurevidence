#!/usr/bin/env python3
"""Guard the read-only OIL pause projection used by VORTEX activation."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TRACKER = ROOT / "data/open-intent-lab/genesis-001/outreach/outreach-tracker.json"
SYNC = ROOT / "data/vortex-activation/oil-genesis-001-pause-sync.json"
HANDOFF_MD = ROOT / "docs/open-intent-lab/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.md"
HANDOFF_JSON = ROOT / "data/open-intent-lab/genesis-001/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.json"
HANDOFF_SUMS = ROOT / "data/open-intent-lab/genesis-001/handoff/OIL_GENESIS_001_PAUSED_HANDOFF_2026-10-03.sha256"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VortexOilPauseSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tracker = load(TRACKER)
        cls.sync = load(SYNC)

    def test_transferred_handoff_hashes_match(self):
        source = self.sync["source_handoff"]
        self.assertEqual(digest(HANDOFF_MD), source["markdown_sha256"])
        self.assertEqual(digest(HANDOFF_JSON), source["manifest_sha256"])
        self.assertEqual(digest(HANDOFF_SUMS), source["checksum_inventory_sha256"])

    def test_oil_remains_paused_and_fail_closed(self):
        self.assertEqual(self.tracker["lifecycle_status"], "PAUSED")
        self.assertEqual(self.tracker["last_completed_node"], "STAGE_3_HUMAN_SEND_DECISION")
        self.assertFalse(self.tracker["send_authorized"])
        self.assertEqual(self.tracker["send_authorized_candidate_ids"], [])
        self.assertTrue(all(not record["send_authorized"] for record in self.tracker["records"]))

    def test_reality_boundary_is_still_zero(self):
        self.assertEqual(self.tracker["messages_sent"], 0)
        self.assertEqual(self.tracker["attempted_transmissions"], 0)
        self.assertEqual(self.tracker["successful_transmissions"], 0)
        self.assertIsNone(self.tracker["first_reality_boundary_t0"])
        self.assertEqual(self.tracker["response_windows_started"], 0)

    def test_production_counters_are_still_zero(self):
        for field in ["provider_created", "evidence_ingested", "vcf_created", "demand_created", "outcome_created", "reuse_record_created"]:
            self.assertEqual(self.tracker[field], 0, field)
            self.assertEqual(self.sync["oil_state"][field], 0, field)

    def test_vortex_channel_cannot_imply_oil_resume(self):
        separation = self.sync["vortex_separation"]
        self.assertTrue(all(value is False for key, value in separation.items() if key != "possible_future_use"))
        self.assertFalse(self.sync["oil_state"]["automatic_resume_allowed"])
        self.assertFalse(self.sync["oil_state"]["stage_4_allowed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
