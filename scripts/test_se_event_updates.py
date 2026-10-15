#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from scripts.se_unified_ops import (
    GateBlocked,
    build_event_x_candidate,
    new_run,
    render_report,
    validate_event_record,
    x_weighted_length,
)


ROOT = Path(__file__).resolve().parents[1]
EVENT_REL = Path("cases/800vdc/events/solaredge-ocp-2026/index.json")
SNAPSHOT_REL = Path("cases/800vdc/events/solaredge-ocp-2026/snapshot-v1.json")


def load(relative: Path | str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class WebsiteFirstEventTests(unittest.TestCase):
    def setUp(self):
        self.event = load(EVENT_REL)
        self.receipt = {
            "event_id": self.event["event_id"],
            "result": "PUBLIC_VERIFIED",
            "http_status": 200,
            "body_marker_verified": True,
            "public_url": self.event["public_url"],
        }

    def test_new_event_and_no_state_change_can_coexist(self):
        validate_event_record(self.event)
        self.assertEqual(self.event["classifications"], ["NEW_EVENT", "NO_STATE_CHANGE"])
        self.assertFalse(self.event["state_changed"])
        self.assertEqual(self.event["old_stop"], self.event["candidate_stop"])

    def test_historical_evidence_cannot_be_today_event(self):
        historical = dict(
            self.event,
            classifications=["NEWLY_DISCOVERED_OLD_EVIDENCE", "NO_STATE_CHANGE"],
            published_at="2026-10-15",
            event_at="2026-10-15",
        )
        with self.assertRaisesRegex(GateBlocked, "historical evidence"):
            validate_event_record(historical)

    def test_unverified_source_cannot_enter_verified_update(self):
        unverified = dict(self.event, verification_status="SEARCH_SNIPPET_ONLY")
        with self.assertRaisesRegex(GateBlocked, "unverified source"):
            validate_event_record(unverified)

    def test_unverified_production_blocks_x_candidate(self):
        candidate = build_event_x_candidate("2026-10-15", self.event, None)
        self.assertEqual(candidate["status"], "WEBSITE_PUBLICATION_BLOCKED")
        self.assertEqual(candidate["approval_gate"], "BLOCKED")
        self.assertIsNone(candidate["text"])
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_verified_candidate_points_to_site_and_site_retains_source_snapshot(self):
        candidate = build_event_x_candidate("2026-10-15", self.event, self.receipt)
        self.assertEqual(candidate["source_urls"], [self.event["public_url"]])
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["blocker"], "X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW")
        self.assertLessEqual(x_weighted_length(candidate["text"]), 280)
        page = (ROOT / "cases/800vdc/events/solaredge-ocp-2026/index.html").read_text(encoding="utf-8")
        self.assertIn(self.event["original_url"], page)
        self.assertIn("snapshot-v1.json", page)

    def test_snapshot_hash_and_root_docs_mirrors(self):
        snapshot = (ROOT / SNAPSHOT_REL).read_bytes()
        self.assertEqual(hashlib.sha256(snapshot).hexdigest(), self.event["snapshot_sha256"])
        for relative in (EVENT_REL, SNAPSHOT_REL, Path("cases/800vdc/events/solaredge-ocp-2026/index.html"), Path("cases/800vdc/events/index.json")):
            self.assertEqual((ROOT / relative).read_bytes(), (ROOT / "docs" / relative).read_bytes())

    def test_daily_counts_are_separate_and_state_date_is_frozen(self):
        review = load("cases/800vdc/search-review-20261015-01.json")
        run = new_run("2026-10-15", "baseline")
        run["reviews"] = [review]
        run["x"].update(result="AWAITING_HUMAN_REVIEW", blocker="X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW")
        report = render_report(run, build_event_x_candidate("2026-10-15", self.event, self.receipt), {})
        self.assertIn("- new_events: 1", report)
        self.assertIn("- state_changing_evidence: 0", report)
        self.assertEqual(review["evidence_state_as_of"], "2026-09-20T10:46:47Z")
        self.assertEqual(review["last_material_change"], "2026-09-20")

    def test_x_write_and_credentials_are_absent(self):
        source = (ROOT / "scripts/se_unified_ops.py").read_text(encoding="utf-8")
        workflow = (ROOT / ".github/workflows/se-unified-ops.yml").read_text(encoding="utf-8")
        for forbidden in ("api.x.com", "X_API_SECRET", "X_ACCESS_TOKEN", "live-x-test"):
            self.assertNotIn(forbidden, source + workflow)


if __name__ == "__main__":
    unittest.main()
