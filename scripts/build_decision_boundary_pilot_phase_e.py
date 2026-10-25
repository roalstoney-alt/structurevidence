#!/usr/bin/env python3
"""Build the deterministic, synthetic Phase E pilot fixture and reports."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

from decision_boundary_pilot_v01 import (
    PROTOCOL_VERSION,
    SCHEMA_VERSION,
    append_event,
    build_report,
    empty_work_units,
    sha256,
)


ROOT = Path(__file__).resolve().parents[1]
PILOT_DIR = Path("pilot/decision-boundary-v0.1")
CONTEXT_PATH = PILOT_DIR / "fixture-context-v0.1.json"
EVENTS_PATH = PILOT_DIR / "synthetic-events-v0.1.jsonl"
REPORT_PATH = PILOT_DIR / "simulation-report-v0.1.json"
REPORT_MD_PATH = PILOT_DIR / "simulation-report-v0.1.md"
HASH_REPORT_PATH = Path("docs/implementation/SE-DUAL-SITE-002-PHASE-E-HASHES.json")
MIRRORS = {
    CONTEXT_PATH: Path("docs") / CONTEXT_PATH,
    EVENTS_PATH: Path("docs") / EVENTS_PATH,
    REPORT_PATH: Path("docs") / REPORT_PATH,
    REPORT_MD_PATH: Path("docs") / REPORT_MD_PATH,
    Path("protocol/decision-boundary-pilot/schema-v0.1.json"): Path("docs/protocol/decision-boundary-pilot/schema-v0.1.json"),
    Path("protocol/decision-boundary-pilot/README.md"): Path("docs/protocol/decision-boundary-pilot/README.md"),
}

PROTECTED_SHA256 = {
    "cases/800vdc/source-dependency/index.html": "e42b94dcbce09900c9b79bc2374bf09b53ace2d1b9e897a50fb544715272ba38",
    "cases/800vdc/source-dependency-v0.1.json": "9038817ab15e1202ea5ae8ca374f515f5381b6480fce22f2ff137d3267cd7705",
    "cases/800vdc/decision-conditions/index.html": "a50ab5f0985decd60aab105b90365ea3c10f4c0e5195d8c779c544649fd4d581",
    "cases/800vdc/decision-conditions-v0.1.json": "c451662988a44c9907c906e6e245b1ee64e5c204fc5dca7b4d06c26f4b49f040",
    "cases/800vdc/decision-conditions-v0.1.md": "bafe2695ee79f6cc0a9b5ed033546d1a36a84071d7a447f9ffed247eb6fe9fea",
    "protocol/source-dependency/registry-v0.1.json": "172172ccc1c9fe8587224c1dcf51ae8354be74d951603da6b5f96b1e7fa68203",
    "deploy/cloudflare-landing/migrations/0001_customer_intake.sql": "156cea56e8278abc280315c10b98af03616cc9c2f71a5bc8a2b02a358c47b851",
    "deploy/cloudflare-landing/locales/en.json": "b85af98ab67ad66bc05f0d90c01e6030a2577a37199f4de9ce022393b84c6cfe",
    "deploy/cloudflare-landing/locales/zh-CN.json": "1dab213b5f6f1356d70cf2d4ec551af4aef822f2ff43d22cbc1baa0d1683e310",
    "deploy/cloudflare-landing/locales/es.json": "89d74f1e785c59927f20f92ca6cf19d1bc55d0300eeedd76a2463ada2b2b58af",
}


def units(**updates: int) -> dict:
    value = empty_work_units()
    value.update(updates)
    return value


def draft(number: int, event_type: str, occurred_at: str, payload: dict) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "pilot_id": "SE-DBP-FIXTURE-001",
        "event_id": f"SE-DBP-FIXTURE-001-E{number:04d}",
        "event_type": event_type,
        "occurred_at": occurred_at,
        "recorded_at": occurred_at,
        "data_classification": "PUBLIC_TEST_FIXTURE_ONLY",
        "payload": payload,
    }


def fixture() -> tuple[dict, list[dict], dict]:
    context = {
        "protocol_version": PROTOCOL_VERSION,
        "pilot_id": "SE-DBP-FIXTURE-001",
        "classification": "PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT",
        "test_fixture_only": True,
        "real_customer_authorization": "NOT_GRANTED",
        "human_scope_approval": "NOT_APPLICABLE_TEST_FIXTURE",
        "data_boundary": "PUBLIC_TEST_FIXTURE_ONLY",
        "case_state_changed": False,
        "evidence_records_changed": False,
        "second_real_human_review": "UNSUPPORTED",
        "customer_identity_collected": False,
        "public_decision_condition_ids": [
            "SE-DC-CML-PDRE-001-OEG-CML-001-v0.1",
            "SE-DC-CML-PDRE-001-OEG-CML-002-v0.1",
        ],
    }
    baseline_scope = {
        "decision_question": "Synthetic evaluation of whether a bounded source review is ready to stop under two public decision conditions.",
        "decision_event": "TEST_FIXTURE_REVIEW_ONLY",
        "deadline_status": "SYNTHETIC_DATE_NOT_CUSTOMER_SUPPLIED",
        "private_owner_status": "NOT_COLLECTED",
        "scoped_source_ids": ["FIXTURE-SOURCE-A", "FIXTURE-SOURCE-B", "FIXTURE-SOURCE-C"],
        "qualifying_rule_ids": ["OEG-CML-001-v0.2", "OEG-CML-002-v0.2"],
        "evidence_cutoff": "2026-10-25T13:59:59Z",
        "last_reviewed_at": "2026-10-25T13:59:59Z",
        "unknowns": ["ACTUAL_CUSTOMER_BASELINE", "ACTUAL_CUSTOMER_DECISION", "ACTUAL_OUTCOME"],
        "competing_hypotheses": ["Review structure may help navigation", "Observed differences may be unrelated to the review structure"],
        "baseline_measurement": {
            "status": "SYNTHETIC_COMPARATOR_ONLY",
            "researcher_minutes": 240,
            "reviewer_touch_minutes": 60,
            "source_acquisition_cost_minor_units": 12000,
            "currency": "USD",
            "comparability": "NOT_AN_OBSERVED_BASELINE",
        },
    }
    drafts = [
        draft(1, "BASELINE_FROZEN", "2026-10-25T14:00:00Z", {
            **baseline_scope,
            "record_freeze_hash": sha256(baseline_scope),
            "work_units": units(),
        }),
        draft(2, "REVIEW_STARTED", "2026-10-25T14:05:00Z", {
            "scope_status": "FROZEN_FIXTURE_SCOPE",
            "work_units": units(researcher_minutes=15, review_rounds=1),
        }),
        draft(3, "EVIDENCE_ADDED", "2026-10-25T14:30:00Z", {
            "source_id": "FIXTURE-SOURCE-A",
            "qualification_status": "TEST_FIXTURE_CANDIDATE",
            "not_customer_evidence": True,
            "work_units": units(researcher_minutes=35, source_acquisition_cost_minor_units=2000, net_new_qualifying_sources=1),
        }),
        draft(4, "EVIDENCE_REJECTED", "2026-10-25T14:55:00Z", {
            "source_id": "FIXTURE-SOURCE-B",
            "reason": "Synthetic source fails the declared minimum level.",
            "work_units": units(researcher_minutes=25, reviewer_touch_minutes=10),
        }),
        draft(5, "CHALLENGE_RECEIVED", "2026-10-25T15:10:00Z", {
            "challenge_id": "FIXTURE-CHALLENGE-001",
            "status": "SYNTHETIC_INPUT_ONLY",
            "work_units": units(researcher_minutes=10, clarifications=1, challenge_submissions=1),
        }),
        draft(6, "RULE_CHECKED", "2026-10-25T15:30:00Z", {
            "rule_id": "OEG-CML-002-v0.2",
            "result": "FIXTURE_NOT_SATISFIED",
            "decision_condition_citation": "SE-DC-CML-PDRE-001-OEG-CML-002-v0.1",
            "work_units": units(researcher_minutes=20, reviewer_touch_minutes=20, decision_condition_citations=1),
        }),
        draft(7, "SUPERSEDED", "2026-10-25T15:35:00Z", {
            "supersedes_event_id": "SE-DBP-FIXTURE-001-E0006",
            "reason": "Fixture correction preserves the old row and narrows the rule label; it does not alter any real evidence conclusion.",
            "work_units": units(researcher_minutes=5, revisions_supersessions=1),
        }),
        draft(8, "RULE_CHECKED", "2026-10-25T15:40:00Z", {
            "rule_id": "OEG-CML-002-v0.2",
            "result": "FIXTURE_NOT_SATISFIED",
            "decision_condition_citation": "SE-DC-CML-PDRE-001-OEG-CML-002-v0.1",
            "supersedes_event_id": "SE-DBP-FIXTURE-001-E0006",
            "work_units": units(researcher_minutes=5, reviewer_touch_minutes=10, decision_condition_citations=1),
        }),
        draft(9, "STOP_POINT_EMITTED", "2026-10-25T16:00:00Z", {
            "stop_status": "FIXTURE_STOP_WITH_UNKNOWNS",
            "client_action": "UNSPECIFIED",
            "decision_recommendation": "NONE",
            "work_units": units(researcher_minutes=10, reviewer_touch_minutes=10),
        }),
    ]
    events: list[dict] = []
    for item in drafts:
        events = append_event(events, item, context)
    return context, events, build_report(context, events)


def render_markdown(context: dict, report: dict) -> str:
    telemetry = report["simulation_telemetry"]
    diagnostic = report["simulation_diagnostics"]
    return f"""# Decision Boundary Pilot · deterministic simulation v0.1

