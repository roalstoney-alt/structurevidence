#!/usr/bin/env python3
"""Check semantic boundaries, referential integrity and frozen public history."""
from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / 'cases/irkutsk-lab-worker-death'
CID = 'SE-IRK-LAB-001'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = []
        self.hrefs = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if 'href' in attrs:
            self.hrefs.append(attrs['href'])
        if tag in {'section', 'article', 'div', 'main', 'header', 'footer', 'aside'}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in {'section', 'article', 'div', 'main', 'header', 'footer', 'aside'}:
            assert self.stack and self.stack.pop() == tag, f'unbalanced tag: {tag}'


def main():
    index = load(CASE / 'index.json')
    current = load(CASE / index['current_snapshot'])
    repaired = load(CASE / 'state-v0.2.json')
    mapping = load(CASE / 'input-alias-map-v0.1.json')
    by_id = {x['claim_id']: x for x in repaired['claims']}
    aliases = {x['input_alias']: x for x in mapping['mappings']}
    assert len(by_id) == len(repaired['claims']) == 17
    assert set(aliases) == {'CL-001', 'CL-002', 'CL-003', 'CL-004', 'CL-062', 'CL-063',
                            'CL-064-A', 'CL-064-B', 'CL-065', 'CL-066', 'CL-067'}
    assert mapping['unresolved_input_aliases'] == repaired['unresolved_input_aliases'] == []
    assert aliases['CL-003']['public_claim_id'] == CID + '.PNEUMONIC_PLAGUE_DIAGNOSIS'
    assert aliases['CL-004']['public_claim_id'] == CID + '.OCCUPATIONAL_LAB_EXPOSURE'
    assert aliases['CL-067']['public_claim_id'] == CID + '.WHO_FULLY_INFORMED_RISK_ASSESSMENT'
    assert aliases['CL-067']['public_claim_id'] != CID + '.WHO_INITIAL_RISK_ASSESSMENT'
    assert by_id[CID + '.WHO_FULLY_INFORMED_RISK_ASSESSMENT']['status'] == 'NOT_ESTABLISHED'
    assert by_id[CID + '.WHO_INITIAL_RISK_ASSESSMENT']['status'] == 'SUPPORTED'
    assert by_id[CID + '.WHO_SECOND_EMPLOYEE_REPORT_VERIFICATION_REQUESTED']['status'] == 'SUPPORTED'
    assert by_id[CID + '.SECOND_PLAGUE_CASE']['status'] == 'NOT_ESTABLISHED'
    assert by_id[CID + '.SECOND_DEATH']['status'] == 'NOT_ESTABLISHED'
    assert aliases['CL-064-A']['origin_claim_id'] == aliases['CL-064-B']['origin_claim_id'] == 'CL-064'
    assert aliases['CL-002']['input_status'] == 'OBSERVED'
    assert 'underlying diagnosis is not upgraded' in aliases['CL-002']['scope_note']

    evidence = {x['evidence_id']: x for x in repaired['sources']}
    assert len(evidence) == len(repaired['sources']) == 10
    for row in repaired['claims']:
        assert set(row['sources']) <= evidence.keys(), row['claim_id']
        assert set(row.get('reported_death_date_sources', [])) <= evidence.keys()
    for row in mapping['mappings']:
        target = by_id[row['public_claim_id']]
        assert target['input_alias'] == row['input_alias']
        assert target['status'] == row['public_status']
    assert evidence[CID + '-EV-008']['retrieval_level'] == 'OPENED_EXTRACTED_TEXT'
    assert urlparse(evidence[CID + '-EV-008']['source_url']).hostname == 'www.who.int'
    assert evidence[CID + '-EV-009']['source_date'] is None
    assert evidence[CID + '-EV-010']['latest_access_status'] == 'OPEN_FAILED_TOOL_INACCESSIBLE'
    assert by_id[CID + '.CONTACT_RELEASE_90_PERCENT_REPORTED']['status'] == 'OBSERVED'
    assert by_id[CID + '.CONTACT_OBSERVATION_COMPLETED_REPORTED']['status'] == 'OBSERVED'

    original = load(CASE / 'state-v0.1.json')
    for row in original['claims']:
        repaired_row = by_id[row['claim_id']]
        assert repaired_row['statement'] == row['statement']
        assert repaired_row['status'] == row['status']
    assert repaired['history'][:len(original['history'])] == original['history']
    archived = load(CASE / 'index-v0.1.json')
    assert archived['evidence'][5]['source_date'] == '2022-07-07'
    assert repaired['sources'][5]['source_date'] == '2026-09-29'
    assert repaired['sources'][5]['previous_recorded_source_date'] == '2022-07-07'
    frozen = load(ROOT / 'scripts/fixtures/irkutsk-public-v0.1-sha256.json')
    for rel, digest in frozen['immutable_records'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest, rel

    review = load(CASE / 'search-review-v0.2.json')
    assert len(review['opened_sources']) == review['page_open_attempt_count'] == 8
    assert sum(x['status'].startswith('READ_') for x in review['opened_sources']) == review['successful_page_open_count'] == 3
    assert sum(x['status'].startswith('OPEN_FAILED_') for x in review['opened_sources']) == review['failed_page_open_count'] == 5
    assert review['result'] == 'REVIEW_INCOMPLETE' and review['state_changed'] is False
    assert review['package_inputs']['status'] == 'AVAILABLE' and len(review['package_inputs']['files']) == 6
    assert load(CASE / 'search-review-v0.1.json')['package_inputs']['status'] == 'MISSING'

    # Current data must resolve its latest pointers; future snapshots may advance.
    assert current['case_id'] == index['case_id'] == CID
    assert current['claims'] == index['claims']
    assert current['sources'] == index['evidence']
    assert current['current_state'] == index['current_state']
    assert load(CASE / index['latest_review'])['review_id'] == current['review_id']
    for path in CASE.iterdir():
        if path.is_file():
            mirror = ROOT / 'docs/cases/irkutsk-lab-worker-death' / path.name
            assert mirror.read_bytes() == path.read_bytes(), path.name

    for rel in ['cases/irkutsk-lab-worker-death/index.html', 'zh-cn/cases/irkutsk-lab-worker-death/index.html']:
        path = ROOT / rel
        assert path.read_bytes() == (ROOT / 'docs' / rel).read_bytes()
        page = Page()
        page.feed(path.read_text())
        assert not page.stack
        assert len(page.ids) == len(set(page.ids)), rel
        assert 'WHO_INITIAL_RISK_ASSESSMENT' in path.read_text()
        assert 'WHO_FULLY_INFORMED_RISK_ASSESSMENT' in page.ids
        for href in page.hrefs:
            if href.startswith('http') or href.startswith('#'):
                continue
            target = ROOT / href.lstrip('/') if href.startswith('/') else path.parent / href
            if '/irkutsk-lab-worker-death/' in str(target):
                assert target.is_file() or (target / 'index.html').is_file(), href
    print('PASS: input semantics, distinct risk claims, historical access limits, source references, immutable snapshots, and bilingual mirrors')


if __name__ == '__main__':
    main()
