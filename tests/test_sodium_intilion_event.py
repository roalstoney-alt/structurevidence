import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVENT_DIR = ROOT / "cases/sodium-ion-bess/events/intilion-catl-mou-2026"
DOCS_EVENT_DIR = ROOT / "docs/cases/sodium-ion-bess/events/intilion-catl-mou-2026"


class SodiumIntilionEventTest(unittest.TestCase):
    def test_snapshot_and_boundary(self):
        event = json.loads((EVENT_DIR / "index.json").read_text())
        snapshot = (EVENT_DIR / "snapshot-v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(snapshot).hexdigest(), event["snapshot_sha256"])
        self.assertEqual(
            set(event["classifications"]),
            {"NEWLY_DISCOVERED_OLD_EVIDENCE", "NO_STATE_CHANGE", "HUMAN_GATE_REQUIRED"},
        )
        self.assertFalse(event["state_changed"])
        self.assertEqual(event["old_stop"], event["candidate_stop"])
        self.assertEqual(event["website_publication_status"], "PENDING_PRODUCTION_VERIFICATION")

    def test_page_marks_chemistry_ambiguity(self):
        page = (EVENT_DIR / "index.html").read_text()
        self.assertIn("SE-EVENT-BESS-SODIUM-001-20261027-INTILION-CATL-MOU", page)
        self.assertIn("does not identify the chemistry of the 3 GWh tranche", page)
        self.assertIn("does not establish a named commissioned sodium-ion site", page)
        self.assertNotIn("commissioned sodium-ion site is established", page)

    def test_public_mirror_and_sitemap(self):
        for name in ("index.json", "snapshot-v1.json"):
            self.assertEqual(
                json.loads((EVENT_DIR / name).read_text()),
                json.loads((DOCS_EVENT_DIR / name).read_text()),
            )
        self.assertEqual((EVENT_DIR / "index.html").read_text(), (DOCS_EVENT_DIR / "index.html").read_text())
        self.assertEqual((ROOT / "sitemap.xml").read_text(), (ROOT / "docs/sitemap.xml").read_text())
        self.assertIn(
            "https://structurevidence.org/cases/sodium-ion-bess/events/intilion-catl-mou-2026/",
            (ROOT / "sitemap.xml").read_text(),
        )

    def test_runner_blocks_x_until_production_verification(self):
        candidate = json.loads((ROOT / "data/ops/se/x-candidates/2026-10-30.json").read_text())
        self.assertEqual(candidate["selected_event_id"], "SE-EVENT-BESS-SODIUM-001-20261027-INTILION-CATL-MOU")
        self.assertEqual(candidate["status"], "WEBSITE_PUBLICATION_BLOCKED")
        self.assertEqual(candidate["approval_gate"], "BLOCKED")
        self.assertIsNone(candidate["text"])
        self.assertEqual(candidate["x_post_sent"], 0)


if __name__ == "__main__":
    unittest.main()
