from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
RESOLUTIONS = {"DAY", "WEEK", "MONTH"}
STRUCTURAL_STATES = {"STRENGTHENING", "WEAKENING", "STABLE", "TENSION", "MIXED", "STRUCTURAL_SHIFT", "INSUFFICIENT_DATA", "NO_OBSERVATION"}
EVIDENCE_STATES = {"NOT_OBSERVED", "OBSERVED", "PARTIAL", "COMPLETE", "UNRESOLVED", "UNDER_REVIEW", "SUPERSEDED", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED"}
EVENT_DOMAINS = {"SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"}
FORBIDDEN_EVIDENCE_STATES = {"FRESH", "AGING", "STALE"}


def fail(message: str) -> None:
    raise SystemExit(f"TIMELINE_R1_MODEL_TEST_FAIL: {message}")


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest() -> str:
    h = hashlib.sha256()
    for path in sorted((ROOT / "timeline").rglob("*.json")):
        h.update(path.relative_to(ROOT).as_posix().encode())
        h.update(path.read_bytes())
    return h.hexdigest()


def load_builder():
    spec = importlib.util.spec_from_file_location("timeline_builder", ROOT / "scripts" / "build_timeline_model.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["timeline_builder"] = module
    spec.loader.exec_module(module)
    return module


def test_fixture_engines() -> None:
    builder = load_builder()
    rules = builder.structural_aggregation_rules()
    if builder.resolve_structural_state(["STRENGTHENING", "WEAKENING"], rules) != "MIXED":
        fail("conflicting structural effects did not resolve to MIXED")
    mutated = json.loads(json.dumps(rules))
    mutated["conflict_pairs"][0]["result"] = "STRUCTURAL_SHIFT"
    if builder.resolve_structural_state(["STRENGTHENING", "WEAKENING"], mutated) != "STRUCTURAL_SHIFT":
        fail("aggregation config mutation did not alter output")
    fixture = [
        {"observation_id": "TL-FIX-O1", "subject_id": "FIX", "dimension_ids": ["SUPPLY_STRUCTURE"], "effective_at": "2026-09-01T00:00:00Z", "structural_effect": "STRENGTHENING", "artifact_refs": ["fixture"], "source_refs": ["fixture"]},
        {"observation_id": "TL-FIX-O2", "subject_id": "FIX", "dimension_ids": ["SUPPLY_STRUCTURE"], "effective_at": "2026-09-02T00:00:00Z", "structural_effect": "WEAKENING", "artifact_refs": ["fixture"], "source_refs": ["fixture"]},
        {"observation_id": "TL-FIX-O3", "subject_id": "FIX", "dimension_ids": ["SUPPLY_STRUCTURE"], "effective_at": "2026-09-09T00:00:00Z", "structural_effect": "STRENGTHENING", "artifact_refs": ["fixture"], "source_refs": ["fixture"]},
        {"observation_id": "TL-FIX-O4", "subject_id": "FIX", "dimension_ids": ["SUPPLY_STRUCTURE"], "effective_at": "2026-09-20T00:00:00Z", "structural_effect": "STRENGTHENING", "artifact_refs": ["fixture"], "source_refs": ["fixture"]},
    ]
    day = builder.build_day_buckets("fix", fixture, ["SUPPLY_STRUCTURE"], rules)
    if len([row for row in day if row["observation_count"]]) != 4:
        fail("fixture DAY active date bucket count is wrong")
    if any(row["date"] in {"2026-09-03", "2026-09-04"} and row["state"] != "NO_OBSERVATION" for row in day):
        fail("structural no-forward-fill rule failed")
    week = builder.aggregate_structural_day_to_week("fix", day, rules)
    month = builder.aggregate_structural_week_to_month("fix", week, rules)
    if len(week) >= len(day) or len(month) >= len(week):
        fail("fixture resolutions were copied instead of aggregated")


def main() -> None:
    test_fixture_engines()
    for subject in SUBJECTS:
        structural = read(ROOT / "timeline" / "subjects" / f"{subject}_structural_timeline.json")
        evidence = read(ROOT / "timeline" / "subjects" / f"{subject}_evidence_timeline.json")
        atomic = read(ROOT / "timeline" / "atomic" / f"{subject}_atomic_observations.json")["observations"]
        day = read(ROOT / "timeline" / "subjects" / f"{subject}_structural_day.json")["buckets"]
        week = read(ROOT / "timeline" / "subjects" / f"{subject}_structural_week.json")["buckets"]
        month = read(ROOT / "timeline" / "subjects" / f"{subject}_structural_month.json")["buckets"]
        ev_day = read(ROOT / "timeline" / "subjects" / f"{subject}_evidence_day.json")["buckets"]
        ev_week = read(ROOT / "timeline" / "subjects" / f"{subject}_evidence_week.json")["buckets"]
        ev_month = read(ROOT / "timeline" / "subjects" / f"{subject}_evidence_month.json")["buckets"]
        ledger = read(ROOT / "timeline" / "subjects" / f"{subject}_event_ledger.json")
        manifest = read(ROOT / "timeline" / "subjects" / f"{subject}_timeline_derivation_manifest.json")

        if structural["model_version"] != "TIMELINE_MODEL_R1" or evidence["model_version"] != "TIMELINE_MODEL_R1":
            fail(f"wrong model version for {subject}")
        if set(structural["supported_resolutions"]) != RESOLUTIONS or set(evidence["supported_resolutions"]) != RESOLUTIONS:
            fail(f"missing resolutions for {subject}")
        if not atomic:
            fail(f"missing atomic observations for {subject}")
        if {obs["knowledge_mode"] for obs in atomic} - {"CONTEMPORANEOUS", "RETROSPECTIVE"}:
            fail(f"invalid knowledge mode for {subject}")
        if any(obs["known_at"] < obs["effective_at"] and obs["effective_at"] != "UNKNOWN" for obs in atomic):
            fail(f"known_at precedes effective_at for {subject}")
        if any(row["state"] not in STRUCTURAL_STATES for row in day + week + month):
            fail(f"invalid structural state for {subject}")
        if any((row["closing_state"] in FORBIDDEN_EVIDENCE_STATES or row["policy_state"] != "POLICY_NOT_CONFIGURED") for row in ev_day + ev_week + ev_month):
            fail(f"premature freshness policy state for {subject}")
        if any(row["closing_state"] not in EVIDENCE_STATES for row in ev_day + ev_week + ev_month):
            fail(f"invalid evidence state for {subject}")
        if any(event["event_domain"] not in EVENT_DOMAINS for event in ledger["events"]):
            fail(f"invalid event domain for {subject}")
        dim_sets = {dim["dimension_id"]: {tuple(row["observations"]) for row in day if row["dimension_id"] == dim["dimension_id"] and row["observations"]} for dim in structural["dimensions"]}
        if len({repr(value) for value in dim_sets.values()}) <= 1 and len(dim_sets) > 1:
            fail(f"all dimensions share identical observation sets for {subject}")
        active_day = [row for row in day if row["observation_count"]]
        if len(active_day) > 1 and (json.dumps(day, sort_keys=True) == json.dumps(week, sort_keys=True) or json.dumps(week, sort_keys=True) == json.dumps(month, sort_keys=True)):
            fail(f"resolution copy detected for {subject}")
        for row in month:
            if row["observation_count"] and not (row["lineage"]["week_bucket_ids"] and row["lineage"]["day_bucket_ids"] and row["lineage"]["atomic_observation_ids"] and row["lineage"]["artifact_refs"]):
                fail(f"broken structural lineage for {subject}")
        for row in ev_month:
            if row["events_count"] and not (row["lineage"]["week_bucket_ids"] and row["lineage"]["day_bucket_ids"] and row["lineage"]["evidence_event_ids"] and row["lineage"]["artifact_refs"]):
                fail(f"broken evidence lineage for {subject}")
        if manifest["atomic_observation_count"] != len(atomic) or not manifest["timeline_input_bundle_sha256"]:
            fail(f"bad derivation manifest for {subject}")
        if any(row["phase"] == structural["current_structural_state"] for row in structural["phase_ribbon"]):
            fail(f"phase ribbon copied current structural state for {subject}")

    before = digest()
    subprocess.run([sys.executable, "-B", "scripts/build_timeline_model.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = digest()
    if before != after:
        fail("timeline generation is not deterministic")
    print("TIMELINE_R1_MODEL_TESTS_PASS")


if __name__ == "__main__":
    main()
