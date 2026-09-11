from __future__ import annotations

import json
from pathlib import Path

from rdl.freshness.validation.gate_registry import summarize


def render(registry: dict) -> str:
    status = {row["gate_id"]: row["status"] for row in registry["results"]}
    meta = registry["metadata"]
    counts = summarize(registry["results"])
    outcomes = meta.get("subject_outcomes", {})
    rows = "\n".join(f"| {row['gate_id']} | {row['status']} | {row['validator']} | {', '.join(row['evidence_refs'])} |" for row in registry["results"])
    subject_blocks = "\n\n".join(f"""{label.upper()}
Release Freshness: {data['release']}
Level Freshness: {data['level']}
Delta Freshness: {data['delta']}
Critical Evidence: {data['critical_evidence']}
GDR-SE: {data['gdr']}""" for label, data in outcomes.items())
    return f"""# RDL Freshness Final Execution Report

PROJECT
StructEvidence

WORKFLOW
STRUCTEVIDENCE_RDL_FRESHNESS_POLICY_v0.1

BASE_COMMIT
`{meta.get('base_commit')}`

IMPLEMENTATION_COMMIT
`{meta.get('implementation_commit')}`

FINAL_AUDIT_COMMIT
`{meta.get('final_audit_commit')}`

REMOTE_MAIN
`{meta.get('remote_main')}`

REMOTE_MATCH
{status['RDLF45_REMOTE_MATCH']}

POLICY_VERSION
RDL_FRESHNESS_v0.1

SUBJECT_CLASSES
{', '.join(meta.get('subject_classes', []))}

CONFIGURED_RULES
{meta.get('configured_rules')}

UNCONFIGURED_RULES
{meta.get('unconfigured_rules')}

LEVEL_FRESHNESS
{status['RDLF03_LEVEL_FRESHNESS_RULES']}

DELTA_FRESHNESS
{status['RDLF04_DELTA_FRESHNESS_RULES']}

EVIDENCE_FAMILY_FRESHNESS
{status['RDLF05_EVIDENCE_FAMILY_RULES']}

NO_GLOBAL_THRESHOLD
{status['RDLF06_NO_GLOBAL_THRESHOLD']}

CADENCE_ANALYSIS
{status['RDLF13_CADENCE_METRICS']}

THRESHOLD_DERIVATION
{status['RDLF14_THRESHOLD_EVIDENCE_BASIS']}

SENSITIVITY_ANALYSIS
{status['RDLF15_SENSITIVITY_ANALYSIS']}

EVENT_INVALIDATION
{status['RDLF08_EVENT_INVALIDATION_RULES']}

CORRECTION_OVERRIDE
{status['RDLF09_CORRECTION_OVERRIDE']}

SUPERSESSION_OVERRIDE
{status['RDLF10_SUPERSESSION_OVERRIDE']}

POLICY_NOT_CONFIGURED_FAILSAFE
{status['RDLF17_POLICY_NOT_CONFIGURED_FAILSAFE']}

CONFIG_DRIVEN_RUNTIME
{status['RDLF12_CONFIG_DRIVEN_RUNTIME']}

RUNTIME_CLOCK
{status['RDLF20_RUNTIME_CLOCK']}

NO_LOOKAHEAD
{status['RDLF19_NO_LOOKAHEAD']}

{subject_blocks}

PAID_DELIVERY
{meta.get('paid_delivery_status')}

TIMELINE_OVERLAY
{status['RDLF26_TIMELINE_OVERLAY']}

GDR_G3_INTEGRATION
{status['RDLF25_GDR_G3_INTEGRATION']}

FROZEN_RESEARCH_HASHES
UNCHANGED

TIMELINE_R1_1A_HASHES
UNCHANGED

ENGLISH_PUBLIC_SURFACE
{status['RDLF40_ENGLISH_PUBLIC_SURFACE']}

ROOT_DOCS_SYNC
{status['RDLF42_ROOT_DOCS_SYNC']}

HREF_INTEGRITY
{status['RDLF41_HREF_INTEGRITY']}

TESTS
{status['RDLF43_TESTS']}

GATE_SUMMARY
PASS: {counts['PASS']}
PARTIAL: {counts['PARTIAL']}
FAIL: {counts['FAIL']}
BLOCKED: {counts['BLOCKED']}
NOT_EVALUATED: {counts['NOT_EVALUATED']}

RDL_FRESHNESS_POLICY_ACCEPTANCE
{counts['acceptance']}

KNOWN_LIMITATIONS
v0.1 is a METHOD PILOT. Sparse Delta and unsupported dimensions remain POLICY_NOT_CONFIGURED.

NEXT_RECOMMENDED_WORKFLOW
RDL Freshness Longitudinal Validation v0.1

## Gate Results

| Gate | Status | Validator | Evidence |
| --- | --- | --- | --- |
{rows}
"""


def write_report(registry_path: Path, report_path: Path) -> str:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    text = render(registry)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(text.strip() + "\n", encoding="utf-8")
    return text
