#!/usr/bin/env python3
import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = Path("cases/800vdc/source-notes/power-integrations-ideal-power-sscb-20261012")


class SourceNoteTests(unittest.TestCase):
    def test_snapshot_hash_and_classification(self):
        note = json.loads((ROOT / REL / "index.json").read_text())
        payload = (ROOT / REL / "snapshot-v1.json").read_bytes()
        self.assertEqual(hashlib.sha256(payload).hexdigest(), note["snapshot_sha256"])
        self.assertEqual(note["classifications"], ["NEWLY_DISCOVERED_OLD_EVIDENCE", "NO_STATE_CHANGE"])
        self.assertFalse(note["state_changed"])

    def test_no_x_text_before_production(self):
        candidate = json.loads((ROOT / "data/ops/se/x-candidates/2026-10-21.json").read_text())
        self.assertEqual(candidate["status"], "WEBSITE_PUBLICATION_BLOCKED")
        self.assertIsNone(candidate["text"])
        self.assertEqual(candidate["x_post_sent"], 0)

    def test_root_docs_mirror(self):
        for name in ("index.html", "index.json", "snapshot-v1.json"):
            self.assertEqual((ROOT / REL / name).read_bytes(), (ROOT / "docs" / REL / name).read_bytes())
        self.assertEqual((ROOT / "sitemap.xml").read_bytes(), (ROOT / "docs/sitemap.xml").read_bytes())


if __name__ == "__main__":
    unittest.main()
