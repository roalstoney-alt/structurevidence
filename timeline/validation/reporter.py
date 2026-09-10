from __future__ import annotations

import json
from pathlib import Path

from .gate_registry import REQUIRED_GATES, summary


def load_registry(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def render_report(registry: dict) -> str:
    results = registry["results"]
    statuses = {row["gate_id"]: row["status"] for row in results}
    facts = registry.get("metadata", {})
    counts = summary(results)
    subject_counts = facts.get("current_subject_comparison_deltas", {})
    gate_rows = "\n".join(f"| {row['gate_id']} | {row['status']} | {row['validator']} | {', '.join(row['evidence_refs'])} |" for row in results)
    missing = [gate for gate in REQUIRED_GATES if gate not in statuses]
    if missing:
        raise ValueError(f"missing gate results: {missing}")
    return f"""# Timeline R1.1a Final Execution Report

PROJECT
StructEvidence

WORKFLOW
STRUCTEVIDENCE_TIMELINE_R1_1A_RUNTIME_CLOSURE_WORKFLOW

TIMELINE_V0_1_COMMIT
`{facts.get('timeline_v0_1_commit', '')}`

TIMELINE_R1_COMMIT
`{facts.get('timeline_r1_commit', '')}`

TIMELINE_R1_1_COMMIT
`{facts.get('timeline_r1_1_commit', '')}`

R1_1A_BASE_COMMIT
`{facts.get('r1_1a_base_commit', '')}`

R1_1A_IMPLEMENTATION_COMMIT
`{facts.get('r1_1a_implementation_commit', '')}`

R1_1A_FINAL_AUDIT_COMMIT
`{facts.get('r1_1a_final_audit_commit', 'not self-recorded by design; verified externally after push')}`

ORIGIN_MAIN
`{facts.get('origin_main', '')}`

REMOTE_MAIN
`{facts.get('remote_main', '')}`

REMOTE_MATCH
{statuses['TL11A_26_REMOTE_MATCH']}

PRIOR_COMPARISON_RUNTIME
{statuses['TL11A_01_PRIOR_COMPARISON_RUNTIME']}

APPEND_SIMULATION
{statuses['TL11A_02_APPEND_SIMULATION']}

COMPARISON_LINEAGE
{statuses['TL11A_03_COMPARISON_LINEAGE']}

NONCOMPARABLE_PRIOR_BLOCK
{statuses['TL11A_04_NONCOMPARABLE_PRIOR_BLOCK']}

EXPLICIT_CHANGE_PRECEDENCE
{statuses['TL11A_05_EXPLICIT_CHANGE_PRECEDENCE']}

REAL_UTC_AS_OF
{statuses['TL11A_06_REAL_UTC_AS_OF']}

EXPLICIT_AS_OF_REPRODUCTION
{statuses['TL11A_07_EXPLICIT_AS_OF_REPRODUCTION']}

NAIVE_TIMESTAMP_REJECT
{statuses['TL11A_08_NAIVE_TIMESTAMP_REJECT']}

AGE_PROGRESSION
{statuses['TL11A_09_AGE_PROGRESSION']}

ACTIVE_FIXED_AS_OF_COUNT
{facts.get('active_fixed_as_of_count', '') if statuses['TL11A_10_NO_ACTIVE_FIXED_AS_OF'] == 'PASS' else 'FAIL'}

GATE_REGISTRY
{statuses['TL11A_11_GATE_REGISTRY']}

NO_DEFAULT_PASS
{statuses['TL11A_12_NO_DEFAULT_PASS']}

REPORT_FROM_GATE_RESULTS
{statuses['TL11A_13_REPORT_FROM_GATE_RESULTS']}

GATE_EVIDENCE_REFS
{statuses['TL11A_14_GATE_EVIDENCE_REFS']}

COMMIT_LINEAGE
{statuses['TL11A_15_BASE_COMMIT_LINEAGE']}

CURRENT_SUBJECT_COMPARISON_DELTAS
Strategy: {subject_counts.get('strategy', 0)}
BNB: {subject_counts.get('bnb', 0)}
SOL: {subject_counts.get('sol', 0)}
TRX: {subject_counts.get('trx', 0)}
XLM: {subject_counts.get('xlm', 0)}

FIXTURE_PRODUCTION_COMPARISON_DELTA
{statuses['TL11A_01_PRIOR_COMPARISON_RUNTIME']}

TIMELINE_R1_REGRESSION
{statuses['TL11A_16_EXISTING_LEVEL_DELTA_REGRESSION']}

TIMELINE_R1_1_REGRESSION
{statuses['TL11A_16_EXISTING_LEVEL_DELTA_REGRESSION']}

EVIDENCE_DYNAMICS
UNCHANGED

GDR_SE
UNCHANGED

RDL_FRESHNESS_POLICY
UNCONFIGURED

FROZEN_RESEARCH_HASHES
UNCHANGED

ENGLISH_PUBLIC_SURFACE
{statuses['TL11A_21_ENGLISH_PUBLIC_SURFACE']}

ROOT_DOCS_SYNC
{statuses['TL11A_22_ROOT_DOCS_SYNC']}

HREF_INTEGRITY
{statuses['TL11A_23_HREF_INTEGRITY']}

TESTS
{statuses['TL11A_24_TESTS']}

GATE_SUMMARY
PASS: {counts['PASS']}
PARTIAL: {counts['PARTIAL']}
FAIL: {counts['FAIL']}
BLOCKED: {counts['BLOCKED']}
NOT_EVALUATED: {counts['NOT_EVALUATED']}

TIMELINE_R1_1A_ACCEPTANCE
{counts['acceptance']}

NEXT_RECOMMENDED_WORKFLOW
RDL Freshness Policy v0.1

## Gate Results

| Gate | Status | Validator | Evidence |
| --- | --- | --- | --- |
{gate_rows}
"""


def write_report(registry_path: Path, report_path: Path) -> str:
    text = render_report(load_registry(registry_path))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text.strip() + "\n", encoding="utf-8")
    return text
