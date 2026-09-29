#!/usr/bin/env python3
"""Validate the controlled StructureEvidence daily/weekly case-watch artifacts."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "case-watch"
EXPECTED_CASE_IDS = {
    "CML-PDRE-001",
    "SE-BESS-SODIUM-001",
    "SE-ONC-NSQNSCLC-CN-001",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(schema_path: Path, instance, label: str) -> None:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        detail = "; ".join(f"{list(error.path)}: {error.message}" for error in errors)
        raise AssertionError(f"{label}: {detail}")


def validate_registry() -> None:
    registry = load_json(DATA / "case-registry.json")
    ids = [case["case_id"] for case in registry["cases"]]
    assert registry["frozen_case_count"] == 3
    assert len(ids) == len(set(ids)) == 3
    assert set(ids) == EXPECTED_CASE_IDS
    assert registry["auto_add_cases"] is False


def validate_daily_ledgers() -> int:
    schema = DATA / "schema" / "daily-observation.schema.json"
    seen = set()
    count = 0
    for path in sorted((DATA / "daily").glob("[0-9][0-9][0-9][0-9]/*/*.jsonl")):
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw.strip():
                continue
            record = json.loads(raw)
            validate(schema, record, f"{path}:{line_number}")
            observation_id = record["observation_id"]
            assert observation_id not in seen, f"duplicate observation_id: {observation_id}"
            seen.add(observation_id)
            observed = datetime.fromisoformat(record["observed_at"].replace("Z", "+00:00"))
            known = datetime.fromisoformat(record["knowledge_time"].replace("Z", "+00:00"))
            assert known <= observed, f"knowledge_time occurs after observed_at: {observation_id}"
            assert record["public_state_mutated"] is False
            count += 1
    return count


def validate_weekly() -> None:
    weekly = load_json(DATA / "weekly" / "2026-W40.json")
    assert weekly["candidate_only"] is True
    assert weekly["review_period"]["complete"] is False
    reviews = weekly["reviews"]
    assert {review["case_id"] for review in reviews} == EXPECTED_CASE_IDS
    schema = DATA / "schema" / "weekly-review.schema.json"
    for review in reviews:
        validate(schema, review, review["case_id"])
        assert review["human_decision"] == "PENDING"
        assert review["publication_approved"] is False


def validate_manifest() -> None:
    manifest = load_json(ROOT / "publication" / "weekly" / "2026-W40-publication-manifest.json")
    validate(DATA / "schema" / "publication-manifest.schema.json", manifest, "publication manifest")
    ids = [case["case_id"] for case in manifest["cases"]]
    assert set(ids) == EXPECTED_CASE_IDS and len(ids) == len(set(ids))
    assert all(case["publication_approved"] is False for case in manifest["cases"])
    assert all(case["human_decision"] == "PENDING" for case in manifest["cases"])
    assert all(case["new_version"] is None for case in manifest["cases"])


def validate_search_provenance() -> None:
    provenance = load_json(DATA / "search-runs" / "2026" / "09" / "2026-09-29.json")
    required = {
        "search_run_id", "date", "queries", "domains_sources_checked", "results_discovered",
        "results_reviewed", "results_rejected", "qualifying_observations",
        "paywalled_restricted_sources", "limits", "stop_reason",
    }
    assert required <= set(provenance)
    assert provenance["mode"] == "REPOSITORY_LOCAL_BACKFILL_ONLY"
    assert provenance["research_authorization"] == "L0_REUSE"


def validate_protected_files() -> None:
    baseline = load_json(DATA / "protected-baseline-sha256.json")
    for relative, expected in baseline["files"].items():
        path = ROOT / relative
        assert path.is_file(), f"protected file missing: {relative}"
        assert sha256(path) == expected, f"protected file mutated: {relative}"


def validate_root_docs_parity() -> None:
    pairs = [
        ("cases/800vdc/index.html", "docs/cases/800vdc/index.html"),
        ("cases/800vdc/stop-v0.1.html", "docs/cases/800vdc/stop-v0.1.html"),
        ("cases/sodium-ion-bess/index.html", "docs/cases/sodium-ion-bess/index.html"),
        ("cases/sodium-ion-bess/state-v0.1.json", "docs/cases/sodium-ion-bess/state-v0.1.json"),
        ("cases/sodium-ion-bess/stop-v0.1.html", "docs/cases/sodium-ion-bess/stop-v0.1.html"),
        ("cases/sodium-ion-bess/decision-memory-v0.1.json", "docs/cases/sodium-ion-bess/decision-memory-v0.1.json"),
        ("cases/nsq-nsclc-china/index.html", "docs/cases/nsq-nsclc-china/index.html"),
        ("cases/nsq-nsclc-china/state-v0.1.json", "docs/cases/nsq-nsclc-china/state-v0.1.json"),
        ("cases/nsq-nsclc-china/stop-v0.1.html", "docs/cases/nsq-nsclc-china/stop-v0.1.html"),
        ("cases/index.html", "docs/cases/index.html"),
        ("sitemap.xml", "docs/sitemap.xml"),
    ]
    for root_relative, docs_relative in pairs:
        assert (ROOT / root_relative).read_bytes() == (ROOT / docs_relative).read_bytes(), (
            f"root/docs drift: {root_relative} != {docs_relative}"
        )


def validate_baseline_semantics() -> None:
    registry = load_json(DATA / "case-registry.json")
    cases = {case["case_id"]: case for case in registry["cases"]}
    assert all(case["audit"]["public_surface"] == "PRESENT" for case in cases.values())
    assert all(case["audit"]["public_version"] == "v0.1" for case in cases.values())
    assert cases["CML-PDRE-001"]["audit"]["state_file"] == "MISSING_PUBLIC_STATE_SNAPSHOT"
    assert cases["SE-BESS-SODIUM-001"]["audit"]["publication_control"] == "MISSING"
    assert cases["SE-ONC-NSQNSCLC-CN-001"]["audit"]["publication_control"] == "MISSING"

    sodium = load_json(ROOT / "cases" / "sodium-ion-bess" / "state-v0.1.json")
    assert any(record["event_date"] != record["knowledge_date"] for record in sodium["records"])
    cml_stop = (ROOT / "cases" / "800vdc" / "stop-v0.1.html").read_text(encoding="utf-8")
    assert "Source event 2026-07-02" in cml_stop
    assert "knowledge time 2026-09-20T10:46:47Z" in cml_stop

    nsclc = load_json(ROOT / "cases" / "nsq-nsclc-china" / "state-v0.1.json")
    assert nsclc["knowledge_cutoff"] == "2026-09-28"
    assert nsclc["patient_specific_success_probability"] == "NOT_ESTABLISHED_STOP"


def validate_medical_boundary() -> None:
    generated = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            DATA / "backfill" / "2026-09-29.json",
            DATA / "weekly" / "2026-W40.json",
            ROOT / "publication" / "weekly" / "2026-W40-publication-manifest.json",
            ROOT / "docs" / "case-watch" / "daily" / "2026-09-29.md",
            ROOT / "docs" / "case-watch" / "weekly" / "2026-W40.md",
        ]
    ).lower()
    prohibited_prescriptive_patterns = [
        "you should take",
        "the patient should take",
        "recommended treatment for this patient",
        "personal success probability is",
        "individual prognosis is",
    ]
    assert not any(pattern in generated for pattern in prohibited_prescriptive_patterns)


def main() -> int:
    checks = [
        ("case registry and IDs", validate_registry),
        ("weekly review schema and gate", validate_weekly),
        ("publication manifest schema and gate", validate_manifest),
        ("search provenance", validate_search_provenance),
        ("protected public/CML/RDL immutability", validate_protected_files),
        ("all intended root/docs and sitemap parity", validate_root_docs_parity),
        ("refreshed baseline and dual-clock semantics", validate_baseline_semantics),
        ("medical public-research boundary", validate_medical_boundary),
    ]
    for label, check in checks:
        check()
        print(f"PASS: {label}")
    count = validate_daily_ledgers()
    print(f"PASS: daily schema, duplicate, dual-clock, and no-public-mutation checks ({count} observations)")
    print(f"PASS: {len(checks) + 1} case-watch validation groups")
    return 0


if __name__ == "__main__":
    sys.exit(main())
