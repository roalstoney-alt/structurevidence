#!/usr/bin/env python3
"""Render evidence cutoffs and actual review status without advancing either clock.

This projection does not perform a review. All timestamps and results must come
from recorded artifacts; generating the page never makes a case freshly checked.
"""
from __future__ import annotations

import html
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CASE_IDS = {'CML-PDRE-001', 'SE-BESS-SODIUM-001', 'SE-ONC-NSQNSCLC-CN-001', 'SE-IRK-LAB-001'}
COUNT_FIELDS = ('new_qualifying_evidence_count', 'new_counter_evidence_count')


def load(root: Path, relative: str):
    return json.loads((root / relative).read_text(encoding='utf-8'))


def build(root: Path) -> dict:
    registry = load(root, 'data/case-watch/case-registry.json')
    status = load(root, 'data/case-watch/monitoring-status.json')
    inputs = {row['case_id']: row for row in status['cases']}
    assert set(inputs) == {row['case_id'] for row in registry['cases']} == CASE_IDS
    rows = []
    for registered in registry['cases']:
        cid = registered['case_id']
        rel = registered['public_slug'].strip('/')
        path = root / rel / 'index.json'
        if path.is_file():
            record = load(root, rel + '/index.json')
            cutoff = record['as_of']
            material = record['last_material_change']
            state = record['current_state']
            title = record['title']
            question = record['question']
            state_file = record.get('current_snapshot')
            state_file = rel + '/' + state_file if state_file else None
        else:
            record = load(root, registered['audit']['state_file'])
            cutoff = record['knowledge_cutoff']
            material = cutoff[:10]
            state = record['publication_state']
            title = 'Non-squamous NSCLC in China'
            question = 'What published evidence and aggregate data gaps are decision-relevant across distinct clinical contexts?'
            state_file = registered['audit']['state_file']

        settings = inputs[cid]
        reviewed_at = None
        review_result = None
        review_id = None
        counts = {field: None for field in COUNT_FIELDS}
        review_file = settings.get('latest_review_file')
        if review_file:
            review = load(root, review_file)
            review_id = review['review_id']
            reviewed_at = review['reviewed_at']
            review_result = review['result']
            assert reviewed_at and review_id
            assert review_result in {'NO_STATE_CHANGE', 'REVIEW_INCOMPLETE', 'HUMAN_GATE_REQUIRED'}
            for field in COUNT_FIELDS:
                counts[field] = review.get(field)
                assert counts[field] is None or (isinstance(counts[field], int) and counts[field] >= 0)
            if review_result == 'NO_STATE_CHANGE':
                assert review.get('review_complete') is True
                assert 'search_boundary' in review and review.get('sources_checked')
                assert counts['new_qualifying_evidence_count'] is not None
                assert counts['new_counter_evidence_count'] is not None

        period = settings['period']
        assert period['status'] in {'NOT_YET_REVIEWED', 'NO_STATE_CHANGE', 'REVIEW_INCOMPLETE', 'HUMAN_GATE_REQUIRED'}
        if period['status'] == 'NOT_YET_REVIEWED':
            # An older review may exist, but it cannot masquerade as this period.
            assert settings.get('period_review_id') is None
        else:
            assert review_id is not None
            assert settings['period_review_id'] == review_id
            assert period['status'] == review_result
            reviewed_date = datetime.fromisoformat(reviewed_at.replace('Z', '+00:00')).astimezone(ZoneInfo('Asia/Hong_Kong')).date().isoformat()
            assert period['start'] <= reviewed_date <= period['end'], 'An older review cannot stand in for this period'

        rows.append({'case_id': cid, 'title': title, 'canonical_path': registered['public_slug'],
                     'question': question, 'current_public_state': state,
                     'evidence_state_as_of': cutoff, 'last_material_change': material,
                     'featured': registered['featured'], 'management_status': registered['management_status'],
                     'last_reviewed_at': reviewed_at, 'review_result': review_result,
                     'latest_review_id': review_id, 'latest_review_file': review_file,
                     'period': period, 'period_review_id': settings.get('period_review_id'),
                     'monitoring': settings['monitoring'], **counts})
    rows.sort(key=lambda row: (row['last_material_change'], row['case_id']), reverse=True)
    return {'schema_version': '1.0', 'status_recorded_at': status['status_recorded_at'],
            'timestamp_semantics': {'status_recorded_at': 'Administrative status observation; not a scientific review timestamp.',
                                    'evidence_state_as_of': 'Cutoff of the currently published evidence state; retained until evidence changes.',
                                    'last_reviewed_at': 'Actual recorded review; null when no completed or bounded current review is recorded.'},
            'cases': rows}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def date(value) -> str:
    return f'<time datetime="{esc(value)}">{esc(value[:10])}</time>'


