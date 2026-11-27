import copy
import unittest

from scripts.se_unified_ops import GateBlocked, default_candidate, x_weighted_length


CONFIG = {
    "x": {
        "daily_manual_text_template": "Fallback {date_sgt}. https://structurevidence.org",
        "method_cutoff": "2026-10-14",
    }
}

REVIEWED_EVENT = {
    "template": "Reviewed method {date_sgt}. https://structurevidence.org/cases/example/events/verified/",
    "event_id": "SE-EVENT-EXAMPLE-1",
    "evidence_cutoff": "2026-10-16T22:45:36Z",
    "snapshot_path": "cases/example/events/verified/snapshot-v1.json",
    "snapshot_sha256": "a" * 64,
}


class ReviewedMethodEventCandidateTest(unittest.TestCase):
    def test_candidate_cites_one_event_and_retains_human_gate(self):
        candidate = default_candidate("2026-10-29", CONFIG, REVIEWED_EVENT)
        self.assertEqual(candidate["source_urls"], ["https://structurevidence.org/cases/example/events/verified/"])
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["x_post_sent"], 0)
        self.assertEqual(candidate["snapshot_sha256"], "a" * 64)
        self.assertLessEqual(x_weighted_length(candidate["text"]), 280)

    def test_missing_snapshot_hash_fails_closed(self):
        event = copy.deepcopy(REVIEWED_EVENT)
        event.pop("snapshot_sha256")
        with self.assertRaises(GateBlocked):
            default_candidate("2026-10-29", CONFIG, event)


if __name__ == "__main__":
    unittest.main()