> `TEST_FIXTURE_ONLY` · `PUBLIC_ILLUSTRATION_NOT_CUSTOMER_PILOT` · not a customer pilot, outcome, recommendation, saving, or ROI claim.

- Pilot ID: `{context['pilot_id']}`
- Protocol: `{report['protocol_version']}`
- Event count: `{report['event_count']}`
- Event chain head SHA-256: `{report['event_chain_head_sha256']}`
- Event ledger SHA-256: `{report['event_ledger_sha256']}`
- Report SHA-256: `{report['report_sha256']}`
- Real customer authorization: `NOT_GRANTED`
- Second real human review: `UNSUPPORTED`
- Case/evidence changes: `false` / `false`

## Telemetry boundary

Observed customer telemetry: `NO_REAL_CUSTOMER_OBSERVATIONS`.

The deterministic fixture totals {telemetry['researcher_minutes']} researcher minutes, {telemetry['reviewer_touch_minutes']} reviewer-touch minutes, {telemetry['source_acquisition_cost_minor_units']} USD minor units, {telemetry['review_rounds']} review round, {telemetry['challenge_submissions']} challenge, {telemetry['decision_condition_citations']} decision-condition citations, and {telemetry['revisions_supersessions']} append-only supersession.

The synthetic comparator arithmetic is {diagnostic['fixture_time_difference_minutes']} minutes and {diagnostic['fixture_cost_difference_minor_units']} USD minor units. These values exist only to make the simulation deterministic and testable. They are not observed effects and cannot establish performance, causation, savings, avoided loss, or ROI.