def render_row(row: dict) -> str:
    path = row['canonical_path']
    extra = ' · FOLDED FROM HOMEPAGE' if row['management_status'] == 'FOLDED' else ''
    label = row['current_public_state'].replace('_', ' ')
    if row['case_id'] == 'CML-PDRE-001':
        label = 'SINGLE INSTANCE EVIDENCE'
    elif row['case_id'] == 'SE-ONC-NSQNSCLC-CN-001':
        label = 'RESEARCH PREVIEW'
    klass = 'not-established' if 'NOT ESTABLISHED' in label and 'INCOMPLETE' not in label else 'pending'
    if row['case_id'] == 'CML-PDRE-001':
        klass = 'observed'
    period = row['period']
    if period['status'] == 'NOT_YET_REVIEWED':
        review = f'<strong>Pending review · {esc(period["id"])}</strong><br><small>No completed review recorded for this period.</small>'
        planned = row['monitoring'].get('configured_start_at')
        if planned:
            review += '<br><small>Configured start: ' + esc(planned[:16].replace('T', ' ')) + ' +08:00</small>'
    else:
        review = date(row['last_reviewed_at']) + f'<br><strong>{esc(period["status"].replace("_", " "))}</strong>'
        review += f'<br><small>{esc(period["id"])} · {esc(period["scope"])}</small>'
    if row['latest_review_file']:
        review += f'<br><a href="/{esc(row["latest_review_file"])}">Review record</a>'
    return (f'<tr data-case-id="{esc(row["case_id"])}"><td><a href="{esc(path)}"><strong>{esc(row["title"])}</strong></a>'
            f'<br><small>{esc(row["case_id"])}{extra}</small></td><td>{esc(row["question"])}</td>'
            f'<td><span class="state {klass}">{esc(label)}</span></td>'
            f'<td>{date(row["last_material_change"])}</td><td>{date(row["evidence_state_as_of"])}</td>'
            f'<td>{review}</td></tr>')


def export(root: Path = ROOT) -> dict:
    public = build(root)
    text = json.dumps(public, ensure_ascii=False, indent=2) + '\n'
    for prefix in ('', 'docs/'):
        (root / prefix / 'cases/review-status.json').write_text(text, encoding='utf-8')
    page = (root / 'cases/index.html').read_text(encoding='utf-8')
    begin = page.index('<table class="watch-table case-index">')
    end = page.index('</table>', begin) + len('</table>')
    table = '<table class="watch-table case-index"><thead><tr><th>CASE</th><th>QUESTION</th><th>CURRENT STATE</th><th>LAST MATERIAL CHANGE</th><th>EVIDENCE STATE AS OF</th><th>RECORDED REVIEW / PERIOD</th></tr></thead><tbody>\n'
    table += '\n'.join(render_row(row) for row in public['cases']) + '\n</tbody></table>'
    page = page[:begin] + table + page[end:]
    start_marker = '<!-- review-clock-note -->'
    end_marker = '<!-- /review-clock-note -->'
    note = (start_marker + '<p>Evidence-state dates advance when accepted evidence changes. Review dates record actual checks; '
            'a pending period is not a no-change finding. <a href="/cases/review-status.json">Review status JSON</a></p>' + end_marker)
    if start_marker in page:
        left = page.index(start_marker)
        right = page.index(end_marker, left) + len(end_marker)
        page = page[:left] + note + page[right:]
    else:
        marker = '<div class="table-scroll"'
        page = page.replace(marker, note + marker, 1)
    for prefix in ('', 'docs/'):
        (root / prefix / 'cases/index.html').write_text(page, encoding='utf-8')
    return public


if __name__ == '__main__':
    value = export()
    print(f'PASS: exported {len(value["cases"])} case review statuses without advancing evidence cutoffs')
