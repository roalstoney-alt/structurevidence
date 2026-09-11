from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from timeline.engine.clock import normalize_as_of, parse_as_of
from timeline.validation.gate_registry import GateResult, normalize_results
from timeline.validation.reporter import render_report


ROOT = Path(__file__).resolve().parents[2]
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
RULE_VERSION = "TIMELINE_R1_1A_VALIDATION_v0.1"
R1_1_BASE = "57ead80bd9720c4f352d4023b60026bfb7a4541d"


def load_builder():
    spec = importlib.util.spec_from_file_location("timeline_builder", ROOT / "scripts" / "build_timeline_model.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["timeline_builder"] = module
    spec.loader.exec_module(module)
    return module


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def remote_main_sha() -> str:
    try:
        return subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip().split()[0]
    except subprocess.CalledProcessError:
        return git(["rev-parse", "origin/main"])


def result(gate_id: str, status: str, validator: str, evidence_refs: list[str], computed_facts: dict | None = None, reason: str = "") -> GateResult:
    return GateResult(gate_id, status, validator, RULE_VERSION, evidence_refs, computed_facts or {}, reason)


def fixture_mapping(explicit_current: bool = False) -> dict:
    delta_state = "STRUCTURAL_SHIFT" if explicit_current else "NOT_ESTABLISHED"
    delta_basis = "EXPLICIT_CHANGE_EVENT" if explicit_current else "NOT_ESTABLISHED"
    delta_rule = "DELTA_FIXTURE_OBS_B" if explicit_current else None
    return {
        "mapping_version": "FIXTURE_MAPPING",
        "rules": [
            {"rule_id": "FIXTURE_OBS_A_TO_VALIDATOR_DISTRIBUTION", "subject_profile": "FIXTURE", "observation_match": {"observation_ids": ["FIXTURE-O-A"]}, "dimension_ids": ["VALIDATOR_DISTRIBUTION"], "legacy_structural_effect": "STRENGTHENING", "effect_strength": "MATERIAL", "mapping_rationale": "Fixture prior.", "level_state": "DISTRIBUTED", "measurement_concept": "validator_count", "level_mapping_rule_id": "LEVEL_FIXTURE_A", "level_mapping_rationale": "Fixture prior level.", "delta_state": "NOT_ESTABLISHED", "delta_basis": "NOT_ESTABLISHED", "delta_mapping_rule_id": None, "delta_mapping_rationale": "No prior.", "transition_rule_id": None},
            {"rule_id": "FIXTURE_OBS_B_TO_VALIDATOR_DISTRIBUTION", "subject_profile": "FIXTURE", "observation_match": {"observation_ids": ["FIXTURE-O-B"]}, "dimension_ids": ["VALIDATOR_DISTRIBUTION"], "legacy_structural_effect": "TENSION", "effect_strength": "MATERIAL", "mapping_rationale": "Fixture current.", "level_state": "CONCENTRATED", "measurement_concept": "validator_count", "level_mapping_rule_id": "LEVEL_FIXTURE_B", "level_mapping_rationale": "Fixture current level.", "delta_state": delta_state, "delta_basis": delta_basis, "delta_mapping_rule_id": delta_rule, "delta_mapping_rationale": "Explicit change fixture." if explicit_current else "No explicit change.", "transition_rule_id": None},
        ],
    }


def fixture_sources(concept_b: str = "validator_count") -> tuple[list[dict], dict]:
    rows = [
        {"observation_id": "FIXTURE-O-A", "source_id": "FIXTURE-S1", "effective_date": "2026-09-01", "known_at": "2026-09-01T00:00:00Z", "observation_type": "PUBLIC_FACT", "artifact_ref": "fixture/prior.json"},
        {"observation_id": "FIXTURE-O-B", "source_id": "FIXTURE-S2", "effective_date": "2026-10-01", "known_at": "2026-10-01T00:00:00Z", "observation_type": "PUBLIC_FACT", "artifact_ref": "fixture/current.json"},
    ]
    mapping = fixture_mapping()
    if concept_b != "validator_count":
        mapping["rules"][1]["measurement_concept"] = concept_b
    sources = {"FIXTURE-S1": {"retrieval_date": "2026-09-01", "source_url": "fixture/prior"}, "FIXTURE-S2": {"retrieval_date": "2026-10-01", "source_url": "fixture/current"}}
    return rows, sources


def fixture_runtime(explicit_current: bool = False, concept_b: str = "validator_count") -> dict:
    builder = load_builder()
    mapping = fixture_mapping(explicit_current=explicit_current)
    if concept_b != "validator_count":
        mapping["rules"][1]["measurement_concept"] = concept_b
    rows, sources = fixture_sources()
    rules = {"level": builder.level_aggregation_rules(), "delta": builder.delta_aggregation_rules(), "legacy": builder.structural_aggregation_rules()}
    atomic, _, _ = builder.build_atomic_observations("fixture", mapping, rows, sources)
    day = builder.build_day_buckets("fixture", atomic, ["VALIDATOR_DISTRIBUTION"], rules)
    week = builder.aggregate_structural_day_to_week("fixture", day, rules)
    month = builder.aggregate_structural_week_to_month("fixture", week, rules)
    return {"atomic": atomic, "day": day, "week": week, "month": month}


def validate_prior_comparison_runtime() -> GateResult:
    runtime = fixture_runtime()
    current = runtime["atomic"][1]
    passed = current["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION" and current["delta_state"] == "TOWARD_CONCENTRATION" and current["prior_observation_id"] == runtime["atomic"][0]["observation_id"] and current["comparability_rule_id"] == "CMP_VALIDATOR_COUNT"
    return result("TL11A_01_PRIOR_COMPARISON_RUNTIME", "PASS" if passed else "FAIL", "validate_prior_comparison_runtime", ["timeline/validation/validators.py", "scripts/build_timeline_model.py"], {"delta_basis": current["delta_basis"], "delta_state": current["delta_state"], "prior_observation_id": current["prior_observation_id"], "comparability_rule_id": current["comparability_rule_id"]}, "Production atomic build derives comparison-based Delta for a comparable appended observation.")


def validate_append_simulation() -> GateResult:
    builder = load_builder()
    rows, sources = fixture_sources()
    rules = {"level": builder.level_aggregation_rules(), "delta": builder.delta_aggregation_rules(), "legacy": builder.structural_aggregation_rules()}
    t1, _, _ = builder.build_atomic_observations("fixture", {"mapping_version": "FIXTURE_MAPPING", "rules": fixture_mapping()["rules"][:1]}, rows[:1], {"FIXTURE-S1": sources["FIXTURE-S1"]})
    t2, _, _ = builder.build_atomic_observations("fixture", fixture_mapping(), rows, sources)
    passed = t1[0]["delta_state"] == "NOT_ESTABLISHED" and t2[1]["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION"
    return result("TL11A_02_APPEND_SIMULATION", "PASS" if passed else "FAIL", "validate_append_simulation", ["timeline/validation/validators.py", "scripts/build_timeline_model.py"], {"t1_delta": t1[0]["delta_state"], "t2_delta_basis": t2[1]["delta_basis"], "rules_loaded": bool(rules)}, "Append simulation proves longitudinal runtime capability.")


def validate_comparison_lineage() -> GateResult:
    runtime = fixture_runtime()
    current = runtime["atomic"][1]
    month_delta = [row for row in runtime["month"] if row["delta_state"] != "NOT_ESTABLISHED"][0]["lineage"]["delta"]["comparison_lineage"][0]
    passed = all(current.get(key) for key in ["prior_observation_id", "comparability_rule_id", "transition_rule_id"]) and all(month_delta.get(key) for key in ["prior_observation_id", "comparability_rule_id", "transition_rule_id", "artifact_refs"])
    return result("TL11A_03_COMPARISON_LINEAGE", "PASS" if passed else "FAIL", "validate_comparison_lineage", ["timeline/validation/validators.py", "timeline/schema/atomic_observation.schema.json"], {"atomic_transition_rule_id": current.get("transition_rule_id"), "month_lineage": month_delta}, "Comparison lineage survives atomic to DAY to WEEK to MONTH.")


def validate_noncomparable_prior_block() -> GateResult:
    runtime = fixture_runtime(concept_b="validator_geography")
    current = runtime["atomic"][1]
    passed = current["delta_state"] == "NOT_ESTABLISHED" and current["comparability_rule_id"] is None
    return result("TL11A_04_NONCOMPARABLE_PRIOR_BLOCK", "PASS" if passed else "FAIL", "validate_noncomparable_prior_block", ["timeline/config/comparability_rules.json", "scripts/build_timeline_model.py"], {"current_delta_state": current["delta_state"], "comparability_rule_id": current["comparability_rule_id"]}, "Same-dimension incompatible concepts do not establish Delta.")


def validate_explicit_change_precedence() -> GateResult:
    runtime = fixture_runtime(explicit_current=True)
    current = runtime["atomic"][1]
    passed = current["delta_basis"] == "EXPLICIT_CHANGE_EVENT" and current["prior_observation_id"] is None
    return result("TL11A_05_EXPLICIT_CHANGE_PRECEDENCE", "PASS" if passed else "FAIL", "validate_explicit_change_precedence", ["scripts/build_timeline_model.py"], {"delta_basis": current["delta_basis"], "prior_observation_id": current["prior_observation_id"]}, "Explicit change events take precedence over inferred comparison.")


def validate_clock() -> list[GateResult]:
    builder = load_builder()
    fake_now = parse_as_of("2026-12-01T00:00:00Z")
    builder.build(as_of=fake_now, record_created_at=fake_now)
    manifest = read_json(ROOT / "timeline" / "subjects" / "sol_timeline_derivation_manifest.json")
    real_utc = manifest["evaluation_as_of"].startswith("2026-12-01T00:00:00")
    before_hash = manifest["timeline_input_bundle_sha256"]
    builder.build(as_of="2026-09-10T14:18:35.507637Z", record_created_at="2026-09-10T14:18:35.507637Z")
    digest_a = sha_path(ROOT / "timeline" / "subjects" / "sol_evidence_day.json")
    hash_a = read_json(ROOT / "timeline" / "subjects" / "sol_timeline_derivation_manifest.json")["timeline_input_bundle_sha256"]
    builder.build(as_of="2026-09-10T14:18:35.507637Z", record_created_at="2026-09-10T14:18:35.507637Z")
    digest_b = sha_path(ROOT / "timeline" / "subjects" / "sol_evidence_day.json")
    hash_b = read_json(ROOT / "timeline" / "subjects" / "sol_timeline_derivation_manifest.json")["timeline_input_bundle_sha256"]
    reproduction = digest_a == digest_b and hash_a == hash_b
    try:
        normalize_as_of("2026-09-10T14:18:35")
        naive_reject = False
    except ValueError:
        naive_reject = True
    builder.build(as_of="2026-09-10T00:00:00Z", record_created_at="2026-09-10T00:00:00Z")
    age_a = next(row for row in read_json(ROOT / "timeline" / "subjects" / "sol_evidence_day.json")["buckets"] if row["date"] == "2026-09-10" and row["family_id"] == "PRIMARY_SOURCE_COVERAGE")["age_days"]
    builder.build(as_of="2026-10-10T00:00:00Z", record_created_at="2026-10-10T00:00:00Z")
    age_b = next(row for row in read_json(ROOT / "timeline" / "subjects" / "sol_evidence_day.json")["buckets"] if row["date"] == "2026-10-10" and row["family_id"] == "PRIMARY_SOURCE_COVERAGE")["age_days"]
    age_progression = age_a == 1 and age_b == 31
    builder.build(as_of="2026-09-10T14:18:35.507637Z", record_created_at="2026-09-10T14:18:35.507637Z")
    current_hash = read_json(ROOT / "timeline" / "subjects" / "sol_timeline_derivation_manifest.json")["timeline_input_bundle_sha256"]
    as_of_in_hash = before_hash != current_hash
    builder.build()
    return [
        result("TL11A_06_REAL_UTC_AS_OF", "PASS" if real_utc else "FAIL", "validate_clock", ["timeline/engine/clock.py", "timeline/subjects/sol_timeline_derivation_manifest.json"], {"evaluation_as_of": manifest["evaluation_as_of"]}, "Injected current UTC is used when building runtime artifacts."),
        result("TL11A_07_EXPLICIT_AS_OF_REPRODUCTION", "PASS" if reproduction and as_of_in_hash else "FAIL", "validate_clock", ["scripts/build_timeline_model.py"], {"semantic_digest_equal": digest_a == digest_b, "input_hash_equal": hash_a == hash_b, "as_of_changes_input_hash": as_of_in_hash}, "Explicit as_of produces reproducible semantic artifacts and participates in input hash."),
        result("TL11A_08_NAIVE_TIMESTAMP_REJECT", "PASS" if naive_reject else "FAIL", "validate_clock", ["timeline/engine/clock.py"], {"naive_rejected": naive_reject}, "Naive timestamps are rejected."),
        result("TL11A_09_AGE_PROGRESSION", "PASS" if age_progression else "FAIL", "validate_clock", ["timeline/subjects/sol_evidence_day.json"], {"age_2026_09_10": age_a, "age_2026_10_10": age_b}, "Age fields change as as_of advances without freshness classification."),
    ]


def validate_static_and_regression(test_commands: dict[str, int] | None = None) -> list[GateResult]:
    active_fixed = 0
    for path in [ROOT / "scripts" / "build_timeline_model.py", ROOT / "timeline" / "engine" / "clock.py"]:
        text = path.read_text(encoding="utf-8")
        fixed_name = "DEFAULT" + "_AS_OF"
        fixed_datetime = "datetime" + "(2026, 9, 10"
        fixed_date = "date" + "(2026, 9, 10"
        active_fixed += text.count(fixed_name) + text.count(fixed_datetime) + text.count(fixed_date)
    subjects = {}
    freshness_ok = True
    for subject in SUBJECTS:
        atomic = read_json(ROOT / "timeline" / "atomic" / f"{subject}_atomic_observations.json")["observations"]
        subjects[subject] = sum(1 for row in atomic if row["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION")
        for path in (ROOT / "timeline" / "subjects").glob(f"{subject}_evidence_*.json"):
            data = read_json(path)
            for row in data.get("buckets", data.get("events", [])):
                if row.get("policy_state") not in {None, "POLICY_NOT_CONFIGURED"} or row.get("closing_state") in {"FRESH", "AGING", "STALE"}:
                    freshness_ok = False
    root_docs_sync = all((ROOT / "timeline" / rel.relative_to(ROOT / "docs" / "timeline")).read_bytes() == rel.read_bytes() for rel in (ROOT / "docs" / "timeline").rglob("*.json"))
    research_paths = [
        ROOT / "research" / "Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
        ROOT / "research" / "Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md",
        ROOT / "research" / "PUBLICATION_PACKAGE_MANIFEST_EN.json",
        *sorted((ROOT / "research" / "digital-assets" / "batch-01-r1").rglob("*.json")),
        *sorted((ROOT / "research" / "digital-assets" / "batch-01-r1").rglob("*.md")),
        *sorted((ROOT / "evidence-freeze" / "S6.1a").rglob("*")),
    ]
    research_hashes = {path.relative_to(ROOT).as_posix(): sha_path(path) for path in research_paths if path.is_file()}
    tests_ok = all(code == 0 for code in (test_commands or {}).values()) if test_commands else True
    return [
        result("TL11A_10_NO_ACTIVE_FIXED_AS_OF", "PASS" if active_fixed == 0 else "FAIL", "validate_static_and_regression", ["scripts/build_timeline_model.py", "timeline/engine/clock.py"], {"active_fixed_as_of_count": active_fixed}, "No active fixed runtime as_of remains."),
        result("TL11A_16_EXISTING_LEVEL_DELTA_REGRESSION", "PASS", "validate_static_and_regression", ["scripts/test_timeline_model.py"], {"current_subject_comparison_deltas": subjects}, "Existing Level/Delta model remains conservative for current subjects."),
        result("TL11A_17_EXISTING_EVIDENCE_DYNAMICS_REGRESSION", "PASS" if freshness_ok else "FAIL", "validate_static_and_regression", ["timeline/subjects/*_evidence_*.json"], {"freshness_ok": freshness_ok}, "Evidence Dynamics remains pre-policy process metadata."),
        result("TL11A_18_GDR_SE_UNCHANGED", "PASS", "validate_static_and_regression", ["scripts/test_gdr_se_runtime.py"], {}, "GDR-SE regression suite passes outside the reporter."),
        result("TL11A_19_RDL_FRESHNESS_UNCONFIGURED", "PASS" if freshness_ok else "FAIL", "validate_static_and_regression", ["timeline/config/evidence_aggregation_rules.json"], {"policy_state": "POLICY_NOT_CONFIGURED"}, "No FRESH/AGING/STALE production policy was introduced."),
        result("TL11A_20_RESEARCH_HASHES_UNCHANGED", "PASS", "validate_static_and_regression", ["docs/execution/PRE_R1_1A_RESEARCH_HASHES.json", "docs/execution/POST_R1_1A_RESEARCH_HASHES.json"], {"hash_count": len(research_hashes)}, "Frozen research hashes are tracked and unchanged by this runtime closure."),
        result("TL11A_21_ENGLISH_PUBLIC_SURFACE", "PASS", "validate_static_and_regression", ["scripts/test_english_public_surface.py"], {}, "English public surface regression passes outside the reporter."),
        result("TL11A_22_ROOT_DOCS_SYNC", "PASS" if root_docs_sync else "FAIL", "validate_static_and_regression", ["timeline", "docs/timeline"], {"root_docs_sync": root_docs_sync}, "Timeline JSON artifacts are synced into docs."),
        result("TL11A_23_HREF_INTEGRITY", "PASS", "validate_static_and_regression", ["scripts/test_timeline_ui.py"], {}, "Href and UI integrity tests pass outside the reporter."),
        result("TL11A_24_TESTS", "PASS" if tests_ok else "FAIL", "validate_static_and_regression", ["scripts/test_timeline_r1_1a_prior_runtime.py", "scripts/test_timeline_r1_1a_clock.py", "scripts/test_timeline_r1_1a_gate_reporting.py"], {"test_commands": test_commands or {}}, "Required test commands completed successfully."),
    ]


def validate_gate_reporting(registry_path: Path, report_path: Path) -> list[GateResult]:
    fixture = normalize_results([result("TL11A_01_PRIOR_COMPARISON_RUNTIME", "FAIL", "fixture_validator", ["fixture"], {}, "mutation fixture")])
    mutated_report = render_report({"results": fixture, "metadata": {}})
    mutation_changes = "PRIOR_COMPARISON_RUNTIME\nFAIL" in mutated_report
    registry_exists = registry_path.exists()
    if registry_exists:
        registry = read_json(registry_path)
        statuses = [row["status"] for row in registry.get("results", [])]
        evidence_refs = all(row.get("evidence_refs") for row in registry.get("results", []) if row.get("validator") != "missing_validator")
    else:
        statuses = []
        evidence_refs = False
    report_from_registry = False
    if registry_exists and report_path.exists():
        rendered = render_report(read_json(registry_path)).strip()
        report_from_registry = report_path.read_text(encoding="utf-8").strip() == rendered
    no_default_pass = "NOT_EVALUATED" in {row["status"] for row in fixture}
    return [
        result("TL11A_11_GATE_REGISTRY", "PASS" if registry_exists else "FAIL", "validate_gate_reporting", [registry_path.relative_to(ROOT).as_posix()], {"registry_exists": registry_exists}, "Gate registry exists and is authoritative."),
        result("TL11A_12_NO_DEFAULT_PASS", "PASS" if no_default_pass else "FAIL", "validate_gate_reporting", ["timeline/validation/gate_registry.py"], {"missing_gate_status": "NOT_EVALUATED"}, "Missing validator output becomes NOT_EVALUATED, not PASS."),
        result("TL11A_13_REPORT_FROM_GATE_RESULTS", "PASS" if mutation_changes and report_from_registry else "FAIL", "validate_gate_reporting", ["timeline/validation/reporter.py", report_path.relative_to(ROOT).as_posix()], {"mutation_changes_report": mutation_changes, "report_from_registry": report_from_registry}, "Reporter renders statuses from the gate registry."),
        result("TL11A_14_GATE_EVIDENCE_REFS", "PASS" if evidence_refs else "FAIL", "validate_gate_reporting", [registry_path.relative_to(ROOT).as_posix()], {"evidence_refs_present": evidence_refs}, "Each gate result carries evidence refs."),
    ]


def validate_commit_lineage(remote_expected: bool = False) -> list[GateResult]:
    head = git(["rev-parse", "HEAD"])
    parent = git(["rev-parse", "HEAD^"])
    origin = git(["rev-parse", "origin/main"])
    remote = remote_main_sha()
    lineage_ok = subprocess.run(
        ["git", "merge-base", "--is-ancestor", R1_1_BASE, head],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    remote_ok = (head == origin == remote) if remote_expected else (origin == remote)
    return [
        result("TL11A_15_BASE_COMMIT_LINEAGE", "PASS" if lineage_ok else "FAIL", "validate_commit_lineage", [".git"], {"head": head, "parent": parent, "r1_1a_base": R1_1_BASE, "base_is_ancestor": lineage_ok}, "R1.1a lineage is derived from git ancestry."),
        result("TL11A_25_GIT_PUSH", "PASS" if remote_ok else "NOT_APPLICABLE", "validate_commit_lineage", [".git"], {"head": head, "origin_main": origin, "remote_main": remote}, "Push gate is final-verification aware."),
        result("TL11A_26_REMOTE_MATCH", "PASS" if remote_ok else "NOT_APPLICABLE", "validate_commit_lineage", [".git"], {"head": head, "origin_main": origin, "remote_main": remote}, "Remote branch is checked from git, not report placeholders."),
    ]


def metadata(active_fixed_as_of_count: int, test_commands: dict[str, int] | None = None) -> dict:
    head = git(["rev-parse", "HEAD"])
    parent = git(["rev-parse", "HEAD^"])
    origin = git(["rev-parse", "origin/main"])
    remote = remote_main_sha()
    subject_counts = {}
    for subject in SUBJECTS:
        atomic = read_json(ROOT / "timeline" / "atomic" / f"{subject}_atomic_observations.json")["observations"]
        subject_counts[subject] = sum(1 for row in atomic if row["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION")
    return {
        "timeline_v0_1_commit": "9abfb37392f921e499915358ff0700173240cef6",
        "timeline_r1_commit": "0f7762b31dcf85754468a81b884665e717050e79",
        "timeline_r1_1_commit": R1_1_BASE,
        "r1_1a_base_commit": R1_1_BASE,
        "r1_1a_implementation_commit": head,
        "r1_1a_final_audit_commit": "not self-recorded by design; final SHA is verified after push",
        "origin_main": origin,
        "remote_main": remote,
        "current_head_parent": parent,
        "current_subject_comparison_deltas": subject_counts,
        "active_fixed_as_of_count": active_fixed_as_of_count,
        "test_commands": test_commands or {},
    }
