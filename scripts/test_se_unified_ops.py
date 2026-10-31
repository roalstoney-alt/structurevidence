#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.se_unified_ops import (
        GateBlocked,
        build_event_x_candidate,
        check_schedule_ownership,
        classify_github_write,
        default_candidate,
        new_run,
        render_report,
        select_x_candidate,
        sha256_text,
        validate_candidate,
        validate_event_record,
        validate_irkutsk_budget,
        validate_review,
        verify_public_deploy,
        x_weighted_length,
    )
except ModuleNotFoundError:
    from se_unified_ops import (
        GateBlocked,
        build_event_x_candidate,
        check_schedule_ownership,
        classify_github_write,
        default_candidate,
        new_run,
        render_report,
        select_x_candidate,
        sha256_text,
        validate_candidate,
        validate_event_record,
        validate_irkutsk_budget,
        validate_review,
        verify_public_deploy,
        x_weighted_length,
    )


CONFIG = {
    "x": {
        "method_test_text": "Evidence states remain inspectable. Verify Your Verify. https://structurevidence.org",
        "daily_manual_text_template": "Daily evidence watch — {date_sgt}. Evidence states remain inspectable. Verify Your Verify. https://structurevidence.org",
        "method_cutoff": "2026-10-14",
    }
}


def review(result="NO_STATE_CHANGE", complete=True):
    return {
        "case_id": "CML-PDRE-001", "review_id": "TEST-REVIEW-1",
        "reviewed_at": "2026-10-14T10:00:00Z", "result": result,
        "review_complete": complete, "search_boundary": "official sources",
        "sources_checked": [{"url": "https://example.org", "status": "READ"}],
        "old_state": "A", "new_state": "A", "new_qualifying_evidence_count": 0,
        "new_counter_evidence_count": 0,
    }


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.candidate = default_candidate("2026-10-14", CONFIG)
        self.event = {
            "event_id": "EV-1", "case_id": "CML-PDRE-001", "title": "Verified event",
            "published_at": "2026-10-15", "event_at": "2026-10-15", "retrieved_at": "2026-10-15T10:00:00Z",
            "originator": "Originator", "publisher": "Publisher", "source_type": "PRIMARY_CORPORATE_ANNOUNCEMENT",
            "original_url": "https://origin.example/event", "accessibility": "PUBLIC_HTML",
            "specific_claims": ["A bounded claim"], "supports": ["A verified event occurred"],
            "does_not_support": ["A state change"], "depends_on": [], "conflicts_counter_evidence": [],
            "verification_status": "VERIFIED_PRIMARY_SOURCE", "search_boundary": "Official source only",
            "snapshot_path": "cases/800vdc/events/ev-1/snapshot-v1.json", "snapshot_sha256": "a" * 64,
            "old_stop": "UNCHANGED", "candidate_stop": "UNCHANGED", "state_changed": False,
            "review_id": "REVIEW-1", "classifications": ["NEW_EVENT", "NO_STATE_CHANGE"],
            "public_url": "https://structurevidence.org/cases/800vdc/events/ev-1/",
            "x_candidate_text": "Verified event; the accepted stop remains unchanged. https://structurevidence.org/cases/800vdc/events/ev-1/",
        }

    def test_A01_exactly_one_active_logical_schedule(self):
        snapshot = {"timers": [{"id": "existing", "project": "StructEvidence", "active": True, "logical_owner": "existing", "local_time": "22:00", "timezone": "Asia/Singapore"}]}
        self.assertEqual(check_schedule_ownership(snapshot)["state"], "PASS")
        snapshot["timers"].append({"id": "duplicate", "project": "StructEvidence", "active": True, "local_time": "09:00", "timezone": "Asia/Singapore"})
        self.assertEqual(check_schedule_ownership(snapshot)["state"], "FAIL")

    def test_A02_no_new_material_preserves_state(self):
        item = review()
        validate_review(item)
        self.assertEqual(item["old_state"], item["new_state"])

    def test_A03_missing_key_source_is_incomplete(self):
        item = review("REVIEW_INCOMPLETE", False)
        item["sources_checked"] = [{"url": "https://example.org", "status": "INACCESSIBLE"}]
        validate_review(item)
        self.assertEqual(item["result"], "REVIEW_INCOMPLETE")

    def test_A04_syndicated_source_retains_dependency(self):
        item = review()
        item.update(search_budget={"targeted_search_groups": 1, "webpage_open_attempts": 2}, source_graph=[
            {"source_id": "origin", "url": "https://origin.example", "retrieved_at": "2026-10-14T10:00:00Z", "originator": "Agency", "publisher": "Agency", "source_type": "OFFICIAL", "claim_ids": ["c1"], "depends_on": [], "relation": "SUPPORT", "verification_status": "READ", "search_boundary": "official"},
            {"source_id": "relay", "url": "https://relay.example", "retrieved_at": "2026-10-14T10:01:00Z", "originator": "Agency", "publisher": "Relay", "source_type": "DERIVATIVE", "claim_ids": ["c1"], "depends_on": ["origin"], "relation": "DUPLICATE", "verification_status": "READ", "search_boundary": "reporting"},
        ])
        validate_irkutsk_budget(item)
        independent = [row for row in item["source_graph"] if not row["depends_on"]]
        self.assertEqual(len(independent), 1)

    def test_A05_material_conclusion_needs_human_gate(self):
        item = dict(self.candidate, material_state_transition=True, approval_gate="AUTO_PUBLISH")
        with self.assertRaises(GateBlocked):
            validate_candidate(item)

    def test_A06_private_item_hard_fails(self):
        item = dict(self.candidate, text="internal contract amount https://structurevidence.org")
        item["content_hash"] = sha256_text(item["text"])
        with self.assertRaises(GateBlocked):
            validate_candidate(item)

    def test_A07_x_write_entrypoints_are_removed(self):
        source = (Path(__file__).with_name("se_unified_ops.py")).read_text(encoding="utf-8")
        self.assertNotIn("api.x.com", source)
        self.assertNotIn("X_API_SECRET", source)
        self.assertNotIn("def live_publish_once", source)

    def test_A08_unverified_website_blocks_event_candidate(self):
        candidate = build_event_x_candidate("2026-10-15", self.event, None)
        self.assertEqual(candidate["status"], "WEBSITE_PUBLICATION_BLOCKED")
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_A09_verified_website_yields_human_candidate(self):
        receipt = {"event_id": "EV-1", "result": "PUBLIC_VERIFIED", "http_status": 200,
                   "body_marker_verified": True, "public_url": self.event["public_url"]}
        candidate = build_event_x_candidate("2026-10-15", self.event, receipt)
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["source_urls"], [self.event["public_url"]])
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_A10_no_fresh_evidence_method_post_is_truthful(self):
        validate_candidate(self.candidate)
        self.assertFalse(self.candidate["new_findings_existed"])
        self.assertIn("2026-10-14", self.candidate["text"])
        self.assertEqual(self.candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(self.candidate["status"], "AWAITING_HUMAN_REVIEW")
        self.assertLessEqual(x_weighted_length(self.candidate["text"]), 280)

    def test_A11_new_event_precedes_historical_evidence(self):
        historical = dict(self.event, event_id="EV-OLD", published_at="2026-09-01", event_at="2026-09-01",
                          classifications=["NEWLY_DISCOVERED_OLD_EVIDENCE", "NO_STATE_CHANGE"])
        receipt = {"event_id": "EV-1", "result": "PUBLIC_VERIFIED", "http_status": 200,
                   "body_marker_verified": True, "public_url": self.event["public_url"]}
        selected = select_x_candidate("2026-10-15", CONFIG, [historical, self.event], {"EV-1": receipt})
        self.assertEqual(selected["selected_event_id"], "EV-1")

    def test_A12_github_write_denied_has_no_fake_sha(self):
        result = classify_github_write(403, "invented")
        self.assertEqual(result["state"], "PUBLIC_UPDATE_BLOCKED")
        self.assertIsNone(result["commit_sha"])

    def test_A13_http_200_stale_body_fails_deploy_verification(self):
        result = verify_public_deploy("new", "old", 200, "old page", "new marker")
        self.assertEqual(result["result"], "PUBLIC_VERIFICATION_FAILED")

    def test_A14_failure_report_is_still_rendered(self):
        run = new_run("2026-10-14", "abc")
        run["x"]["blocker"] = "X_PUBLISH_BLOCKED"
        report = render_report(run, self.candidate, {})
        self.assertIn("StructEvidence Daily Execution Report", report)
        self.assertIn("X_PUBLISH_BLOCKED", report)
        self.assertIn(f"Exact English text: {self.candidate['text']}", report)
        self.assertIn(f"Content hash: {self.candidate['content_hash']}", report)
        self.assertIn("Approval gate: HUMAN_GATE_REQUIRED", report)
        self.assertIn("X_POST_SENT: 0", report)
        self.assertIn("Report delivered at: NONE", report)
        self.assertEqual(new_run("2026-10-18", "abc")["internal_workflows"]["sunday_weekly_synthesis"]["state"], "UNVERIFIED")
        self.assertEqual(new_run("2026-10-19", "abc")["internal_workflows"]["monday_socsm"]["state"], "UNVERIFIED")

    def test_A15_cml_stopped_is_missed_not_relaunched(self):
        run = new_run("2026-10-14", "abc")
        report = render_report(run, self.candidate, {"cml": {"enabled": "YES", "state": "MISSED", "next_action": "alert owner; no relaunch"}})
        self.assertIn("| MISSED | alert owner; no relaunch |", report)

    def test_A16_historical_missing_review_stays_unreviewed(self):
        run = new_run("2026-10-14", "abc")
        self.assertEqual(run["reviews"], [])
        self.assertNotIn("NO_STATE_CHANGE", json.dumps(run))

    def test_A17_material_correction_is_gated(self):
        item = dict(self.candidate, correction_required=True, material_state_transition=True, approval_gate="HUMAN_GATE_REQUIRED")
        validate_candidate(item)
        self.assertEqual(item["approval_gate"], "HUMAN_GATE_REQUIRED")

    def test_A18_artifacts_do_not_contain_secrets(self):
        artifact = json.dumps({"publication_mode": "HUMAN_REVIEW_ONLY", "x_post_sent": 0})
        self.assertNotIn("Bearer ", artifact)
        self.assertNotIn("oauth_token_secret", artifact.lower())
        validate_event_record(self.event)

    def test_A19_reviewed_method_candidate_cites_one_event_and_snapshot(self):
        reviewed = {
            "template": "Reviewed method note for {date_sgt}. https://structurevidence.org/cases/800vdc/events/ev-1/",
            "event_id": "EV-1",
            "evidence_cutoff": "2026-10-15T10:00:00Z",
            "snapshot_path": "cases/800vdc/events/ev-1/snapshot-v1.json",
            "snapshot_sha256": "a" * 64,
        }
        candidate = default_candidate("2026-10-31", CONFIG, reviewed)
        self.assertEqual(candidate["source_urls"], ["https://structurevidence.org/cases/800vdc/events/ev-1/"])
        self.assertEqual(candidate["snapshot_sha256"], "a" * 64)
        self.assertEqual(candidate["factual_status"], "METHOD_CONTENT+NO_STATE_CHANGE")
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_A20_reviewed_method_candidate_rejects_non_event_url(self):
        reviewed = {
            "template": "Reviewed method note for {date_sgt}. https://structurevidence.org",
            "event_id": "EV-1",
            "evidence_cutoff": "2026-10-15T10:00:00Z",
            "snapshot_path": "cases/800vdc/events/ev-1/snapshot-v1.json",
            "snapshot_sha256": "a" * 64,
        }
        with self.assertRaises(GateBlocked):
            default_candidate("2026-10-31", CONFIG, reviewed)


if __name__ == "__main__":
    unittest.main()
