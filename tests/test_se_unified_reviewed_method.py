import unittest

from scripts.se_unified_ops import GateBlocked, default_candidate


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
        candidate = default_candidate("2026-10-31", CONFIG, self.reviewed_event())
        self.assertEqual(candidate["source_urls"], ["https://structurevidence.org/cases/800vdc/events/ev-1/"])
        self.assertEqual(candidate["snapshot_sha256"], "a" * 64)
        self.assertEqual(candidate["factual_status"], "METHOD_CONTENT+NO_STATE_CHANGE")
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_rejects_non_event_url(self):
        reviewed = self.reviewed_event()
        reviewed["template"] = "Reviewed method note for {date_sgt}. https://structurevidence.org"
        with self.assertRaises(GateBlocked):
            default_candidate("2026-10-31", CONFIG, reviewed)


if __name__ == "__main__":
    unittest.main()
