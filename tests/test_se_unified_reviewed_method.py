import unittest

from scripts.se_unified_ops import GateBlocked, default_candidate, new_run, render_report


CONFIG = {
    "x": {
        "method_test_text": "Evidence states remain inspectable. https://structurevidence.org",
        "daily_manual_text_template": "Daily evidence watch — {date_sgt}. https://structurevidence.org",
        "method_cutoff": "2026-10-14",
    }
}


class ReviewedMethodCandidateTest(unittest.TestCase):
    def reviewed_event(self):
        return {
            "template": "Reviewed method note for {date_sgt}. https://structurevidence.org/cases/800vdc/events/ev-1/",
            "event_id": "EV-1",
            "evidence_cutoff": "2026-10-15T10:00:00Z",
            "snapshot_path": "cases/800vdc/events/ev-1/snapshot-v1.json",
            "snapshot_sha256": "a" * 64,
        }

    def test_cites_one_event_and_snapshot(self):
        candidate = default_candidate("2026-11-04", CONFIG, self.reviewed_event())
        self.assertEqual(candidate["source_urls"], ["https://structurevidence.org/cases/800vdc/events/ev-1/"])
        self.assertEqual(candidate["snapshot_sha256"], "a" * 64)
        self.assertEqual(candidate["factual_status"], "METHOD_CONTENT+NO_STATE_CHANGE")
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_rejects_non_event_url(self):
        reviewed = self.reviewed_event()
        reviewed["template"] = "Reviewed method note for {date_sgt}. https://structurevidence.org"
        with self.assertRaises(GateBlocked):
            default_candidate("2026-11-04", CONFIG, reviewed)

    def test_report_counts_review_and_x_human_gates(self):
        candidate = default_candidate("2026-11-04", CONFIG, self.reviewed_event())
        run = new_run("2026-11-04", "abc")
        run["reviews"] = [{
            "case_id": "SE-IRK-LAB-001",
            "review_id": "R1",
            "reviewed_at": "2026-11-04T22:00:00+08:00",
            "result": "REVIEW_INCOMPLETE",
            "classifications": ["NO_STATE_CHANGE", "HUMAN_GATE_REQUIRED"],
        }]
        self.assertIn("human_gate_count: 2", render_report(run, candidate, {}))


if __name__ == "__main__":
    unittest.main()
