#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.se_unified_ops import (
        BlockedPublisher,
        GateBlocked,
        PublisherError,
        canonical_post_text,
        check_schedule_ownership,
        classify_github_write,
        default_candidate,
        live_publish_once,
        new_run,
        render_report,
        sha256_text,
        validate_candidate,
        validate_irkutsk_budget,
        validate_review,
        verify_public_deploy,
        x_weighted_length,
    )
except ModuleNotFoundError:
    from se_unified_ops import (
    BlockedPublisher,
    GateBlocked,
    PublisherError,
    canonical_post_text,
    check_schedule_ownership,
    classify_github_write,
    default_candidate,
    live_publish_once,
    new_run,
    render_report,
    sha256_text,
    validate_candidate,
    validate_irkutsk_budget,
    validate_review,
    verify_public_deploy,
    x_weighted_length,
    )


CONFIG = {
    "x": {
        "method_test_text": "Evidence states remain inspectable. Verify Your Verify. https://structurevidence.org",
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


class FakePublisher:
    def __init__(self, *, readback=True, timeout_once=False):
        self.account = {"id": "42", "username": "structevidence"}
        self.posts = []
        self.publish_calls = 0
        self.readback = readback
        self.timeout_once = timeout_once

    def verify_account(self):
        return self.account

    def recent_posts(self, limit=50):
        return self.posts[:limit]

    def publish(self, text, idempotency_key):
        del idempotency_key
        self.publish_calls += 1
        post = {"id": "1001", "author_id": "42", "text": text, "created_at": "2026-10-14T10:00:00Z"}
        self.posts.append(post)
        if self.timeout_once:
            self.timeout_once = False
            raise PublisherError("timeout", outcome_unknown=True)
        return post

    def fetch_post(self, post_id):
        if not self.readback:
            return {}
        return next(row for row in self.posts if row["id"] == post_id)


class AcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.ledger = self.root / "x-posts.jsonl"
        self.candidate = default_candidate("2026-10-14", CONFIG)

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

    def test_A07_missing_adapter_blocks_without_send(self):
        with self.assertRaises(PublisherError):
            live_publish_once(BlockedPublisher(), self.candidate, self.ledger)
        self.assertFalse(self.ledger.exists())

    def test_A08_write_without_readback_is_pending(self):
        receipt = live_publish_once(FakePublisher(readback=False), self.candidate, self.ledger)
        self.assertEqual(receipt["status"], "POST_ACCEPTED_VERIFICATION_PENDING")
        self.assertIsNone(receipt["post_url"])

    def test_A09_timeout_reconciles_before_retry(self):
        provider = FakePublisher(timeout_once=True)
        receipt = live_publish_once(provider, self.candidate, self.ledger)
        self.assertEqual(receipt["status"], "PUBLISHED_VERIFIED")
        self.assertEqual(provider.publish_calls, 1)

    def test_A10_no_fresh_evidence_method_post_is_truthful(self):
        validate_candidate(self.candidate)
        self.assertFalse(self.candidate["new_findings_existed"])
        self.assertLessEqual(x_weighted_length(self.candidate["text"]), 280)

    def test_A11_replay_does_not_duplicate_post(self):
        provider = FakePublisher()
        first = live_publish_once(provider, self.candidate, self.ledger)
        second = live_publish_once(provider, self.candidate, self.ledger)
        self.assertEqual(first["post_id"], second["post_id"])
        self.assertTrue(second["replayed"])
        self.assertEqual(provider.publish_calls, 1)

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
        artifact = json.dumps({"credential_env": "X_USER_ACCESS_TOKEN", "token_value": None})
        self.assertNotIn("Bearer ", artifact)
        self.assertNotIn("oauth_token_secret", artifact.lower())


if __name__ == "__main__":
    unittest.main()