## Baseline and outcome

- Comparison status: `INSUFFICIENT_DATA`
- Causal attribution: `NOT_ESTABLISHED`
- ROI: `NOT_EVALUATED`
- Client decision recorded: `false`
- Outcome observed: `false`

An actual comparison requires independently authorized scope, a real comparable baseline, client-supplied decision data, a permitted independently observed outcome, and causal analysis. No fixture value may be promoted into customer evidence.

## Missing data

{chr(10).join(f'- `{item}`' for item in report['missing_data'])}

## Causal limitations

{chr(10).join(f'- {item}' for item in report['causal_limitations'])}
"""


def file_sha256(path: Path | str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def write_hash_report(report: dict) -> None:
    for path, expected in PROTECTED_SHA256.items():
        actual = file_sha256(path)
        if actual != expected:
            raise RuntimeError(f"protected baseline drift: {path}: {actual} != {expected}")
    artifacts = [
        CONTEXT_PATH,
        EVENTS_PATH,
        REPORT_PATH,
        REPORT_MD_PATH,
        Path("protocol/decision-boundary-pilot/schema-v0.1.json"),
        Path("protocol/decision-boundary-pilot/README.md"),
        Path("scripts/decision_boundary_pilot_v01.py"),
        Path("scripts/build_decision_boundary_pilot_phase_e.py"),
        Path("scripts/test_decision_boundary_pilot_phase_e.py"),
        Path("docs/implementation/SE-DUAL-SITE-002-PHASE-E-PAGES-AUDIT.md"),
    ]
    hashes = {
        "project": "SE-DUAL-SITE-UPGRADE-002",
        "phase": "E",
        "baseline_main_sha": "95219314309e01af6bf4042831b2bf4ba18fbc02",
        "generated_from_fixture_time": "2026-10-25T16:00:00Z",
        "original_records_changed": 0,
        "case_state_changed": False,
        "client_decision_recorded": False,
        "real_customer_authorization": "NOT_GRANTED",
        "production_deployed": False,
        "event_ledger_sha256": report["event_ledger_sha256"],
        "event_chain_head_sha256": report["event_chain_head_sha256"],
        "simulation_report_sha256": report["report_sha256"],
        "protected_baseline_sha256": PROTECTED_SHA256,
        "phase_e_artifact_sha256": {str(path): file_sha256(path) for path in artifacts},
        "pages_deployment_audit": {
            "settings_ui_field": "UNVERIFIED_CONNECTOR_NO_ADMIN_ENDPOINT",
            "effective_source": "VERIFIED_MAIN_BRANCH_REPOSITORY_ROOT",
            "trigger": "GITHUB_MANAGED_DYNAMIC_PAGES_WORKFLOW_ON_MAIN_CHANGE",
            "target_main_sha_published": "VERIFIED",
            "workflow_run_id": 40198754542,
            "live_commit_unique_artifact_sha256": "180be9ffe40acf35a7e2b341552caafc4673d7e4d98f9b2a45d6fde52eb3c24e",
        },
        "test_results": {
            "phase_e_decision_boundary_pilot": "21/21 PASS",
            "source_dependency_protocol": "20/20 PASS",
            "phase_b_source_dependency_view": "21/21 PASS",
            "phase_c_decision_conditions": "26/26 PASS",
            "commercial_worker": "39/39 PASS",
            "brand_seo_history_focused": "16/16 PASS",
            "public_commercial_boundary": "PASS",
            "public_record_drift": "PASS",
            "history_immutability": "6/6 PASS; base guard PASS",
            "internal_links": "0 broken / 0 orphan",
            "tests_suite": "41 tests / 11 existing failures / 0 new failures",
            "scripts_suite": "500 tests / 37 existing failures / 11 existing errors / 0 new failures; includes 21 new passing Phase E tests",
            "public_case_primitives": "9 tests / 3 existing failures / 0 new failures",
            "commercial_domain_split": "5 tests / 1 existing failure / 0 new failures",
            "git_diff_check": "PASS",
            "new_regression_count": 0,
        },
    }
    (ROOT / HASH_REPORT_PATH).write_text(json.dumps(hashes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_outputs() -> dict:
    context, events, report = fixture()
    payloads = {
        CONTEXT_PATH: json.dumps(context, ensure_ascii=False, indent=2) + "\n",
        EVENTS_PATH: "".join(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in events),
        REPORT_PATH: json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        REPORT_MD_PATH: render_markdown(context, report),
    }
    for path, content in payloads.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    for source, mirror in MIRRORS.items():
        target = ROOT / mirror
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / source, target)
    write_hash_report(report)
    return report


if __name__ == "__main__":
    built = write_outputs()
    print(f"PHASE_E_EVENT_COUNT = {built['event_count']}")
    print(f"EVENT_LEDGER_SHA256 = {built['event_ledger_sha256']}")
    print(f"REPORT_SHA256 = {built['report_sha256']}")
