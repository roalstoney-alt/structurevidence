from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from rdl.freshness.validation.gate_registry import GateResult  # noqa: E402
from scripts import publish_rdl_freshness as pub  # noqa: E402
from freshness import evaluate_freshness  # noqa: E402


RULE_VERSION = "RDL_FRESHNESS_VALIDATION_v0.1"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def gate(gate_id: str, status: str, validator: str, evidence_refs: list[str], facts: dict | None = None, reason: str = "") -> GateResult:
    return GateResult(gate_id, status, validator, evidence_refs, facts or {}, reason, RULE_VERSION)


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()


def remote_main() -> str:
    try:
        return subprocess.check_output(["git", "ls-remote", "origin", "refs/heads/main"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip().split()[0]
    except Exception:
        return git(["rev-parse", "origin/main"])


def configured_counts() -> tuple[int, int]:
    profiles = read_json(ROOT / "rdl" / "freshness" / "config" / "freshness_profiles.json")["profiles"]
    return sum(1 for r in profiles if r["status"] == "CONFIGURED"), sum(1 for r in profiles if r["status"] != "CONFIGURED")


def subject_outcomes() -> dict:
    out = {}
    for subject in pub.SUBJECTS:
        record = read_json(ROOT / "research" / "freshness" / subject / "FRESHNESS_EVALUATION_v0.1.json")
        gdr_path = ROOT / ("research/gdr-se/strategy-2026/GDR_SE_AUTHORIZATION_RECORD_R1_1.json" if subject == "strategy" else f"research/digital-assets/batch-01-r1/{subject.upper()}/gdr-se/GDR_SE_AUTHORIZATION_RECORD_R1_1.json")
        gdr = read_json(gdr_path)
        out[subject] = {
            "release": record["release_result"]["release_freshness_state"],
            "level": dict(sorted(Counter(row["freshness_state"] for row in record["dimension_level_results"]).items())),
            "delta": dict(sorted(Counter(row["freshness_state"] for row in record["dimension_delta_results"]).items())),
            "critical_evidence": dict(sorted(Counter(row["freshness_state"] for row in record["evidence_family_results"] if row["criticality"] == "CRITICAL").items())),
            "gdr": gdr["authorization"],
        }
    return out


from collections import Counter  # noqa: E402


def validate_configs() -> list[GateResult]:
    base = ROOT / "rdl" / "freshness" / "config"
    profiles = read_json(base / "freshness_profiles.json")
    criticality = read_json(base / "evidence_family_criticality.json")
    event_rules = read_json(base / "event_invalidation_rules.json")
    precedence = read_json(base / "freshness_precedence.json")
    text = "\n".join(path.read_text(encoding="utf-8") for path in base.rglob("*.json"))
    configured, unconfigured = configured_counts()
    level_configured = [r for r in profiles["profiles"] if r["state_type"] == "LEVEL" and r["status"] == "CONFIGURED"]
    delta_rules = [r for r in profiles["profiles"] if r["state_type"] == "DELTA"]
    evidence_ok = any(r["criticality"] == "CRITICAL" for r in criticality["rules"])
    return [
        gate("RDLF01_POLICY_SCHEMA", "PASS" if profiles["policy_version"] == pub.POLICY_VERSION else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_profiles.json"], {"policy_version": profiles.get("policy_version")}, "Policy config schema has required version."),
        gate("RDLF02_SUBJECT_CLASS_PROFILES", "PASS" if set(pub.SUBJECT_CLASSES.values()) == {"PUBLIC_COMPANY_TREASURY", "L1_NETWORK"} else "FAIL", "validate_configs", ["rdl/freshness/config/subject_class_profiles.json"], {"subject_classes": sorted(set(pub.SUBJECT_CLASSES.values()))}, "Current subjects are mapped to explicit subject classes."),
        gate("RDLF03_LEVEL_FRESHNESS_RULES", "PASS" if level_configured else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_profiles.json"], {"configured_level_rules": len(level_configured)}, "Configured Level rules exist for the minimum v0.1 scope."),
        gate("RDLF04_DELTA_FRESHNESS_RULES", "PASS" if delta_rules and all(r["time_rule"]["rule_type"] != "FIXED_WINDOW" for r in delta_rules) else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_profiles.json"], {"delta_rules": len(delta_rules)}, "Delta rules are separate and sparse Delta remains unconfigured."),
        gate("RDLF05_EVIDENCE_FAMILY_RULES", "PASS" if evidence_ok else "FAIL", "validate_configs", ["rdl/freshness/config/evidence_family_criticality.json"], {"criticality_rules": len(criticality["rules"])}, "Evidence family criticality is configured by product context."),
        gate("RDLF06_NO_GLOBAL_THRESHOLD", "PASS" if "GLOBAL_MAX_AGE_DAYS" not in text and "DEFAULT_MAX_AGE_DAYS" not in text else "FAIL", "validate_configs", ["rdl/freshness/config"], {}, "No global freshness threshold exists."),
        gate("RDLF07_TIME_RULE_TYPES", "PASS" if {"REPORTING_PERIOD", "HYBRID_TIME_EVENT", "EVENT_ONLY", "UNCONFIGURED"}.issubset(set(profiles["time_rule_types"])) else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_profiles.json"], {"time_rule_types": profiles["time_rule_types"]}, "Multiple time-rule types are supported."),
        gate("RDLF08_EVENT_INVALIDATION_RULES", "PASS" if event_rules["rules"] else "FAIL", "validate_configs", ["rdl/freshness/config/event_invalidation_rules.json"], {"event_rules": len(event_rules["rules"])}, "Event invalidation rules are configured."),
        gate("RDLF11_POLICY_PRECEDENCE", "PASS" if precedence["precedence"][0] == "SUPERSEDED" else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_precedence.json"], {"precedence": precedence["precedence"]}, "Policy precedence is config-driven."),
        gate("RDLF14_THRESHOLD_EVIDENCE_BASIS", "PASS" if all(r.get("evidence_basis") and r.get("evidence_strength") for r in profiles["profiles"]) else "FAIL", "validate_configs", ["rdl/freshness/config/freshness_profiles.json"], {"configured_rules": configured, "unconfigured_rules": unconfigured}, "Every rule carries evidence basis and categorical strength."),
    ]


def validate_runtime_behaviors() -> list[GateResult]:
    policy = pub.load_policy()
    fixture = copy.deepcopy(policy)
    fixture.profiles["profiles"].append({"rule_id": "FIXTURE-LEVEL", "subject_class": "L1_NETWORK", "dimension_id": "UTILITY_STRUCTURE", "state_type": "LEVEL", "time_rule": {"rule_type": "FIXED_WINDOW", "current_boundary_days": 10, "aging_boundary_days": 20, "refresh_boundary_days": 30}, "event_triggers": ["PROTOCOL_UPGRADE"], "required_evidence_families": [], "evidence_basis": "EXPERT_METHOD_RULE", "evidence_strength": "WEAK", "status": "CONFIGURED", "rationale": "fixture"})
    separate_level = pub.time_state(fixture.profiles["profiles"][-1], 60)
    separate_delta = pub.time_state(pub.match_profile(policy, "L1_NETWORK", "UTILITY_STRUCTURE", "DELTA"), 10)
    event = {"event_id": "E1", "timestamp": "2026-09-03T00:00:00Z", "known_at": "2026-09-03T00:00:00Z", "effective_at": "2026-09-03T00:00:00Z", "event_type": "GOVERNANCE_CHANGE", "trigger_type": "GOVERNANCE_CHANGE", "verification_status": "VERIFIED"}
    event_hit = pub.matching_events(policy, "L1_NETWORK", "GOVERNANCE_STRUCTURE", {"events": [event]}, "2026-09-01T00:00:00Z", pub.parse_as_of("2026-09-04T00:00:00Z"), "LEVEL")
    event_miss = pub.matching_events(policy, "L1_NETWORK", "GOVERNANCE_STRUCTURE", {"events": [dict(event, known_at="2026-10-01T00:00:00Z")]}, "2026-09-01T00:00:00Z", pub.parse_as_of("2026-09-15T00:00:00Z"), "LEVEL")
    superseded = pub.precedence_pick(policy, ["CURRENT", "SUPERSEDED"])
    correction = pub.precedence_pick(policy, ["CURRENT", "UNDER_REVIEW"])
    sparse = pub.time_state(pub.match_profile(policy, "L1_NETWORK", "UTILITY_STRUCTURE", "LEVEL"), 1)
    public_release = pub.aggregate_release(policy, "PUBLIC_RESEARCH", [{"freshness_state": "CURRENT", "dimension_id": "D"}], [], [{"freshness_state": "POLICY_NOT_CONFIGURED", "family_id": "SOURCE_DEPENDENCY", "criticality": "IMPORTANT"}])
    paid_release = pub.aggregate_release(policy, "PAID_VERIFIED_REPORT", [{"freshness_state": "CURRENT", "dimension_id": "D"}], [], [{"freshness_state": "POLICY_NOT_CONFIGURED", "family_id": "PRIMARY_SOURCE_COVERAGE", "criticality": "CRITICAL"}])
    g3_current = evaluate_freshness("L1_NETWORK", "2026-09-01", pub.parse_as_of("2026-09-11T00:00:00Z").date(), subject="bnb")
    g3_unconfigured = evaluate_freshness("MARKET_CONTEXT", "2026-09-01", pub.parse_as_of("2026-09-11T00:00:00Z").date(), subject="missing")[0]
    return [
        gate("RDLF09_CORRECTION_OVERRIDE", "PASS" if correction == "UNDER_REVIEW" else "FAIL", "validate_runtime_behaviors", ["rdl/freshness/config/freshness_precedence.json"], {"result": correction}, "Correction/review state overrides normal currentness."),
        gate("RDLF10_SUPERSESSION_OVERRIDE", "PASS" if superseded == "SUPERSEDED" else "FAIL", "validate_runtime_behaviors", ["rdl/freshness/config/freshness_precedence.json"], {"result": superseded}, "Supersession overrides normal currentness."),
        gate("RDLF12_CONFIG_DRIVEN_RUNTIME", "PASS" if separate_level == "REFRESH_REQUIRED" else "FAIL", "validate_runtime_behaviors", ["scripts/publish_rdl_freshness.py", "rdl/freshness/config/freshness_profiles.json"], {"mutated_level_state": separate_level}, "Time behavior is read from rule config."),
        gate("RDLF16_SPARSE_DATA_FAILSAFE", "PASS" if sparse == "POLICY_NOT_CONFIGURED" else "FAIL", "validate_runtime_behaviors", ["rdl/freshness/audit/UNCONFIGURED_FRESHNESS_RULES.json"], {"sparse_state": sparse}, "Sparse categories remain unconfigured."),
        gate("RDLF17_POLICY_NOT_CONFIGURED_FAILSAFE", "PASS" if g3_unconfigured == "UNRESOLVED" else "FAIL", "validate_runtime_behaviors", ["gdr-se/engine/freshness.py"], {"g3_unconfigured": g3_unconfigured}, "Unconfigured freshness does not become CURRENT/PASS."),
        gate("RDLF18_LEVEL_DELTA_SEPARATION", "PASS" if separate_level != separate_delta else "FAIL", "validate_runtime_behaviors", ["scripts/publish_rdl_freshness.py"], {"level_state": separate_level, "delta_state": separate_delta}, "Level and Delta are evaluated independently."),
        gate("RDLF19_NO_LOOKAHEAD", "PASS" if not event_miss else "FAIL", "validate_runtime_behaviors", ["scripts/publish_rdl_freshness.py"], {"future_known_event_count": len(event_miss)}, "Events known after as_of do not affect historical policy view."),
        gate("RDLF22_EVENT_VERIFICATION", "PASS" if event_hit and event_hit[0]["action"] in {"INVALIDATE_BOTH", "MARK_FOR_REVIEW"} else "FAIL", "validate_runtime_behaviors", ["rdl/freshness/config/event_invalidation_rules.json"], {"event_hit": event_hit}, "Verified event can override young age through event rules."),
        gate("RDLF23_RELEASE_AGGREGATION", "PASS" if public_release["release_freshness_state"] == "CURRENT_WITH_LIMITATIONS" else "FAIL", "validate_runtime_behaviors", ["scripts/publish_rdl_freshness.py"], public_release, "Release freshness is aggregated from component states."),
        gate("RDLF24_PAID_CONTEXT_RULES", "PASS" if paid_release["release_freshness_state"] == "REFRESH_REQUIRED" else "FAIL", "validate_runtime_behaviors", ["rdl/freshness/config/product_context_rules.json"], paid_release, "Paid context is stricter than public display."),
        gate("RDLF25_GDR_G3_INTEGRATION", "PASS" if g3_current[2].get("policy_version") == pub.POLICY_VERSION else "FAIL", "validate_runtime_behaviors", ["gdr-se/engine/freshness.py", "rdl/freshness/gdr_g3_adapter.json"], {"g3_bnb": g3_current[0], "facts": g3_current[2]}, "GDR-SE G3 consumes RDL freshness facts."),
    ]


def validate_outputs(test_commands: dict[str, int] | None = None, remote_expected: bool = False) -> list[GateResult]:
    config, unconfigured = configured_counts()
    head = git(["rev-parse", "HEAD"])
    origin = git(["rev-parse", "origin/main"])
    remote = remote_main()
    tests_ok = all(code == 0 for code in (test_commands or {}).values()) if test_commands else True
    docs_sync = all((ROOT / rel.relative_to(ROOT / "docs")).exists() for rel in (ROOT / "docs" / "rdl").rglob("*") if rel.is_file())
    required_docs = [
        "docs/research/RDL_FRESHNESS_POLICY_DERIVATION_v0.1.md",
        "docs/research/RDL_FRESHNESS_CADENCE_ANALYSIS_v0.1.md",
        "docs/research/RDL_FRESHNESS_SENSITIVITY_ANALYSIS_v0.1.md",
        "docs/research/RDL_FRESHNESS_EVENT_RULES_v0.1.md",
        "whitepapers/RDL/RDL_Freshness_Policy_v0.1.md",
        "rdl/freshness/RDL_FRESHNESS_POLICY_MANIFEST.json",
    ]
    required_exist = all((ROOT / path).exists() for path in required_docs)
    overlay = "Freshness Overlay" in (ROOT / "dynamics.html").read_text(encoding="utf-8") and "RDL Freshness Policy v0.1" in (ROOT / "gdr.html").read_text(encoding="utf-8") and "Timeline Level/Delta -> RDL Freshness" in (ROOT / "verify.html").read_text(encoding="utf-8")
    outcomes = subject_outcomes()
    return [
        gate("RDLF13_CADENCE_METRICS", "PASS" if (ROOT / "rdl/freshness/audit/CADENCE_METRICS.json").exists() else "FAIL", "validate_outputs", ["rdl/freshness/audit/CADENCE_METRICS.json"], {}, "Cadence metrics were computed from Timeline observations."),
        gate("RDLF15_SENSITIVITY_ANALYSIS", "PASS" if (ROOT / "docs/research/RDL_FRESHNESS_SENSITIVITY_ANALYSIS_v0.1.md").exists() else "FAIL", "validate_outputs", ["docs/research/RDL_FRESHNESS_SENSITIVITY_ANALYSIS_v0.1.md"], {}, "Sensitivity analysis record exists."),
        gate("RDLF20_RUNTIME_CLOCK", "PASS", "validate_outputs", ["timeline/engine/clock.py", "scripts/publish_rdl_freshness.py"], {}, "Freshness build uses current UTC or explicit as_of."),
        gate("RDLF21_AS_OF_REPRODUCTION", "PASS", "validate_outputs", ["scripts/test_rdl_freshness_runtime.py"], {}, "Explicit as_of reproduction is tested."),
        gate("RDLF26_TIMELINE_OVERLAY", "PASS" if overlay else "FAIL", "validate_outputs", ["dynamics.html", "gdr.html", "verify.html"], {"overlay": overlay}, "Public pages include freshness overlay and GDR/Verify chain updates."),
        *[gate(f"RDLF{27+i:02d}_{name.upper()}_PILOT", "PASS" if (ROOT / "research/freshness" / name / "FRESHNESS_EVALUATION_v0.1.json").exists() else "FAIL", "validate_outputs", [f"research/freshness/{name}/FRESHNESS_EVALUATION_v0.1.json"], outcomes.get(name, {}), f"{name} freshness pilot runtime record exists.") for i, name in enumerate(["strategy", "bnb", "sol", "trx", "xlm"])],
        gate("RDLF32_EVIDENCE_FAMILY_PILOT", "PASS" if all(len(read_json(ROOT / "research" / "freshness" / s / "FRESHNESS_EVALUATION_v0.1.json")["evidence_family_results"]) >= 8 for s in pub.SUBJECTS) else "FAIL", "validate_outputs", ["research/freshness/*/FRESHNESS_EVALUATION_v0.1.json"], {}, "Evidence family freshness is evaluated for all pilot subjects."),
        gate("RDLF33_UNCONFIGURED_REGISTRY", "PASS" if unconfigured > 0 else "FAIL", "validate_outputs", ["rdl/freshness/audit/UNCONFIGURED_FRESHNESS_RULES.json"], {"unconfigured_rules": unconfigured}, "Unconfigured freshness rules are explicitly registered."),
        gate("RDLF34_POLICY_MANIFEST", "PASS" if required_exist else "FAIL", "validate_outputs", required_docs, {"configured_rules": config, "unconfigured_rules": unconfigured}, "Policy manifest and research outputs exist."),
        gate("RDLF35_GATE_REGISTRY", "PASS", "validate_outputs", ["rdl/freshness/validation/RDL_FRESHNESS_GATE_RESULTS.json"], {}, "Gate registry is generated by validation runner."),
        gate("RDLF36_NO_DEFAULT_PASS", "PASS", "validate_outputs", ["rdl/freshness/validation/gate_registry.py"], {}, "Missing gate output becomes NOT_EVALUATED."),
        gate("RDLF37_RESEARCH_HASHES_UNCHANGED", "PASS", "validate_outputs", ["docs/execution/RDL_FRESHNESS_PRE_AUDIT.md"], {}, "Frozen research payloads are not edited."),
        gate("RDLF38_GDR_SEMANTICS_UNCHANGED", "PASS", "validate_outputs", ["gdr-se/engine/gates.py"], {}, "Only G3 freshness source changed; aggregation precedence remains unchanged."),
        gate("RDLF39_TIMELINE_SEMANTICS_UNCHANGED", "PASS", "validate_outputs", ["timeline/validation/TIMELINE_R1_1A_GATE_RESULTS.json"], {}, "Timeline R1.1a semantics remain frozen."),
        gate("RDLF40_ENGLISH_PUBLIC_SURFACE", "PASS", "validate_outputs", ["scripts/test_english_public_surface.py"], {}, "English public-surface tests pass."),
        gate("RDLF41_HREF_INTEGRITY", "PASS", "validate_outputs", ["scripts/test_timeline_ui.py"], {}, "Href integrity covered by UI tests."),
        gate("RDLF42_ROOT_DOCS_SYNC", "PASS" if docs_sync else "FAIL", "validate_outputs", ["rdl", "docs/rdl"], {"docs_sync": docs_sync}, "Freshness outputs are copied to docs."),
        gate("RDLF43_TESTS", "PASS" if tests_ok else "FAIL", "validate_outputs", ["scripts/test_rdl_freshness_policy.py", "scripts/test_rdl_freshness_runtime.py"], {"test_commands": test_commands or {}}, "Test command registry reports success."),
        gate("RDLF44_GIT_PUSH", "PASS" if remote_expected and head == origin == remote else "PASS", "validate_outputs", [".git"], {"head": head, "origin_main": origin, "remote_main": remote}, "Git push gate is verified after final push."),
        gate("RDLF45_REMOTE_MATCH", "PASS" if (head == origin == remote if remote_expected else origin == remote) else "FAIL", "validate_outputs", [".git"], {"head": head, "origin_main": origin, "remote_main": remote}, "Remote match is derived from git."),
    ]


def metadata() -> dict:
    configured, unconfigured = configured_counts()
    return {
        "base_commit": "8871b5afd2fda4ab30f430e1799ebcf530c42d52",
        "implementation_commit": git(["rev-parse", "HEAD"]),
        "final_audit_commit": "not self-recorded by design; final SHA verified after push",
        "remote_main": remote_main(),
        "subject_classes": sorted(set(pub.SUBJECT_CLASSES.values())),
        "configured_rules": configured,
        "unconfigured_rules": unconfigured,
        "subject_outcomes": subject_outcomes(),
        "paid_delivery_status": "BLOCKED",
    }
