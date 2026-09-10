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
DELTA_BASES = {"COMPARISON_TO_PRIOR_OBSERVATION", "EXPLICIT_CHANGE_EVENT", "NOT_ESTABLISHED"}
EVIDENCE_STATES = {"NOT_OBSERVED", "OBSERVED", "PARTIAL", "COMPLETE", "UNRESOLVED", "UNDER_REVIEW", "SUPERSEDED", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED"}
EVENT_DOMAINS = {"SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"}
FORBIDDEN_EVIDENCE_STATES = {"FRESH", "AGING", "STALE"}


def fail(message: str) -> None:
    raise SystemExit(f"TIMELINE_R1_1_MODEL_TEST_FAIL: {message}")


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
    rules = {"level": builder.level_aggregation_rules(), "delta": builder.delta_aggregation_rules(), "legacy": builder.structural_aggregation_rules()}
    snapshot = [{"observation_id": "TL-FIX-O1", "subject_id": "FIX", "dimension_ids": ["VALIDATOR_DISTRIBUTION"], "effective_at": "2026-09-01T00:00:00Z", "level_state": "FIXED_OR_RESTRICTED_SET", "delta_state": "NOT_ESTABLISHED", "delta_basis": "NOT_ESTABLISHED", "prior_observation_id": None, "comparability_rule_id": None, "artifact_refs": ["fixture"], "source_refs": ["fixture"]}]
    day = builder.build_day_buckets("fix", snapshot, ["VALIDATOR_DISTRIBUTION"], rules)
    active = [row for row in day if row["observation_count"]][0]
    if active["level_state"] != "FIXED_OR_RESTRICTED_SET" or active["delta_state"] != "NOT_ESTABLISHED":
        fail("single snapshot did not preserve Level while blocking Delta")
    prior = dict(snapshot[0], observation_id="TL-FIX-O0", effective_at="2026-08-01T00:00:00Z", measurement_concept="validator_count")
    current = dict(snapshot[0], observation_id="TL-FIX-O2", effective_at="2026-09-01T00:00:00Z", measurement_concept="validator_count")
    if builder.find_prior_comparable_observation(current, [prior], builder.comparability_rules())["observation_id"] != "TL-FIX-O0":
        fail("prior comparable selector failed")
    non_comparable = dict(prior, measurement_concept="validator_geography")
    if builder.find_prior_comparable_observation(current, [non_comparable], builder.comparability_rules()) is not None:
        fail("non-comparable prior was accepted")
    explicit = [dict(snapshot[0], delta_state="TOWARD_CONTRACTION", delta_basis="EXPLICIT_CHANGE_EVENT")]
    explicit_day = builder.build_day_buckets("fix", explicit, ["VALIDATOR_DISTRIBUTION"], rules)
    if [row for row in explicit_day if row["observation_count"]][0]["delta_basis"] != "EXPLICIT_CHANGE_EVENT":
        fail("explicit change event support failed")
    mutated_level = json.loads(json.dumps(rules))
    mutated_level["level"]["mixed"] = "INSUFFICIENT_DATA"
    if builder.resolve_level_state(["CONCENTRATED", "FIXED_OR_RESTRICTED_SET"], mutated_level["level"]) != "INSUFFICIENT_DATA":
        fail("level config mutation did not change behavior")
    mutated_delta = json.loads(json.dumps(rules))
    mutated_delta["delta"]["mixed"] = "INSUFFICIENT_DATA"
    if builder.resolve_delta_state(["TOWARD_CONTRACTION", "ROLE_WEAKENING"], mutated_delta["delta"]) != "INSUFFICIENT_DATA":
        fail("delta config mutation did not change behavior")


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

        if structural["model_version"] != "TIMELINE_MODEL_R1_1" or evidence["model_version"] != "TIMELINE_MODEL_R1_1":
            fail(f"wrong model version for {subject}")
        if set(structural["supported_resolutions"]) != RESOLUTIONS or set(evidence["supported_resolutions"]) != RESOLUTIONS:
            fail(f"missing resolutions for {subject}")
        if not atomic:
            fail(f"missing atomic observations for {subject}")
        if any("structural_effect" in obs for obs in atomic):
            fail(f"active structural_effect remains in atomic output for {subject}")
        if any("legacy_structural_effect" not in obs for obs in atomic):
            fail(f"missing migration legacy field for {subject}")
        if any(obs["delta_basis"] not in DELTA_BASES for obs in atomic):
            fail(f"invalid delta basis for {subject}")
        if any(obs["delta_basis"] == "NOT_ESTABLISHED" and obs["delta_state"] != "NOT_ESTABLISHED" for obs in atomic):
            fail(f"delta established without basis for {subject}")
        if subject == "sol" and any(obs["delta_state"] != "NOT_ESTABLISHED" for obs in atomic):
            fail("SOL single-date observations should not manufacture Delta")
        for row in day + week + month:
            if "level_state" not in row or "delta_state" not in row or "level_age_days" not in row or "delta_age_days" not in row:
                fail(f"missing Level/Delta bucket field for {subject}")
            if row["delta_state"] == "NOT_ESTABLISHED" and row["delta_age_days"] is not None:
                fail(f"unestablished Delta has age for {subject}")
        if any((row["closing_state"] in FORBIDDEN_EVIDENCE_STATES or row["policy_state"] != "POLICY_NOT_CONFIGURED") for row in ev_day + ev_week + ev_month):
            fail(f"premature freshness policy state for {subject}")
        if any(row["closing_state"] not in EVIDENCE_STATES for row in ev_day + ev_week + ev_month):
            fail(f"invalid evidence state for {subject}")
        if any(event["event_domain"] not in EVENT_DOMAINS for event in ledger["events"]):
            fail(f"invalid event domain for {subject}")
        dim_sets = {dim["dimension_id"]: {tuple(row["level_observation_ids"]) for row in day if row["dimension_id"] == dim["dimension_id"] and row["level_observation_ids"]} for dim in structural["dimensions"]}
        if len({repr(value) for value in dim_sets.values()}) <= 1 and len(dim_sets) > 1:
            fail(f"all dimensions share identical level observation sets for {subject}")
        for row in month:
            if row["observation_count"] and not (row["lineage"]["level"]["week_bucket_ids"] and row["lineage"]["level"]["day_bucket_ids"] and row["lineage"]["level"]["atomic_observation_ids"] and row["lineage"]["level"]["artifact_refs"]):
                fail(f"broken Level lineage for {subject}")
            if row["delta_state"] != "NOT_ESTABLISHED" and not (row["lineage"]["delta"]["week_bucket_ids"] and row["lineage"]["delta"]["day_bucket_ids"] and row["lineage"]["delta"]["comparison_lineage"]):
                fail(f"broken Delta lineage for {subject}")
        if manifest["atomic_observation_count"] != len(atomic) or not manifest["level_mapping_sha256"] or not manifest["delta_mapping_sha256"]:
            fail(f"bad derivation manifest for {subject}")
    before = digest()
    subprocess.run([sys.executable, "-B", "scripts/build_timeline_model.py"], cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    after = digest()
    if before != after:
        fail("timeline generation is not deterministic")
    print("TIMELINE_R1_1_MODEL_TESTS_PASS")


if __name__ == "__main__":
    main()
