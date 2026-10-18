import unittest

from scripts.se_unified_ops import GateBlocked, default_candidate


class XCandidateFallbackTest(unittest.TestCase):
    def test_daily_template_does_not_require_legacy_template(self):
        config = {"x": {"daily_manual_text_template": "Evidence watch {date_sgt}. https://structurevidence.org",
                        "method_cutoff": "2026-10-14"}}
        candidate = default_candidate("2026-10-18", config)
        self.assertIn("2026-10-18", candidate["text"])
        self.assertEqual(candidate["approval_gate"], "HUMAN_GATE_REQUIRED")
        self.assertEqual(candidate["x_post_sent"], 0)
        self.assertIsNone(candidate["post_id"])

    def test_legacy_template_remains_supported(self):
        config = {"x": {"method_test_text": "Evidence limits remain. https://structurevidence.org",
                        "method_cutoff": "2026-10-14"}}
        self.assertEqual(default_candidate("2026-10-18", config)["text"], config["x"]["method_test_text"])

    def test_daily_template_takes_precedence(self):
        config = {"x": {"daily_manual_text_template": "Daily https://structurevidence.org",
                        "method_test_text": "Legacy https://structurevidence.org", "method_cutoff": "2026-10-14"}}
        self.assertEqual(default_candidate("2026-10-18", config)["text"], config["x"]["daily_manual_text_template"])

    def test_missing_templates_fail_closed(self):
        with self.assertRaisesRegex(GateBlocked, "method candidate template"):
            default_candidate("2026-10-18", {"x": {"method_cutoff": "2026-10-14"}})


if __name__ == "__main__":
    unittest.main()
