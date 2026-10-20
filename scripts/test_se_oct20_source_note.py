import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cases/800vdc/source-notes/china-xd-guian-attribution-20260729/'

class SourceNoteBoundaryTests(unittest.TestCase):
    def load(self, path):
        return json.loads((ROOT / path).read_text())

    def test_snapshot_and_mirrors(self):
        note = self.load(BASE + 'index.json')
        self.assertEqual(hashlib.sha256((ROOT / BASE / 'snapshot-v1.json').read_bytes()).hexdigest(), note['snapshot_sha256'])
        for path in (BASE+'index.json', BASE+'index.html', BASE+'snapshot-v1.json', BASE+'source-v1.json', 'sitemap.xml', 'cases/index.html', 'cases/review-status.json'):
            self.assertEqual((ROOT/path).read_bytes(), (ROOT/'docs'/path).read_bytes())

    def test_attribution_not_primary_or_new_event(self):
        note = self.load(BASE + 'index.json')
        self.assertTrue(note['not_a_verified_primary_event'])
        self.assertEqual(note['verification_status'], 'VERIFIED_SECONDARY_REPORT_ONLY')
        self.assertIsNone(note['upstream_original_url'])
        self.assertIsNone(note['event_at'])
        self.assertNotIn('NEW_EVENT', note['classifications'])
        self.assertFalse(note['state_changed'])
        self.assertEqual(note['old_stop'], note['candidate_stop'])

    def test_blocked_x_has_no_body(self):
        x = self.load('data/ops/se/x-candidates/2026-10-20-cloud-01.json')
        self.assertEqual(x['status'], 'WEBSITE_PUBLICATION_BLOCKED')
        self.assertIsNone(x['text'])
        self.assertIsNone(x['content_sha256'])
        self.assertEqual(x['X_POST_SENT'], 0)

    def test_counts_not_independent_adoption(self):
        review = self.load('cases/800vdc/search-review-20261020-cloud-01.json')
        self.assertEqual(review['daily_counters']['new_sources'], 1)
        self.assertEqual(review['daily_counters']['new_independent_evidence'], 0)
        self.assertEqual(review['daily_counters']['new_events'], 0)
        self.assertEqual(review['daily_counters']['state_changing_evidence'], 0)
        self.assertEqual(review['new_qualifying_evidence_count'], 0)

    def test_primary_event_ledger_not_polluted(self):
        ledger = self.load('cases/800vdc/events/index.json')
        self.assertNotIn('SE-SOURCE-NOTE-CML-PDRE-001-20260729-XD-GUIAN', {e['event_id'] for e in ledger['events']})

if __name__ == '__main__':
    unittest.main()
