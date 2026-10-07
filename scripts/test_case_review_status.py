#!/usr/bin/env python3
"""Verify truthful review clocks, pending periods and the generated case index."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from export_case_review_status import ROOT, build, export


class ReviewStatusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ('data/case-watch', 'cases', 'docs/cases'):
            shutil.copytree(ROOT / directory, self.root / directory)
        # Exercise an unrun period in a fixture; the live schedule may advance.
        metadata = self.metadata()
        for case in metadata['cases']:
            if case['case_id'] != 'SE-IRK-LAB-001':
                case.update(latest_review_file=None, period_review_id=None)
                case['period'].update(id='2026-W41', start='2026-10-05', end='2026-10-11', status='NOT_YET_REVIEWED')
        self.save(metadata)

    def metadata(self):
        return json.loads((self.root / 'data/case-watch/monitoring-status.json').read_text())

    def save(self, value):
        (self.root / 'data/case-watch/monitoring-status.json').write_text(json.dumps(value))

    def weekly_review(self, *, result='NO_STATE_CHANGE', complete=True, at='2026-10-08T06:30:00+08:00'):
        metadata = self.metadata()
        case = next(row for row in metadata['cases'] if row['case_id'] == 'CML-PDRE-001')
        rel = 'data/case-watch/reviews/test-actual-review.json'
        review = {'case_id': case['case_id'], 'review_id': 'TEST-W41-001', 'reviewed_at': at,
                  'result': result, 'review_complete': complete,
                  'new_qualifying_evidence_count': 0, 'new_counter_evidence_count': 0,
                  'search_boundary': 'A bounded source check',
                  'sources_checked': [{'url': 'https://example.org/primary', 'status': 'READ'}]}
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(review))
        case['latest_review_file'] = rel
        case['period_review_id'] = review['review_id']
        case['period']['status'] = result
        self.save(metadata)
        return path

    def test_unrun_period_has_no_invented_review_or_counts(self):
        cases = {row['case_id']: row for row in build(self.root)['cases']}
        for cid in ('CML-PDRE-001', 'SE-BESS-SODIUM-001', 'SE-ONC-NSQNSCLC-CN-001'):
            case = cases[cid]
            self.assertEqual(case['period']['status'], 'NOT_YET_REVIEWED')
            self.assertIsNone(case['last_reviewed_at'])
            self.assertIsNone(case['new_qualifying_evidence_count'])
            self.assertIsNone(case['new_counter_evidence_count'])

    def test_real_no_change_review_advances_only_review_clock(self):
        before = build(self.root)
        original = (self.root / 'cases/800vdc/index.json').read_bytes()
        self.weekly_review()
        after = {row['case_id']: row for row in export(self.root)['cases']}
        case = after['CML-PDRE-001']
        self.assertEqual(case['last_reviewed_at'], '2026-10-08T06:30:00+08:00')
        self.assertEqual(case['review_result'], 'NO_STATE_CHANGE')
        previous = next(row for row in before['cases'] if row['case_id'] == case['case_id'])
        for field in ('evidence_state_as_of', 'last_material_change', 'current_public_state'):
            self.assertEqual(case[field], previous[field])
        self.assertEqual((self.root / 'cases/800vdc/index.json').read_bytes(), original)

    def test_incomplete_cannot_be_labeled_no_change(self):
        self.weekly_review(complete=False)
        with self.assertRaises(AssertionError):
            build(self.root)

    def test_previous_period_cannot_be_reused_as_current_review(self):
        self.weekly_review(at='2026-09-29T12:00:00+08:00')
        with self.assertRaisesRegex(AssertionError, 'older review'):
            build(self.root)

    def test_latest_accepted_irkutsk_cutoff_is_read_without_rewriting_snapshot(self):
        cases = {row['case_id']: row for row in build(self.root)['cases']}
        source = json.loads((self.root / 'cases/irkutsk-lab-worker-death/index.json').read_text())
        self.assertEqual(cases['SE-IRK-LAB-001']['evidence_state_as_of'], source['as_of'])
        settings = next(row for row in self.metadata()['cases'] if row['case_id'] == 'SE-IRK-LAB-001')
        expected = json.loads((self.root / settings['latest_review_file']).read_text())['result']
        self.assertEqual(cases['SE-IRK-LAB-001']['review_result'], expected)

    def test_projection_is_deterministic_and_mirrored(self):
        export(self.root)
        first = {rel: (self.root / rel).read_bytes() for rel in ('cases/index.html', 'cases/review-status.json')}
        export(self.root)
        for rel, value in first.items():
            self.assertEqual((self.root / rel).read_bytes(), value)
            self.assertEqual((self.root / 'docs' / rel).read_bytes(), value)
        page = first['cases/index.html'].decode()
        self.assertIn('EVIDENCE STATE AS OF', page)
        self.assertIn('RECORDED REVIEW / PERIOD', page)
        self.assertIn('Pending review · 2026-W41', page)
        self.assertIn('FOLDED FROM HOMEPAGE', page)


if __name__ == '__main__':
    unittest.main()
