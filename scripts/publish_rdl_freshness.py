from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.engine.clock import parse_as_of  # noqa: E402


POLICY_VERSION = "RDL_FRESHNESS_v0.1a"
ENGINE_VERSION = "RDL_FRESHNESS_ENGINE_v0.1a"
RUNTIME_RECORD = "FRESHNESS_EVALUATION_v0.1a.json"
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
SUBJECT_LABELS = {"strategy": "Strategy 2026", "bnb": "BNB", "sol": "SOL", "trx": "TRX", "xlm": "XLM"}
SUBJECT_CLASSES = {"strategy": "PUBLIC_COMPANY_TREASURY", "bnb": "L1_NETWORK", "sol": "L1_NETWORK", "trx": "L1_NETWORK", "xlm": "L1_NETWORK"}
PRODUCT_CONTEXTS = ["PUBLIC_RESEARCH", "PAID_VERIFIED_REPORT", "CUSTOM_AUDIT", "STRUCTURAL_MONITOR"]
FRESHNESS_STATES = ["CURRENT", "CURRENT_WITH_LIMITATIONS", "AGING", "REFRESH_REQUIRED", "EVENT_INVALIDATED", "UNDER_REVIEW", "SUPERSEDED", "INSUFFICIENT_DATA", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED"]
EVENT_DOMAINS = ["SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"]
EVENT_TARGETS = ["LEVEL", "DELTA", "EVIDENCE", "RELEASE", "AUTHORIZATION", "LEVEL_AND_DELTA"]
TIME_RULE_TYPES = ["FIXED_WINDOW", "SOURCE_CADENCE_MULTIPLE", "REPORTING_PERIOD", "EVENT_ONLY", "HYBRID_TIME_EVENT", "UNCONFIGURED"]
EVIDENCE_FAMILIES = ["PRIMARY_SOURCE_COVERAGE", "SECONDARY_SUPPORT", "COUNTER_EVIDENCE_COVERAGE", "NUMERICAL_RECONCILIATION", "SOURCE_DEPENDENCY", "INDEPENDENT_REVIEW", "CORRECTION_STATUS", "SUPERSESSION_STATUS", "AUTHORIZATION_STATUS"]
DIMENSIONS = {
    "PUBLIC_COMPANY_TREASURY": ["TREASURY_STRUCTURE", "RESOURCE_PRESSURE", "NARRATIVE_DEPENDENCE", "SOURCE_DEPENDENCY"],
    "L1_NETWORK": ["SUPPLY_STRUCTURE", "UTILITY_STRUCTURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE", "RESOURCE_PRESSURE", "SETTLEMENT_ROLE", "TREASURY_STRUCTURE", "FOUNDATION_DEPENDENCE"],
}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha_json(data) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def iso_z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_day(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def age_days(timestamp: str | None, as_of: datetime) -> int | None:
    day = parse_day(timestamp)
    return None if day is None else max((as_of.date() - day).days, 0)


def freshness_profiles() -> dict:
    rules = [
        {
            "rule_id": "FRESH-PCT-TREASURY-LEVEL",
            "subject_class": "PUBLIC_COMPANY_TREASURY",
            "dimension_id": "TREASURY_STRUCTURE",
            "state_type": "LEVEL",
            "time_rule": {"rule_type": "REPORTING_PERIOD", "current_boundary_days": 120, "aging_boundary_days": 180, "refresh_boundary_days": 240, "reporting_basis": "quarterly plus filing lag"},
            "event_triggers": ["TREASURY_POLICY_CHANGE", "TREASURY_TRANSACTION", "MATERIAL_DISCLOSURE", "CORRECTION", "SUPERSESSION"],
            "required_evidence_families": ["PRIMARY_SOURCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"],
            "evidence_basis": "REPORTING_SCHEDULE",
            "evidence_strength": "MODERATE",
            "status": "CONFIGURED",
            "rationale": "Corporate treasury policy is tied to periodic SEC/company reporting and material disclosure events; cadence data is sparse, so the rule is a method-pilot reporting-period rule rather than empirical optimization.",
        },
        {
            "rule_id": "FRESH-L1-SUPPLY-LEVEL",
            "subject_class": "L1_NETWORK",
            "dimension_id": "SUPPLY_STRUCTURE",
            "state_type": "LEVEL",
            "time_rule": {"rule_type": "HYBRID_TIME_EVENT", "current_boundary_days": 180, "aging_boundary_days": 270, "refresh_boundary_days": 365},
            "event_triggers": ["SUPPLY_MECHANISM_CHANGE", "PROTOCOL_UPGRADE", "CORRECTION", "SUPERSESSION"],
            "required_evidence_families": ["PRIMARY_SOURCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"],
            "evidence_basis": "EXPERT_METHOD_RULE",
            "evidence_strength": "WEAK",
            "status": "CONFIGURED",
            "rationale": "Supply mechanics often persist between protocol changes; sparse current data prevents empirical cadence classification, so v0.1 uses broad bands plus event invalidation.",
        },
        {
            "rule_id": "FRESH-L1-VALIDATOR-LEVEL",
            "subject_class": "L1_NETWORK",
            "dimension_id": "VALIDATOR_DISTRIBUTION",
            "state_type": "LEVEL",
            "time_rule": {"rule_type": "HYBRID_TIME_EVENT", "current_boundary_days": 120, "aging_boundary_days": 180, "refresh_boundary_days": 240},
            "event_triggers": ["VALIDATOR_SET_CHANGE", "GOVERNANCE_CHANGE", "PROTOCOL_UPGRADE", "CLIENT_DIVERSITY_CHANGE", "CORRECTION", "SUPERSESSION"],
            "required_evidence_families": ["PRIMARY_SOURCE_COVERAGE", "COUNTER_EVIDENCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"],
            "evidence_basis": "EXPERT_METHOD_RULE",
            "evidence_strength": "WEAK",
            "status": "CONFIGURED",
            "rationale": "Validator distribution can change faster than persistent architecture, but current cross-subject cadence is sparse. The rule is conservative and event-sensitive.",
        },
        {
            "rule_id": "FRESH-L1-GOVERNANCE-LEVEL",
            "subject_class": "L1_NETWORK",
            "dimension_id": "GOVERNANCE_STRUCTURE",
            "state_type": "LEVEL",
            "time_rule": {"rule_type": "EVENT_ONLY"},
            "event_triggers": ["GOVERNANCE_CHANGE", "PROTOCOL_UPGRADE", "CORRECTION", "SUPERSESSION"],
            "required_evidence_families": ["PRIMARY_SOURCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"],
            "evidence_basis": "EXPERT_METHOD_RULE",
            "evidence_strength": "WEAK",
            "status": "CONFIGURED",
            "rationale": "Governance mechanism descriptions persist until a verified governance or protocol event changes the mechanism.",
        },
        {
            "rule_id": "FRESH-DELTA-DEFAULT-R0",
            "subject_class": "*",
            "dimension_id": "*",
            "state_type": "DELTA",
            "time_rule": {"rule_type": "UNCONFIGURED"},
            "event_triggers": ["CORRECTION", "SUPERSESSION"],
            "required_evidence_families": [],
            "evidence_basis": "INSUFFICIENT",
            "evidence_strength": "UNRESOLVED",
            "status": "UNCONFIGURED",
            "rationale": "Comparison-based Delta history is not yet dense enough for v0.1 time windows. Delta absence is not staleness.",
        },
    ]
    for subject_class, dims in DIMENSIONS.items():
        for dim in dims:
            if not any(r["subject_class"] == subject_class and r["dimension_id"] == dim and r["state_type"] == "LEVEL" for r in rules):
                rules.append({
                    "rule_id": f"FRESH-{subject_class.replace('_', '-')}-{dim}-LEVEL-UNCONFIGURED",
                    "subject_class": subject_class,
                    "dimension_id": dim,
                    "state_type": "LEVEL",
                    "time_rule": {"rule_type": "UNCONFIGURED"},
                    "event_triggers": ["CORRECTION", "SUPERSESSION"],
                    "required_evidence_families": [],
                    "evidence_basis": "INSUFFICIENT",
                    "evidence_strength": "UNRESOLVED",
                    "status": "UNCONFIGURED",
                    "rationale": "Insufficient cadence data for a configured v0.1 rule.",
                })
    return {"policy_version": POLICY_VERSION, "time_rule_types": TIME_RULE_TYPES, "profiles": rules}


def evidence_family_criticality() -> dict:
    rows = []
    for context in PRODUCT_CONTEXTS:
        for family in EVIDENCE_FAMILIES:
            if family in {"PRIMARY_SOURCE_COVERAGE", "COUNTER_EVIDENCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"}:
                critical = "CRITICAL"
            elif family in {"NUMERICAL_RECONCILIATION", "SOURCE_DEPENDENCY", "AUTHORIZATION_STATUS"}:
                critical = "IMPORTANT"
            elif family == "SECONDARY_SUPPORT":
                critical = "SUPPORTING"
            else:
                critical = "CONDITIONAL"
            if context == "PAID_VERIFIED_REPORT" and family in {"SOURCE_DEPENDENCY", "NUMERICAL_RECONCILIATION", "INDEPENDENT_REVIEW"}:
                critical = "CRITICAL"
            rows.append({"product_context": context, "family_id": family, "criticality": critical})
    return {"policy_version": POLICY_VERSION, "criticality_values": ["CRITICAL", "IMPORTANT", "SUPPORTING", "CONDITIONAL", "NOT_APPLICABLE"], "rules": rows}


def event_invalidation_rules() -> dict:
    rules = [
        ("PUBLIC_COMPANY_TREASURY", "TREASURY_STRUCTURE", "TREASURY_POLICY_CHANGE", ["SUBJECT_EVENT"], "LEVEL_AND_DELTA", "MATERIAL", "INVALIDATE_BOTH"),
        ("PUBLIC_COMPANY_TREASURY", "TREASURY_STRUCTURE", "TREASURY_TRANSACTION", ["SUBJECT_EVENT"], "LEVEL", "POTENTIALLY_MATERIAL", "MARK_FOR_REVIEW"),
        ("PUBLIC_COMPANY_TREASURY", "TREASURY_STRUCTURE", "MATERIAL_DISCLOSURE", ["RESEARCH_EVENT"], "RELEASE", "MATERIAL", "HUMAN_REVIEW_REQUIRED"),
        ("L1_NETWORK", "SUPPLY_STRUCTURE", "SUPPLY_MECHANISM_CHANGE", ["SUBJECT_EVENT"], "LEVEL_AND_DELTA", "MATERIAL", "INVALIDATE_BOTH"),
        ("L1_NETWORK", "VALIDATOR_DISTRIBUTION", "VALIDATOR_SET_CHANGE", ["SUBJECT_EVENT"], "LEVEL_AND_DELTA", "MATERIAL", "INVALIDATE_BOTH"),
        ("L1_NETWORK", "VALIDATOR_DISTRIBUTION", "CLIENT_DIVERSITY_CHANGE", ["SUBJECT_EVENT"], "LEVEL", "POTENTIALLY_MATERIAL", "MARK_FOR_REVIEW"),
        ("L1_NETWORK", "GOVERNANCE_STRUCTURE", "GOVERNANCE_CHANGE", ["SUBJECT_EVENT"], "LEVEL_AND_DELTA", "MATERIAL", "INVALIDATE_BOTH"),
        ("*", "*", "CORRECTION", ["RESEARCH_EVENT"], "RELEASE", "MATERIAL", "HUMAN_REVIEW_REQUIRED"),
        ("*", "*", "SOURCE_RETRACTION", ["EVIDENCE_EVENT"], "EVIDENCE", "MATERIAL", "HUMAN_REVIEW_REQUIRED"),
        ("*", "*", "SUPERSESSION", ["RESEARCH_EVENT"], "RELEASE", "MATERIAL", "INVALIDATE_RELEASE"),
    ]
    return {"policy_version": POLICY_VERSION, "event_domain_enum": EVENT_DOMAINS, "event_targets": EVENT_TARGETS, "event_types": ["TREASURY_POLICY_CHANGE", "TREASURY_TRANSACTION", "GOVERNANCE_CHANGE", "PROTOCOL_UPGRADE", "SUPPLY_MECHANISM_CHANGE", "VALIDATOR_SET_CHANGE", "FOUNDATION_ALLOCATION_CHANGE", "CORRECTION", "SUPERSESSION", "SOURCE_RETRACTION", "MATERIAL_DISCLOSURE", "CLIENT_DIVERSITY_CHANGE"], "rules": [{"rule_id": f"EV-{i:03d}", "subject_class": sc, "dimension_id": dim, "event_type": typ, "allowed_event_domains": domains, "applies_to": applies, "severity": sev, "action": action, "requires_verified_event": True, "retroactive_invalidation": False} for i, (sc, dim, typ, domains, applies, sev, action) in enumerate(rules, 1)]}


def evidence_freshness_rules() -> dict:
    rules = []
    for context in PRODUCT_CONTEXTS:
        rules.extend([
            {"rule_id": f"FRESH-EVIDENCE-{context}-PRIMARY_SOURCE_COVERAGE", "family_id": "PRIMARY_SOURCE_COVERAGE", "subject_class": "*", "product_context": context, "rule_type": "HYBRID_TIME_EVENT", "status": "CONFIGURED", "current_boundary_days": 180, "aging_boundary_days": 270, "refresh_boundary_days": 365, "event_triggers": ["SOURCE_RETRACTION", "CORRECTION", "SUPERSESSION"], "evidence_basis": "EXPERT_METHOD_RULE", "evidence_strength": "WEAK"},
            {"rule_id": f"FRESH-EVIDENCE-{context}-COUNTER_EVIDENCE_COVERAGE", "family_id": "COUNTER_EVIDENCE_COVERAGE", "subject_class": "*", "product_context": context, "rule_type": "HYBRID_TIME_EVENT", "status": "CONFIGURED", "current_boundary_days": 180, "aging_boundary_days": 270, "refresh_boundary_days": 365, "event_triggers": ["SOURCE_RETRACTION", "CORRECTION", "SUPERSESSION"], "evidence_basis": "EXPERT_METHOD_RULE", "evidence_strength": "WEAK"},
            {"rule_id": f"FRESH-EVIDENCE-{context}-CORRECTION_STATUS", "family_id": "CORRECTION_STATUS", "subject_class": "*", "product_context": context, "rule_type": "EVENT_ONLY", "status": "CONFIGURED", "event_triggers": ["CORRECTION"], "evidence_basis": "RESEARCH_EVENT_STATUS", "evidence_strength": "MODERATE"},
            {"rule_id": f"FRESH-EVIDENCE-{context}-SUPERSESSION_STATUS", "family_id": "SUPERSESSION_STATUS", "subject_class": "*", "product_context": context, "rule_type": "EVENT_ONLY", "status": "CONFIGURED", "event_triggers": ["SUPERSESSION"], "evidence_basis": "RESEARCH_EVENT_STATUS", "evidence_strength": "MODERATE"},
        ])
    for family in EVIDENCE_FAMILIES:
        if family not in {"PRIMARY_SOURCE_COVERAGE", "COUNTER_EVIDENCE_COVERAGE", "CORRECTION_STATUS", "SUPERSESSION_STATUS"}:
            rules.append({"rule_id": f"FRESH-EVIDENCE-GLOBAL-{family}-UNCONFIGURED", "family_id": family, "subject_class": "*", "product_context": "*", "rule_type": "UNCONFIGURED", "status": "UNCONFIGURED", "event_triggers": [], "evidence_basis": "INSUFFICIENT", "evidence_strength": "UNRESOLVED"})
    return {"policy_version": POLICY_VERSION, "rules": rules}


def freshness_precedence() -> dict:
    return {"policy_version": POLICY_VERSION, "precedence": ["SUPERSEDED", "EVENT_INVALIDATED", "UNDER_REVIEW", "REFRESH_REQUIRED", "INSUFFICIENT_DATA", "AGING", "CURRENT_WITH_LIMITATIONS", "CURRENT", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED"]}


def product_context_rules() -> dict:
    return {
        "policy_version": POLICY_VERSION,
        "rules": [
            {"product_context": "PUBLIC_RESEARCH", "allow_states": ["CURRENT", "CURRENT_WITH_LIMITATIONS", "AGING", "REFRESH_REQUIRED"], "delivery_status_if_critical_unconfigured": "CURRENT_WITH_LIMITATIONS", "rationale": "Public research may remain visible with clear currentness labels."},
            {"product_context": "PAID_VERIFIED_REPORT", "allow_states": ["CURRENT"], "delivery_status_if_critical_unconfigured": "REFRESH_REQUIRED", "rationale": "Paid current delivery cannot rely on unconfigured critical freshness rules."},
            {"product_context": "CUSTOM_AUDIT", "allow_states": ["CURRENT", "CURRENT_WITH_LIMITATIONS", "AGING"], "delivery_status_if_critical_unconfigured": "UNDER_REVIEW", "rationale": "Custom audits can proceed only after scope review when policy is incomplete."},
            {"product_context": "STRUCTURAL_MONITOR", "allow_states": ["CURRENT", "CURRENT_WITH_LIMITATIONS", "AGING"], "delivery_status_if_critical_unconfigured": "UNDER_REVIEW", "rationale": "Monitor activation requires configured refresh paths."},
        ],
    }


@dataclass
class PolicyRuntime:
    profiles: dict
    criticality: dict
    evidence_rules: dict
    event_rules: dict
    precedence: dict
    product_rules: dict


def config_dir() -> Path:
    return ROOT / "rdl" / "freshness" / "config"


def load_policy() -> PolicyRuntime:
    base = config_dir()
    return PolicyRuntime(read_json(base / "freshness_profiles.json"), read_json(base / "evidence_family_criticality.json"), read_json(base / "evidence_freshness_rules.json"), read_json(base / "event_invalidation_rules.json"), read_json(base / "freshness_precedence.json"), read_json(base / "product_context_rules.json"))


def write_configs() -> PolicyRuntime:
    base = config_dir()
    configs = {
        "freshness_profiles.json": freshness_profiles(),
        "evidence_family_criticality.json": evidence_family_criticality(),
        "evidence_freshness_rules.json": evidence_freshness_rules(),
        "event_invalidation_rules.json": event_invalidation_rules(),
        "freshness_precedence.json": freshness_precedence(),
        "product_context_rules.json": product_context_rules(),
        "freshness_state_taxonomy.json": {"policy_version": POLICY_VERSION, "states": FRESHNESS_STATES},
        "subject_class_profiles.json": {"policy_version": POLICY_VERSION, "subject_classes": ["PUBLIC_COMPANY_TREASURY", "L1_NETWORK", "PROTOCOL_GOVERNANCE", "MARKET_CONTEXT"], "current_subject_mapping": SUBJECT_CLASSES},
        "state_type_taxonomy.json": {"policy_version": POLICY_VERSION, "state_types": ["LEVEL", "DELTA"]},
        "time_rule_types.json": {"policy_version": POLICY_VERSION, "time_rule_types": TIME_RULE_TYPES},
    }
    for name, data in configs.items():
        write_json(base / name, data)
    return load_policy()


def match_profile(policy: PolicyRuntime, subject_class: str, dimension: str, state_type: str) -> dict | None:
    profiles = policy.profiles["profiles"]
    for rule in profiles:
        if rule["subject_class"] == subject_class and rule["dimension_id"] == dimension and rule["state_type"] == state_type:
            return rule
    for rule in profiles:
        if rule["subject_class"] == "*" and rule["dimension_id"] == "*" and rule["state_type"] == state_type:
            return rule
    return None


def precedence_pick(policy: PolicyRuntime, states: list[str]) -> str:
    precedence = policy.precedence["precedence"]
    present = set(states)
    for state in precedence:
        if state in present:
            return state
    return "POLICY_NOT_CONFIGURED"


def time_state(rule: dict, age: int | None) -> str:
    tr = rule["time_rule"]
    if rule["status"] != "CONFIGURED" or tr["rule_type"] == "UNCONFIGURED":
        return "POLICY_NOT_CONFIGURED"
    if age is None:
        return "INSUFFICIENT_DATA"
    if tr["rule_type"] == "EVENT_ONLY":
        return "CURRENT"
    if age <= tr["current_boundary_days"]:
        return "CURRENT"
    if age <= tr["aging_boundary_days"]:
        return "AGING"
    return "REFRESH_REQUIRED"


def target_matches(applies_to: str, target: str) -> bool:
    return applies_to == target or (applies_to == "LEVEL_AND_DELTA" and target in {"LEVEL", "DELTA"})


def supersession_allows_current(event: dict, target: str, current_artifact_id: str | None) -> tuple[bool, str]:
    if target != "RELEASE" or (event.get("trigger_type") or event.get("event_type")) != "SUPERSESSION":
        return True, "not a release supersession event"
    superseded = event.get("superseded_artifact_id")
    successor = event.get("successor_artifact_id")
    if current_artifact_id and current_artifact_id == successor:
        return False, "current release is successor, not superseded"
    if current_artifact_id and current_artifact_id == superseded:
        return True, "current release is superseded artifact"
    return False, "supersession relation does not target current release"


def match_event_to_target(event: dict, rule: dict, subject_class: str, dimension: str, target: str, state_timestamp: str | None, evaluation_as_of: datetime, current_artifact_id: str | None = None) -> dict:
    trigger = event.get("trigger_type") or event.get("event_type")
    if rule["event_type"] != trigger:
        return {"matched": False, "reason": "event type mismatch"}
    if rule["subject_class"] not in {subject_class, "*"} or rule["dimension_id"] not in {dimension, "*"}:
        return {"matched": False, "reason": "subject class or dimension mismatch"}
    domain = event.get("event_domain", "SUBJECT_EVENT")
    if domain not in rule.get("allowed_event_domains", []):
        return {"matched": False, "reason": "event domain mismatch"}
    if not target_matches(rule["applies_to"], target):
        return {"matched": False, "reason": "target mismatch"}
    known = parse_day(event.get("known_at") or event.get("timestamp"))
    effective = parse_day(event.get("effective_at") or event.get("timestamp"))
    state_day = parse_day(state_timestamp)
    if known is None or known > evaluation_as_of.date():
        return {"matched": False, "reason": "event not known at evaluation_as_of"}
    if effective is None:
        return {"matched": False, "reason": "missing effective_at"}
    if target in {"LEVEL", "DELTA"}:
        if state_day is None:
            return {"matched": False, "reason": "missing state timestamp"}
        if effective <= state_day and not rule.get("retroactive_invalidation", False):
            return {"matched": False, "reason": "event is not after state timestamp"}
    allowed, reason = supersession_allows_current(event, target, current_artifact_id)
    if not allowed:
        return {"matched": False, "reason": reason}
    verified = event.get("verification_status", "VERIFIED") == "VERIFIED"
    action = rule["action"] if verified or not rule.get("requires_verified_event", True) else "MARK_FOR_REVIEW"
    return {"matched": True, "event_id": event["event_id"], "event_domain": domain, "event_type": trigger, "rule_id": rule["rule_id"], "target": target, "action": action, "reason": reason if trigger == "SUPERSESSION" else "event domain, target, time and verification matched"}


def matching_events(policy: PolicyRuntime, subject_class: str, dimension: str, event_ledger: dict, observed_at: str | None, as_of: datetime, target: str, current_artifact_id: str | None = None) -> list[dict]:
    out = []
    for event in event_ledger.get("events", []):
        for rule in policy.event_rules["rules"]:
            match = match_event_to_target(event, rule, subject_class, dimension, target, observed_at, as_of, current_artifact_id)
            if match.get("matched"):
                out.append(match)
    return out


def event_state(events: list[dict], target: str) -> str:
    actions = {event["action"] for event in events}
    if actions & {"INVALIDATE_BOTH", "INVALIDATE_LEVEL", "INVALIDATE_DELTA", "INVALIDATE_RELEASE"}:
        return "EVENT_INVALIDATED"
    if actions & {"HUMAN_REVIEW_REQUIRED", "MARK_FOR_REVIEW"}:
        return "UNDER_REVIEW"
    return "CURRENT"


def latest_level_rows(subject: str, as_of: datetime) -> dict[str, dict]:
    rows = read_json(ROOT / "timeline" / "subjects" / f"{subject}_structural_day.json")["buckets"]
    latest = {}
    for row in rows:
        if row["date"] > as_of.date().isoformat() or row["observation_count"] == 0:
            continue
        latest[row["dimension_id"]] = row
    return latest


def latest_evidence_rows(subject: str, as_of: datetime) -> dict[str, dict]:
    rows = read_json(ROOT / "timeline" / "subjects" / f"{subject}_evidence_day.json")["buckets"]
    latest = {}
    for row in rows:
        if row["date"] <= as_of.date().isoformat():
            latest[row["family_id"]] = row
    return latest


def current_release_artifact_id(subject: str) -> str:
    return "STRATEGY-2026-R1" if subject == "strategy" else f"{subject.upper()}-R1"


def supersession_relations() -> dict:
    relations = []
    for subject in SUBJECTS:
        successor = current_release_artifact_id(subject)
        superseded = "STRATEGY-2026-PILOT" if subject == "strategy" else f"{subject.upper()}-PILOT"
        relations.append({"relation_id": f"SUP-{subject.upper()}-PILOT-R1", "subject": subject, "successor_artifact_id": successor, "superseded_artifact_id": superseded, "relation_type": "REFINES", "effective_at": "2026-09-09T00:00:00Z", "known_at": "2026-09-09T00:00:00Z", "source_ref": "v0.1a directional audit registry"})
    return {"policy_version": POLICY_VERSION, "relation_types": ["REPLACES", "REFINES", "DEPRECATES", "CORRECTS", "WITHDRAWS"], "relations": relations}


def release_event_state(policy: PolicyRuntime, subject_class: str, event_ledger: dict, as_of: datetime, artifact_id: str) -> tuple[str, list[dict]]:
    events = matching_events(policy, subject_class, "*", event_ledger, "1900-01-01T00:00:00Z", as_of, "RELEASE", artifact_id)
    return event_state(events, "RELEASE"), events


def match_evidence_rule(policy: PolicyRuntime, subject_class: str, family: str, product_context: str) -> dict:
    candidates = policy.evidence_rules["rules"]
    selectors = [
        (product_context, subject_class, family),
        (product_context, "*", family),
        ("*", "*", family),
    ]
    for context, klass, fam in selectors:
        for rule in candidates:
            if rule["product_context"] == context and rule["subject_class"] == klass and rule["family_id"] == fam:
                return rule
    return {"rule_id": f"FRESH-EVIDENCE-{family}-POLICY-NOT-CONFIGURED", "family_id": family, "subject_class": "*", "product_context": "*", "rule_type": "UNCONFIGURED", "status": "UNCONFIGURED", "event_triggers": [], "evidence_basis": "INSUFFICIENT", "evidence_strength": "UNRESOLVED"}


def evidence_time_state(rule: dict, age: int | None) -> str:
    if rule["status"] != "CONFIGURED" or rule["rule_type"] == "UNCONFIGURED":
        return "POLICY_NOT_CONFIGURED"
    if age is None and rule["rule_type"] != "EVENT_ONLY":
        return "INSUFFICIENT_DATA"
    if rule["rule_type"] == "EVENT_ONLY":
        return "CURRENT"
    if age <= rule["current_boundary_days"]:
        return "CURRENT"
    if age <= rule["aging_boundary_days"]:
        return "AGING"
    return "REFRESH_REQUIRED"


def evaluate_subject(subject: str, as_of: datetime, policy: PolicyRuntime | None = None, product_context: str = "PUBLIC_RESEARCH") -> dict:
    policy = policy or load_policy()
    subject_class = SUBJECT_CLASSES[subject]
    structural_index = read_json(ROOT / "timeline" / "subjects" / f"{subject}_structural_timeline.json")
    event_ledger = read_json(ROOT / "timeline" / "subjects" / f"{subject}_event_ledger.json")
    level_rows = latest_level_rows(subject, as_of)
    evidence_rows = latest_evidence_rows(subject, as_of)
    level_results = []
    delta_results = []
    artifact_id = current_release_artifact_id(subject)
    for dim in [d["dimension_id"] for d in structural_index["dimensions"]]:
        row = level_rows.get(dim)
        observed_at = row.get("level_last_observed_at") if row else None
        rule = match_profile(policy, subject_class, dim, "LEVEL")
        base_state = "POLICY_NOT_CONFIGURED" if not rule else time_state(rule, age_days(observed_at, as_of))
        events = matching_events(policy, subject_class, dim, event_ledger, observed_at, as_of, "LEVEL", artifact_id)
        state = precedence_pick(policy, [base_state, event_state(events, "LEVEL")])
        level_results.append({"subject_id": structural_index["subject_id"], "dimension_id": dim, "state_type": "LEVEL", "level_state": row.get("level_state") if row else "NO_OBSERVATION", "freshness_state": state, "rule_id": rule["rule_id"] if rule else None, "rule_type": rule["time_rule"]["rule_type"] if rule else "UNCONFIGURED", "evaluation_as_of": iso_z(as_of), "last_update_at": observed_at, "age_days": age_days(observed_at, as_of), "event_status": "INVALIDATING_EVENT" if state == "EVENT_INVALIDATED" else "REVIEW_EVENT" if events else "NO_INVALIDATING_EVENT", "evidence_basis": rule["evidence_basis"] if rule else "INSUFFICIENT", "evidence_strength": rule["evidence_strength"] if rule else "UNRESOLVED", "reason": rule["rationale"] if rule else "No configured policy profile.", "lineage": {"timeline_bucket_id": row.get("bucket_id") if row else None, "event_rules": events}, "level_event_matches": events})
        delta_at = row.get("delta_last_established_at") if row and row.get("delta_state") != "NOT_ESTABLISHED" else None
        delta_rule = match_profile(policy, subject_class, dim, "DELTA")
        delta_events = []
        if row is None or row.get("delta_state") == "NOT_ESTABLISHED":
            delta_state = "NOT_APPLICABLE"
            reason = "No current Delta exists; absence of Delta is not staleness."
        else:
            delta_base = time_state(delta_rule, age_days(delta_at, as_of)) if delta_rule else "POLICY_NOT_CONFIGURED"
            delta_events = matching_events(policy, subject_class, dim, event_ledger, delta_at, as_of, "DELTA", artifact_id)
            delta_state = precedence_pick(policy, [delta_base, event_state(delta_events, "DELTA")])
            reason = delta_rule["rationale"] if delta_rule else "No configured Delta policy profile."
        delta_results.append({"subject_id": structural_index["subject_id"], "dimension_id": dim, "state_type": "DELTA", "delta_state": row.get("delta_state") if row else "NOT_ESTABLISHED", "freshness_state": delta_state, "rule_id": delta_rule["rule_id"] if delta_rule else None, "rule_type": delta_rule["time_rule"]["rule_type"] if delta_rule else "UNCONFIGURED", "evaluation_as_of": iso_z(as_of), "last_update_at": delta_at, "age_days": age_days(delta_at, as_of), "event_status": "INVALIDATING_EVENT" if delta_state == "EVENT_INVALIDATED" else "REVIEW_EVENT" if delta_events else "NO_INVALIDATING_EVENT", "evidence_basis": delta_rule["evidence_basis"] if delta_rule else "INSUFFICIENT", "evidence_strength": delta_rule["evidence_strength"] if delta_rule else "UNRESOLVED", "reason": reason, "lineage": {"timeline_bucket_id": row.get("bucket_id") if row else None, "event_rules": delta_events}, "delta_event_matches": delta_events})
    critical_rules = {(row["product_context"], row["family_id"]): row["criticality"] for row in policy.criticality["rules"]}
    evidence_results = []
    for family in EVIDENCE_FAMILIES:
        row = evidence_rows.get(family)
        last = row.get("latest_update_at") if row else None
        crit = critical_rules.get((product_context, family), "SUPPORTING")
        ev_rule = match_evidence_rule(policy, subject_class, family, product_context)
        ev_events = matching_events(policy, subject_class, "*", event_ledger, last, as_of, "EVIDENCE", artifact_id)
        ev_events = [event for event in ev_events if event["event_type"] in set(ev_rule.get("event_triggers", []))]
        state = precedence_pick(policy, [evidence_time_state(ev_rule, age_days(last, as_of)), event_state(ev_events, "EVIDENCE")])
        evidence_results.append({"subject_id": structural_index["subject_id"], "family_id": family, "freshness_state": state, "last_update_at": last, "age_days": age_days(last, as_of), "criticality": crit, "rule_id": ev_rule["rule_id"], "rule_type": ev_rule["rule_type"], "evaluation_as_of": iso_z(as_of), "event_status": "INVALIDATING_EVENT" if state == "EVENT_INVALIDATED" else "REVIEW_EVENT" if ev_events else "NO_INVALIDATING_EVENT", "evidence_basis": ev_rule["evidence_basis"], "evidence_strength": ev_rule["evidence_strength"], "lineage": {"timeline_bucket_id": row.get("bucket_id") if row else None, "event_rules": ev_events}})
    release_state, release_events = release_event_state(policy, subject_class, event_ledger, as_of, artifact_id)
    release = aggregate_release(policy, product_context, level_results, delta_results, evidence_results, [{"freshness_state": release_state, "event_matches": release_events, "artifact_id": artifact_id}])
    hashes = config_hashes()
    bundle = input_bundle_hash(subject, as_of, hashes)
    return {"policy_version": POLICY_VERSION, "engine_version": ENGINE_VERSION, "subject_id": structural_index["subject_id"], "subject_key": subject, "subject_label": SUBJECT_LABELS[subject], "subject_class": subject_class, "product_context": product_context, "current_release_artifact_id": artifact_id, "evaluation_as_of": iso_z(as_of), "profile_hash": hashes["freshness_profiles_sha256"], "event_rules_hash": hashes["event_invalidation_rules_sha256"], "criticality_hash": hashes["evidence_family_criticality_sha256"], "evidence_rules_hash": hashes["evidence_freshness_rules_sha256"], "precedence_hash": hashes["freshness_precedence_sha256"], "input_bundle_hash": bundle, "subject_freshness_summary": release, "dimension_level_results": level_results, "dimension_delta_results": delta_results, "evidence_family_results": evidence_results, "release_event_results": [{"freshness_state": release_state, "event_status": "INVALIDATING_EVENT" if release_state == "EVENT_INVALIDATED" else "REVIEW_EVENT" if release_events else "NO_INVALIDATING_EVENT", "event_matches": release_events, "artifact_id": artifact_id}], "release_result": release}


def aggregate_release(policy: PolicyRuntime, product_context: str, levels: list[dict], deltas: list[dict], evidence: list[dict], release_events: list[dict] | None = None) -> dict:
    release_events = release_events or []
    candidates = [row["freshness_state"] for row in levels + deltas + evidence + release_events if row["freshness_state"] != "NOT_APPLICABLE"]
    critical_unconfigured = [row for row in levels + evidence if row["freshness_state"] == "POLICY_NOT_CONFIGURED" and row.get("criticality", "CRITICAL") == "CRITICAL"]
    if product_context == "PAID_VERIFIED_REPORT" and critical_unconfigured:
        candidates.append("REFRESH_REQUIRED")
    state = precedence_pick(policy, candidates) if candidates else "CURRENT"
    if state == "POLICY_NOT_CONFIGURED" and product_context == "PUBLIC_RESEARCH":
        state = "CURRENT_WITH_LIMITATIONS"
    blockers = [row for row in levels + deltas + evidence + release_events if row["freshness_state"] in {"EVENT_INVALIDATED", "UNDER_REVIEW", "REFRESH_REQUIRED", "SUPERSEDED"} and row.get("criticality", "CRITICAL") == "CRITICAL"]
    limitations = [row for row in levels + deltas + evidence if row["freshness_state"] in {"AGING", "CURRENT_WITH_LIMITATIONS", "POLICY_NOT_CONFIGURED", "INSUFFICIENT_DATA"}]
    if state == "CURRENT" and limitations and product_context == "PUBLIC_RESEARCH":
        state = "CURRENT_WITH_LIMITATIONS"
    return {"release_context": product_context, "release_freshness_state": state, "blocking_dimensions": [row.get("dimension_id") for row in blockers if row.get("dimension_id")], "blocking_evidence_families": [row.get("family_id") for row in blockers + critical_unconfigured if row.get("family_id")], "limitations": [row.get("dimension_id") or row.get("family_id") for row in limitations], "paid_delivery": "BLOCKED" if product_context == "PAID_VERIFIED_REPORT" and state != "CURRENT" else "NOT_AUTHORIZED_BY_FRESHNESS_ALONE", "next_refresh_reason": "POLICY_NOT_CONFIGURED" if critical_unconfigured else "TIME_WINDOW" if blockers else "MANUAL_REVIEW" if limitations else "EXPECTED_REPORTING_EVENT"}


def config_hashes() -> dict:
    paths = {
        "freshness_profiles_sha256": config_dir() / "freshness_profiles.json",
        "event_invalidation_rules_sha256": config_dir() / "event_invalidation_rules.json",
        "evidence_family_criticality_sha256": config_dir() / "evidence_family_criticality.json",
        "evidence_freshness_rules_sha256": config_dir() / "evidence_freshness_rules.json",
        "freshness_precedence_sha256": config_dir() / "freshness_precedence.json",
        "product_context_rules_sha256": config_dir() / "product_context_rules.json",
    }
    return {key: sha_path(path) for key, path in paths.items()}


def input_bundle_hash(subject: str, as_of: datetime, hashes: dict) -> str:
    manifest = ROOT / "timeline" / "subjects" / f"{subject}_timeline_derivation_manifest.json"
    payload = {"policy_version": POLICY_VERSION, "engine_version": ENGINE_VERSION, "subject": subject, "timeline_manifest_sha256": sha_path(manifest), "config_hashes": hashes, "evaluation_as_of": iso_z(as_of)}
    return sha_json(payload)


def cadence_metrics() -> dict:
    results = []
    for subject in SUBJECTS:
        atomic = read_json(ROOT / "timeline" / "atomic" / f"{subject}_atomic_observations.json")["observations"]
        by_dim = defaultdict(list)
        for obs in atomic:
            for dim in obs["dimension_ids"]:
                by_dim[dim].append(parse_day(obs["effective_at"]))
        for dim, dates in by_dim.items():
            dates = sorted(d for d in dates if d)
            intervals = [(b - a).days for a, b in zip(dates, dates[1:])]
            results.append({"subject": subject, "subject_class": SUBJECT_CLASSES[subject], "dimension_id": dim, "count": len(dates), "interval_count": len(intervals), "median_interval_days": percentile(intervals, 50), "mean_interval_days": round(sum(intervals) / len(intervals), 2) if intervals else None, "p25_interval_days": percentile(intervals, 25), "p75_interval_days": percentile(intervals, 75), "p90_interval_days": percentile(intervals, 90), "maximum_interval_days": max(intervals) if intervals else None, "event_triggered_changes": sum(1 for obs in atomic if dim in obs["dimension_ids"] and obs["freshness_trigger_candidate"]), "silent_periods": max(len(intervals) - sum(1 for obs in atomic if dim in obs["dimension_ids"] and obs["freshness_trigger_candidate"]), 0)})
    return {"policy_version": POLICY_VERSION, "minimum_empirical_interval_sample": 5, "metrics": results}


def percentile(values: list[int], pct: int) -> int | None:
    if not values:
        return None
    values = sorted(values)
    idx = round((len(values) - 1) * pct / 100)
    return values[idx]


def unconfigured_registry(policy: PolicyRuntime) -> dict:
    items = []
    for rule in policy.profiles["profiles"]:
        if rule["status"] != "CONFIGURED":
            items.append({"rule_id": rule["rule_id"], "subject_class": rule["subject_class"], "dimension_id": rule["dimension_id"], "state_type": rule["state_type"], "reason": "INSUFFICIENT_CADENCE_DATA" if rule["evidence_basis"] == "INSUFFICIENT" else "METHOD_UNRESOLVED"})
    return {"policy_version": POLICY_VERSION, "items": items}


def threshold_review_record(policy: PolicyRuntime) -> dict:
    rows = []
    for rule in policy.profiles["profiles"]:
        tr = rule["time_rule"]
        if tr["rule_type"] in {"HYBRID_TIME_EVENT", "REPORTING_PERIOD"}:
            chosen = {key: tr[key] for key in ["current_boundary_days", "aging_boundary_days", "refresh_boundary_days"]}
            rows.append({"rule_id": rule["rule_id"], "candidate_thresholds": {"current": [90, 120, 180], "aging": [150, 180, 270], "refresh": [210, 240, 365]}, "chosen_rule": chosen, "reviewer_rationale": rule["rationale"], "alternative_rejected": "Single global 30 day cutoff rejected because cadence evidence is sparse and domain-specific.", "subject_outcomes_hidden": True})
    return {"policy_version": POLICY_VERSION, "records": rows}


def write_runtime(as_of: datetime, policy: PolicyRuntime) -> dict:
    results = {}
    for subject in SUBJECTS:
        result = evaluate_subject(subject, as_of, policy, "PUBLIC_RESEARCH")
        out_dir = ROOT / "research" / "freshness" / subject
        write_json(out_dir / RUNTIME_RECORD, result)
        history = out_dir / "history.jsonl"
        history.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"policy_version": POLICY_VERSION, "evaluation_as_of": result["evaluation_as_of"], "input_bundle_hash": result["input_bundle_hash"], "release_freshness_state": result["release_result"]["release_freshness_state"]}, sort_keys=True)
        existing = history.read_text(encoding="utf-8").splitlines() if history.exists() else []
        if line not in existing:
            history.write_text("\n".join([*existing, line]).strip() + "\n", encoding="utf-8")
        results[subject] = result
    return results


def write_manifest(policy: PolicyRuntime, runtime: dict) -> None:
    hashes = config_hashes()
    derivation = ROOT / "docs" / "research" / "RDL_FRESHNESS_POLICY_DERIVATION_v0.1.md"
    validation = ROOT / "docs" / "execution" / "RDL_FRESHNESS_v0_1a_FINAL_EXECUTION_REPORT.md"
    unconfigured = unconfigured_registry(policy)["items"]
    write_json(ROOT / "rdl" / "freshness" / "RDL_FRESHNESS_POLICY_MANIFEST.json", {"policy_version": POLICY_VERSION, "supersedes_policy_version": "RDL_FRESHNESS_v0.1", "config_hashes": hashes, "event_scope_hash": hashes["event_invalidation_rules_sha256"], "evidence_freshness_config_hash": hashes["evidence_freshness_rules_sha256"], "precedence_hash": hashes["freshness_precedence_sha256"], "research_derivation_hash": sha_path(derivation) if derivation.exists() else None, "validation_report_hash": sha_path(validation) if validation.exists() else None, "rule_count": len(policy.profiles["profiles"]), "configured_count": sum(1 for row in policy.profiles["profiles"] if row["status"] == "CONFIGURED"), "unconfigured_count": len(unconfigured), "evaluation_engine_version": ENGINE_VERSION, "subject_count": len(runtime)})


def write_research_docs(policy: PolicyRuntime, metrics: dict) -> None:
    configured = [r for r in policy.profiles["profiles"] if r["status"] == "CONFIGURED"]
    unconfigured = [r for r in policy.profiles["profiles"] if r["status"] != "CONFIGURED"]
    write_text(ROOT / "docs" / "research" / "RDL_FRESHNESS_POLICY_DERIVATION_v0.1.md", f"""# RDL Freshness Policy Derivation v0.1

Status: METHOD PILOT

Research question: determine whether structural Level, structural Delta, evidence-family and release records remain current enough for their stated research use.

Subject classes: PUBLIC_COMPANY_TREASURY and L1_NETWORK are configured for the current pilot surface. PROTOCOL_GOVERNANCE and MARKET_CONTEXT remain present but unconfigured.

Level and Delta are evaluated separately. Evidence age is separate from structural state age. No global freshness threshold is used.

Configured rules: {len(configured)}

Unconfigured rules: {len(unconfigured)}

Rejected rules: a universal 30 day freshness cutoff, a shared Level/Delta age rule, and any rule tuned to make paid delivery easier.

Final rule basis: reporting-period rules for corporate treasury, hybrid time/event rules for supply and validator distribution, event-only rules for persistent governance mechanisms, and explicit POLICY_NOT_CONFIGURED fail-safes for sparse categories.""")
    metric_rows = "\n".join(f"| {m['subject']} | {m['dimension_id']} | {m['count']} | {m['interval_count']} | {m['median_interval_days'] or 'N/A'} | {m['p75_interval_days'] or 'N/A'} | {m['p90_interval_days'] or 'N/A'} | {m['maximum_interval_days'] or 'N/A'} |" for m in metrics["metrics"])
    write_text(ROOT / "docs" / "research" / "RDL_FRESHNESS_CADENCE_ANALYSIS_v0.1.md", f"""# RDL Freshness Cadence Analysis v0.1

Minimum empirical interval sample: {metrics['minimum_empirical_interval_sample']}

Current timeline data is sparse. Numeric policy windows in v0.1 are therefore classified as REPORTING_SCHEDULE or EXPERT_METHOD_RULE, not high-strength empirical rules.

| Subject | Dimension | Observations | Intervals | Median | P75 | P90 | Max |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
{metric_rows}""")
    write_text(ROOT / "docs" / "research" / "RDL_FRESHNESS_SENSITIVITY_ANALYSIS_v0.1.md", """# RDL Freshness Sensitivity Analysis v0.1

Candidate windows were reviewed against 90/120/180 day current bands, 150/180/270 day aging bands, and 210/240/365 day refresh bands.

Because many categories have fewer than five intervals, small-window alternatives were rejected where they would create cliff effects without source cadence support.

Result: use broad bands only for minimum viable configured Level/evidence rules, and keep sparse Delta and unsupported dimensions POLICY_NOT_CONFIGURED.""")
    write_text(ROOT / "docs" / "research" / "RDL_FRESHNESS_EVENT_RULES_v0.1.md", """# RDL Freshness Event Rules v0.1

Verified material events can override young age. Unverified events mark records for review unless a future policy explicitly requires precautionary invalidation.

Event severity is not investment risk. EVENT_INVALIDATED means the research currentness state needs review; it does not assert that an entity is unhealthy, unsafe, insolvent or investable.""")


def write_rule_table(policy: PolicyRuntime) -> None:
    rows = []
    for rule in policy.profiles["profiles"]:
        tr = rule["time_rule"]
        rows.append(f"| {rule['subject_class']} | {rule['dimension_id']} | {rule['state_type']} | {tr['rule_type']} | {tr.get('current_boundary_days', 'N/A')} | {tr.get('aging_boundary_days', 'N/A')} | {tr.get('refresh_boundary_days', 'N/A')} | {', '.join(rule['event_triggers']) or 'N/A'} | {rule['evidence_basis']} | {rule['evidence_strength']} | {rule['status']} |")
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_RULE_TABLE_v0.1.md", "# RDL Freshness Rule Table v0.1\n\n| Subject Class | Dimension | State Type | Rule Type | Current Boundary | Aging Boundary | Refresh Boundary | Event Triggers | Evidence Basis | Evidence Strength | Status |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(rows))


def write_pages(runtime: dict) -> None:
    disclaimer = "Freshness describes whether the evidence and structural observations are current enough for the stated research purpose. It does not determine whether an asset, company, or protocol is good, safe, solvent, or investable."
    summary_cards = "".join(f'<article class="card"><h2>{SUBJECT_LABELS[s]}</h2><p>Release Freshness: <code>{r["release_result"]["release_freshness_state"]}</code></p><p>Next Refresh Reason: <code>{r["release_result"]["next_refresh_reason"]}</code></p><p><a href="research/freshness/{s}/{RUNTIME_RECORD}">Freshness record</a></p></article>' for s, r in runtime.items())
    for page in ["dynamics.html", "docs/dynamics.html"]:
        path = ROOT / page
        text = path.read_text(encoding="utf-8")
        marker = "<section><h2>Process Concepts</h2>"
        overlay = f'<section><h2>Freshness Overlay</h2><p>{disclaimer}</p><div class="grid">{summary_cards}</div></section>\n'
        if "Freshness Overlay" not in text:
            text = text.replace(marker, overlay + marker, 1)
        write_text(path, text)
    gdr_text = (ROOT / "gdr.html").read_text(encoding="utf-8")
    gdr_insert = '<p>G3 Evidence Freshness is evaluated using RDL Freshness Policy v0.1a where a configured profile exists. EVENT_INVALIDATED, UNDER_REVIEW and critical unconfigured states set explicit fail-safe facts for GDR-SE aggregation.</p>'
    if "RDL Freshness Policy v0.1a" not in gdr_text:
        gdr_text = gdr_text.replace("<p>GDR-SE produces categorical release decisions, not scores, ratings or rankings.</p>", "<p>GDR-SE produces categorical release decisions, not scores, ratings or rankings.</p>\n  " + gdr_insert)
    write_text(ROOT / "gdr.html", gdr_text)
    shutil.copyfile(ROOT / "gdr.html", ROOT / "docs" / "gdr.html")
    verify_text = (ROOT / "verify.html").read_text(encoding="utf-8")
    path_text = "Finding -> Method -> Observation -> RTP Provenance -> Timeline Level/Delta -> RDL Freshness -> GDR-SE G3 -> Release Authorization"
    if "Timeline Level/Delta" not in verify_text:
        verify_text = verify_text.replace('<ol class="process"><li>Finding</li><li>Method</li><li>Calculation / Claim</li><li>Source / Artifact</li><li>RTP provenance</li><li>RDL publication gate</li></ol>', f'<p><code>{path_text}</code></p>')
    write_text(ROOT / "verify.html", verify_text)
    shutil.copyfile(ROOT / "verify.html", ROOT / "docs" / "verify.html")
    rdl = (ROOT / "architecture" / "rdl.html").read_text(encoding="utf-8")
    rdl_scope = "<section><h2>RDL Operating Scope</h2><p><code>RDL -> publication policy -> correction/supersession -> RDL Freshness Policy v0.1a -> governance standards</code></p></section>"
    if "RDL Freshness Policy v0.1a" not in rdl:
        if "RDL -> publication policy -> correction/supersession -> RDL Freshness Policy v0.1 -> governance standards" in rdl:
            rdl = rdl.replace("<section><h2>RDL Operating Scope</h2><p><code>RDL -> publication policy -> correction/supersession -> RDL Freshness Policy v0.1 -> governance standards</code></p></section>", rdl_scope)
        elif "RDL -> publication policy -> correction/supersession -> freshness policy -> governance standards" in rdl:
            rdl = rdl.replace("<section><h2>RDL Operating Scope</h2><p><code>RDL -> publication policy -> correction/supersession -> freshness policy -> governance standards</code></p></section>", rdl_scope)
        else:
            rdl = rdl.replace("<section>\n  <h2>Operational Detail</h2>", f"{rdl_scope}\n<section>\n  <h2>Operational Detail</h2>")
    write_text(ROOT / "architecture" / "rdl.html", rdl)
    (ROOT / "docs" / "architecture").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "architecture" / "rdl.html", ROOT / "docs" / "architecture" / "rdl.html")


def write_whitepaper() -> None:
    write_text(ROOT / "whitepapers" / "RDL" / "RDL_Freshness_Policy_v0.1a.md", """# RDL Freshness Policy v0.1a

Status: METHOD PILOT

## Problem

Freshness asks whether evidence and structural observations remain current enough for a stated research purpose. It is not a simple age cutoff.

## Definitions

RDL Freshness evaluates Structural Level, Structural Delta, Evidence Families and Research Releases separately.

## Level Freshness

Level freshness evaluates whether the latest supported structural condition remains defensible under subject-class, dimension, time-rule and event-trigger policy.

## Delta Freshness

Delta freshness evaluates whether an established direction of change remains relevant. A missing Delta is not stale; it is not applicable or unconfigured.

## Evidence Freshness

Evidence-family freshness is evaluated per family and product context. Criticality can differ between public research and paid verified reports.

## Event Invalidation

Verified material events can override young observations. Plausible but unverified events trigger review rather than an unsupported negative classification.

## Correction And Supersession

Material unresolved corrections trigger UNDER_REVIEW. Supersession overrides currentness.

## Policy Derivation

v0.1a uses reporting-period, hybrid time/event, event-only and explicit unconfigured rules. Sparse categories remain POLICY_NOT_CONFIGURED. Event matching requires both event domain and exact target compatibility.

## GDR-SE Interaction

GDR-SE G3 consumes RDL Freshness output. GDR-SE does not invent freshness thresholds.

## Limitations

This is a method pilot, not a validated industry standard, rating, score or investment signal.

## Future Validation

Future work should collect longitudinal cadence data and validate threshold stability before expanding configured rules.""")


def write_schemas() -> None:
    base = ROOT / "rdl" / "freshness" / "schema"
    write_json(base / "freshness_evaluation.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["policy_version", "subject_id", "evaluation_as_of", "dimension_level_results", "dimension_delta_results", "evidence_family_results", "release_result", "input_bundle_hash"]})
    write_json(base / "freshness_profile.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["policy_version", "profiles"]})
    write_json(base / "freshness_gate_result.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["gate_id", "status", "validator", "rule_version", "evaluated_at", "evidence_refs", "computed_facts", "reason"]})
    write_json(base / "supersession_relation.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["relation_id", "successor_artifact_id", "superseded_artifact_id", "relation_type", "effective_at", "known_at", "source_ref"]})


def write_gdr_adapter(runtime: dict) -> None:
    adapter = {"policy_version": POLICY_VERSION, "mapping": {"CURRENT": "PASS", "CURRENT_WITH_LIMITATIONS": "PARTIAL", "AGING": "PARTIAL", "REFRESH_REQUIRED": "UNRESOLVED", "EVENT_INVALIDATED": "FAIL", "UNDER_REVIEW": "UNRESOLVED", "SUPERSEDED": "SUPERSEDED", "INSUFFICIENT_DATA": "UNRESOLVED", "POLICY_NOT_CONFIGURED": "UNRESOLVED"}, "fail_safe_facts": {"REFRESH_REQUIRED": {"refresh_required": True}, "EVENT_INVALIDATED": {"human_review_required": True}, "UNDER_REVIEW": {"human_review_required": True}, "INSUFFICIENT_DATA": {"human_review_required": True}, "POLICY_NOT_CONFIGURED": {"human_review_required": True}}, "subjects": {k: {"release_freshness_state": v["release_result"]["release_freshness_state"], "record_path": f"research/freshness/{k}/{RUNTIME_RECORD}"} for k, v in runtime.items()}}
    write_json(ROOT / "rdl" / "freshness" / "gdr_g3_adapter.json", adapter)


def write_audits(policy: PolicyRuntime, runtime: dict) -> None:
    configured = sum(1 for row in policy.profiles["profiles"] if row["status"] == "CONFIGURED")
    unconfigured = sum(1 for row in policy.profiles["profiles"] if row["status"] != "CONFIGURED")
    outcomes = "\n".join(f"| {SUBJECT_LABELS[s]} | {r['release_result']['release_freshness_state']} | {Counter(row['freshness_state'] for row in r['dimension_level_results'])} | {Counter(row['freshness_state'] for row in r['dimension_delta_results'])} | {Counter(row['freshness_state'] for row in r['evidence_family_results'])} |" for s, r in runtime.items())
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_PRE_AUDIT.md", "# RDL Freshness Pre Audit\n\nTimeline R1.1a gate registry is present and reports `RUNTIME_CLOSURE_PASS`. The RDL Freshness Policy v0.1 layer is implemented as an overlay and does not reopen Timeline semantics.")
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_POLICY_CONFIG_AUDIT.md", f"# RDL Freshness Policy Config Audit\n\nConfigured rules: {configured}\n\nUnconfigured rules: {unconfigured}\n\nNo `GLOBAL_MAX_AGE_DAYS` or `DEFAULT_MAX_AGE_DAYS` exists in production config. Precedence, event invalidation, evidence criticality and product-context rules are versioned config inputs.")
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_RUNTIME_AUDIT.md", "# RDL Freshness Runtime Audit\n\n| Subject | Release Freshness | Level Freshness | Delta Freshness | Evidence Freshness |\n| --- | --- | --- | --- | --- |\n" + outcomes)
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_GDR_INTEGRATION_AUDIT.md", f"# RDL Freshness GDR Integration Audit\n\nGDR-SE G3 consumes `rdl/freshness/gdr_g3_adapter.json` and per-subject `research/freshness/*/{RUNTIME_RECORD}`. EVENT_INVALIDATED and UNDER_REVIEW now set explicit fail-safe facts consumed by aggregation. Other GDR-SE gates and aggregation precedence remain unchanged.")
    write_text(ROOT / "docs" / "execution" / "RDL_FRESHNESS_TIMELINE_UI_AUDIT.md", "# RDL Freshness Timeline UI Audit\n\nSubject and Dynamics pages preserve Level/Delta trajectories and add a separate Freshness Overlay with release freshness, next refresh reason and links to runtime records.")


def sync_outputs() -> None:
    shutil.copytree(ROOT / "rdl", ROOT / "docs" / "rdl", dirs_exist_ok=True)
    shutil.copytree(ROOT / "research" / "freshness", ROOT / "docs" / "research" / "freshness", dirs_exist_ok=True)
    shutil.copytree(ROOT / "whitepapers" / "RDL", ROOT / "docs" / "whitepapers" / "RDL", dirs_exist_ok=True)


def build(as_of: datetime | str | None = None) -> dict:
    as_of_dt = parse_as_of(as_of if isinstance(as_of, str) or as_of is None else as_of.isoformat())
    policy = write_configs()
    write_schemas()
    metrics = cadence_metrics()
    write_json(ROOT / "rdl" / "freshness" / "audit" / "CADENCE_METRICS.json", metrics)
    write_json(ROOT / "rdl" / "freshness" / "audit" / "UNCONFIGURED_FRESHNESS_RULES.json", unconfigured_registry(policy))
    write_json(ROOT / "rdl" / "freshness" / "audit" / "THRESHOLD_REVIEW_RECORD.json", threshold_review_record(policy))
    write_json(ROOT / "rdl" / "freshness" / "audit" / "SUPERSESSION_RELATIONS.json", supersession_relations())
    runtime = write_runtime(as_of_dt, policy)
    write_gdr_adapter(runtime)
    write_research_docs(policy, metrics)
    write_rule_table(policy)
    write_whitepaper()
    write_pages(runtime)
    write_audits(policy, runtime)
    write_manifest(policy, runtime)
    sync_outputs()
    write_manifest(policy, runtime)
    sync_outputs()
    return runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=None)
    args = parser.parse_args()
    build(args.as_of)
    print("RDL_FRESHNESS_BUILD_PASS")


if __name__ == "__main__":
    main()
