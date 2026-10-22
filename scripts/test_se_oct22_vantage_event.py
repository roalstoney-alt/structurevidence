#!/usr/bin/env python3
import hashlib, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REL=Path("cases/800vdc/events/vantage-heron-capacity-agreement-2026")
class VantageEventTest(unittest.TestCase):
  def test_event_hash_and_state(self):
    event=json.loads((ROOT/REL/"index.json").read_text())
    self.assertEqual(hashlib.sha256((ROOT/REL/"snapshot-v1.json").read_bytes()).hexdigest(),event["snapshot_sha256"])
    self.assertIn("NEW_EVENT",event["classifications"]); self.assertIn("NO_STATE_CHANGE",event["classifications"]); self.assertFalse(event["state_changed"])
  def test_site_first_gate(self):
    x=json.loads((ROOT/"data/ops/se/x-candidates/2026-10-22.json").read_text())
    self.assertEqual(x["status"],"WEBSITE_PUBLICATION_BLOCKED"); self.assertIsNone(x["text"]); self.assertEqual(x["x_post_sent"],0)
  def test_mirrors(self):
    for name in ("index.html","index.json","snapshot-v1.json"):
      self.assertEqual((ROOT/REL/name).read_bytes(),(ROOT/"docs"/REL/name).read_bytes())
    self.assertEqual((ROOT/"sitemap.xml").read_bytes(),(ROOT/"docs/sitemap.xml").read_bytes())
if __name__=="__main__": unittest.main()
