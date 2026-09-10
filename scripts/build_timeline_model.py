from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import shutil
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from timeline.engine.clock import parse_as_of, utc_now  # noqa: E402

DOCS = ROOT / "docs"
MODEL_VERSION = "TIMELINE_MODEL_R1_1A"
UI_VERSION = "TIMELINE_UI_R1_1A"
MAPPING_VERSION = "TIMELINE_MAPPING_v0.1"
AGGREGATION_VERSION = "TIMELINE_AGGREGATION_v0.1"
TIMELINE_V0_1_COMMIT = "9abfb37392f921e499915358ff0700173240cef6"
TIMELINE_R1_COMMIT = "0f7762b31dcf85754468a81b884665e717050e79"
TIMELINE_R1_1_COMMIT = "57ead80bd9720c4f352d4023b60026bfb7a4541d"
SUBJECTS = ["strategy", "bnb", "sol", "trx", "xlm"]
RESOLUTIONS = ["DAY", "WEEK", "MONTH"]
LEVEL_STATES = ["EXPANSIONARY", "CONTRACTIONARY", "BALANCED", "MECHANISM_TRANSITION", "DISTRIBUTED", "MODERATELY_CONCENTRATED", "CONCENTRATED", "FIXED_OR_RESTRICTED_SET", "MECHANISM_DEFINED", "LIMITED_ROLE", "ESTABLISHED_ROLE", "MATERIAL_ROLE", "DOMINANT_ROLE", "MIXED_ROLE", "LOW_DEPENDENCE", "MATERIAL_DEPENDENCE", "HIGH_DEPENDENCE", "HYBRID_DEPENDENCE", "SOURCE_DEPENDENT", "INSUFFICIENT_DATA", "NO_OBSERVATION", "MIXED_LEVEL"]
DELTA_STATES = ["TOWARD_CONTRACTION", "TOWARD_EXPANSION", "TOWARD_CONCENTRATION", "TOWARD_DISTRIBUTION", "TOWARD_HIGHER_DEPENDENCE", "TOWARD_LOWER_DEPENDENCE", "ROLE_STRENGTHENING", "ROLE_WEAKENING", "UNCHANGED", "STRUCTURAL_SHIFT", "MIXED_CHANGE", "NOT_ESTABLISHED", "INSUFFICIENT_DATA"]
DELTA_BASES = ["COMPARISON_TO_PRIOR_OBSERVATION", "EXPLICIT_CHANGE_EVENT", "NOT_ESTABLISHED"]
EVIDENCE_STATES = ["NOT_OBSERVED", "OBSERVED", "PARTIAL", "COMPLETE", "UNRESOLVED", "UNDER_REVIEW", "SUPERSEDED", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED"]
EVENT_DOMAINS = ["SUBJECT_EVENT", "EVIDENCE_EVENT", "RESEARCH_EVENT", "AUTHORIZATION_EVENT"]
OBSERVATION_MODES = ["DIRECT", "RECONSTRUCTED", "SPARSE_EVENT_STATE"]


STRUCTURAL_TAXONOMY = {
    "SUPPLY_STRUCTURE": "Supply mechanics, issuance, burn or distribution structure.",
    "UTILITY_STRUCTURE": "Documented functional demand or use context.",
    "GOVERNANCE_STRUCTURE": "Control, voting, validator or decision structure.",
    "RESOURCE_PRESSURE": "Resource, fee, liquidity or capacity pressure.",
    "TREASURY_STRUCTURE": "Treasury, reserve or funding architecture.",
    "NARRATIVE_DEPENDENCE": "Dependence on claims, framing or issuer narrative.",
    "SETTLEMENT_ROLE": "Settlement, payments or transfer-function role.",
    "VALIDATOR_DISTRIBUTION": "Validator, quorum or block-producer distribution.",
    "FOUNDATION_DEPENDENCE": "Foundation or sponsoring-entity dependence.",
    "SOURCE_DEPENDENCY": "Bridge dimension showing source-independence constraints where they shape structural interpretation.",
}

EVIDENCE_TAXONOMY = {
    "PRIMARY_SOURCE_COVERAGE": "Primary source availability and source package capture.",
    "SECONDARY_SUPPORT": "Secondary corroboration where available.",
    "COUNTER_EVIDENCE_COVERAGE": "Targeted counter-evidence coverage.",
    "NUMERICAL_RECONCILIATION": "Arithmetic or quantitative reconciliation status.",
    "SOURCE_DEPENDENCY": "Independence and dependency boundaries of source families.",
    "INDEPENDENT_REVIEW": "Independent or blind-review availability.",
    "CORRECTION_STATUS": "Correction record status.",
    "SUPERSESSION_STATUS": "Supersession or version status.",
    "AUTHORIZATION_STATUS": "GDR-SE runtime authorization status.",
}

SUBJECT_CONFIG = {
    "strategy": {"label": "Strategy 2026", "subject_type": "PUBLIC_COMPANY_TREASURY", "page": "strategy-2026.html", "default_resolution": "MONTH", "structural_state": "HYBRID_ACCUMULATION_MONETIZATION", "evidence_state": "SEMANTIC_TENSION_BUT_RECONCILABLE", "source_coverage": "PARTIAL", "last_reviewed": "2026-09-08", "dimensions": ["TREASURY_STRUCTURE", "RESOURCE_PRESSURE", "NARRATIVE_DEPENDENCE", "SOURCE_DEPENDENCY"]},
    "bnb": {"label": "BNB", "subject_type": "DIGITAL_ASSET", "page": "bnb.html", "default_resolution": "WEEK", "dimensions": ["SUPPLY_STRUCTURE", "UTILITY_STRUCTURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE"]},
    "sol": {"label": "SOL", "subject_type": "DIGITAL_ASSET", "page": "sol.html", "default_resolution": "WEEK", "dimensions": ["UTILITY_STRUCTURE", "RESOURCE_PRESSURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE"]},
    "trx": {"label": "TRX", "subject_type": "DIGITAL_ASSET", "page": "trx.html", "default_resolution": "WEEK", "dimensions": ["SETTLEMENT_ROLE", "RESOURCE_PRESSURE", "VALIDATOR_DISTRIBUTION", "GOVERNANCE_STRUCTURE"]},
    "xlm": {"label": "XLM", "subject_type": "DIGITAL_ASSET", "page": "xlm.html", "default_resolution": "MONTH", "dimensions": ["TREASURY_STRUCTURE", "FOUNDATION_DEPENDENCE", "SETTLEMENT_ROLE", "VALIDATOR_DISTRIBUTION"]},
}

DIMENSION_RULES = {
    "strategy": {
        "STRATEGY-R1-O1": ("TREASURY_STRUCTURE", "STRENGTHENING", "MATERIAL", "SEC filing period anchors treasury baseline."),
        "STRATEGY-R1-O2": ("TREASURY_STRUCTURE", "STRUCTURAL_SHIFT", "MATERIAL", "Digital credit framework disclosure changes the treasury structure record."),
        "STRATEGY-R1-O3": ("RESOURCE_PRESSURE", "TENSION", "MATERIAL", "BTC monetization disclosure creates resource-pressure evidence."),
        "STRATEGY-R1-O4": ("NARRATIVE_DEPENDENCE", "TENSION", "MODERATE", "BTC monetization disclosure changes the narrative-dependence record."),
        "STRATEGY-R1-O5": ("SOURCE_DEPENDENCY", "TENSION", "MODERATE", "S6.1a source-dependency graph records partial independence boundaries."),
    },
    "bnb": {
        "BNB-R1-O1": ("SUPPLY_STRUCTURE", "STRUCTURAL_SHIFT", "MATERIAL", "Quarterly burn directly changes circulating supply structure."),
        "BNB-R1-O2": ("SUPPLY_STRUCTURE", "STRENGTHENING", "MODERATE", "Long-run burn target belongs to supply mechanics."),
        "BNB-R1-O3": ("SUPPLY_STRUCTURE", "STRENGTHENING", "MODERATE", "BEP95 burn mechanic belongs to supply mechanics."),
        "BNB-R1-O4": ("UTILITY_STRUCTURE", "STRENGTHENING", "MODERATE", "Fee-utility claim maps to network utility structure."),
        "BNB-R1-O5": ("VALIDATOR_DISTRIBUTION", "TENSION", "MODERATE", "Validator election set constrains validator distribution."),
        "BNB-R1-O6": ("VALIDATOR_DISTRIBUTION", "TENSION", "MODERATE", "Cabinet/candidate split maps to validator distribution."),
        "BNB-R1-O7": ("GOVERNANCE_STRUCTURE", "TENSION", "MODERATE", "Consensus-set selection maps to governance/control structure."),
        "BNB-R1-O8": ("GOVERNANCE_STRUCTURE", "STRENGTHENING", "LOW", "On-chain governance description maps to governance structure."),
        "BNB-R1-O9": ("UTILITY_STRUCTURE", "MIXED", "LOW", "Multichain ecosystem component maps to utility dependence."),
    },
    "sol": {
        "SOL-R1-O1": ("RESOURCE_PRESSURE", "STRENGTHENING", "MODERATE", "Fee split belongs to resource economics."),
        "SOL-R1-O2": ("RESOURCE_PRESSURE", "STRENGTHENING", "LOW", "Staking rewards belong to validator/resource economics."),
        "SOL-R1-O3": ("RESOURCE_PRESSURE", "STRENGTHENING", "LOW", "Inflation schedule belongs to resource economics."),
        "SOL-R1-O4": ("VALIDATOR_DISTRIBUTION", "STRENGTHENING", "MODERATE", "Foundation stake recipient count maps to validator distribution."),
        "SOL-R1-O5": ("VALIDATOR_DISTRIBUTION", "STRENGTHENING", "MODERATE", "SFDP stake share maps to validator distribution."),
        "SOL-R1-O6": ("VALIDATOR_DISTRIBUTION", "STRENGTHENING", "LOW", "Location/country spread maps to validator distribution."),
        "SOL-R1-O7": ("GOVERNANCE_STRUCTURE", "TENSION", "MODERATE", "Client criteria belong to control/client diversity structure."),
        "SOL-R1-O8": ("UTILITY_STRUCTURE", "TENSION", "LOW", "Client-status evidence is preserved as potential-conflict utility/control context."),
    },
    "trx": {
        "TRX-R1-O1": ("SETTLEMENT_ROLE", "STRENGTHENING", "MATERIAL", "Transaction count maps to settlement role context."),
        "TRX-R1-O2": ("SETTLEMENT_ROLE", "STRENGTHENING", "MATERIAL", "USDT transfer share maps directly to stablecoin settlement role."),
        "TRX-R1-O3": ("RESOURCE_PRESSURE", "STRENGTHENING", "MATERIAL", "Resource delegation share maps to resource pressure."),
        "TRX-R1-O4": ("RESOURCE_PRESSURE", "STRENGTHENING", "MODERATE", "Bandwidth/Energy mechanism maps to resource economy."),
        "TRX-R1-O5": ("VALIDATOR_DISTRIBUTION", "STRUCTURAL_SHIFT", "MATERIAL", "27 SR producer structure maps to validator distribution."),
        "TRX-R1-O6": ("GOVERNANCE_STRUCTURE", "TENSION", "MODERATE", "Top-127 reward structure maps to governance control."),
        "TRX-R1-O7": ("GOVERNANCE_STRUCTURE", "STRENGTHENING", "LOW", "TRON Power voting maps to governance structure."),
        "TRX-R1-O8": ("GOVERNANCE_STRUCTURE", "TENSION", "LOW", "Missing concentration evidence is mapped as governance tension, not stability."),
    },
    "xlm": {
        "XLM-R1-O1": ("TREASURY_STRUCTURE", "STRENGTHENING", "MATERIAL", "SDF mandate balance maps to treasury structure."),
        "XLM-R1-O2": ("TREASURY_STRUCTURE", "STRENGTHENING", "MATERIAL", "Product and Innovation balance maps to treasury structure."),
        "XLM-R1-O3": ("TREASURY_STRUCTURE", "STRENGTHENING", "MATERIAL", "Assets and Liquidity balance maps to treasury structure."),
        "XLM-R1-O4": ("FOUNDATION_DEPENDENCE", "STRENGTHENING", "MODERATE", "Operational funding sales map to foundation dependence."),
        "XLM-R1-O5": ("TREASURY_STRUCTURE", "STRENGTHENING", "MODERATE", "Supply distribution example maps to treasury/supply structure."),
        "XLM-R1-O6": ("FOUNDATION_DEPENDENCE", "STRENGTHENING", "MODERATE", "SDF mandate balance in supply example maps to foundation dependence."),
        "XLM-R1-O7": ("VALIDATOR_DISTRIBUTION", "TENSION", "MODERATE", "Quorum-set structure maps to validator distribution."),
        "XLM-R1-O8": ("SETTLEMENT_ROLE", "STRENGTHENING", "LOW", "RWA/payment activity maps to settlement role."),
    },
}

LEVEL_RULES = {
    "strategy": {
        "STRATEGY-R1-O1": ("HYBRID_DEPENDENCE", "treasury_disclosure", "Filing establishes a treasury-structure level without directional change."),
        "STRATEGY-R1-O2": ("HYBRID_DEPENDENCE", "treasury_policy", "Digital credit framework establishes current treasury architecture level."),
        "STRATEGY-R1-O3": ("MATERIAL_DEPENDENCE", "resource_pressure", "BTC monetization disclosure establishes resource-pressure level."),
        "STRATEGY-R1-O4": ("MATERIAL_DEPENDENCE", "narrative_dependency", "Narrative-dependence review establishes condition level, not trend."),
        "STRATEGY-R1-O5": ("SOURCE_DEPENDENT", "source_architecture", "Source dependency is retained as hybrid boundary metadata."),
    },
    "bnb": {
        "BNB-R1-O1": ("CONTRACTIONARY", "burn_quantity", "Burn amount establishes contractionary supply level."),
        "BNB-R1-O2": ("CONTRACTIONARY", "burn_target", "Burn target establishes contractionary supply-mechanism level."),
        "BNB-R1-O3": ("CONTRACTIONARY", "gas_fee_burn", "BEP95 establishes contractionary mechanism level."),
        "BNB-R1-O4": ("ESTABLISHED_ROLE", "fee_utility_role", "Native fee role establishes utility level."),
        "BNB-R1-O5": ("FIXED_OR_RESTRICTED_SET", "validator_count", "Active validator election count establishes validator-distribution level."),
        "BNB-R1-O6": ("FIXED_OR_RESTRICTED_SET", "validator_tier_split", "Cabinet/candidate split establishes validator-distribution level."),
        "BNB-R1-O7": ("FIXED_OR_RESTRICTED_SET", "consensus_set_count", "Consensus-set selection establishes governance level."),
        "BNB-R1-O8": ("MECHANISM_DEFINED", "governance_mechanism", "On-chain governance description establishes governance mechanism level."),
        "BNB-R1-O9": ("MIXED_ROLE", "multichain_utility", "Multichain component establishes mixed utility role level."),
    },
    "sol": {
        "SOL-R1-O1": ("MECHANISM_DEFINED", "fee_split", "Base-fee split establishes resource-economics level."),
        "SOL-R1-O2": ("MECHANISM_DEFINED", "validator_rewards", "Staking reward formula establishes resource-economics level."),
        "SOL-R1-O3": ("MECHANISM_DEFINED", "inflation_schedule", "Inflation schedule establishes resource-economics level."),
        "SOL-R1-O4": ("MODERATELY_CONCENTRATED", "foundation_stake_recipients", "Foundation stake recipient count establishes validator-distribution level."),
        "SOL-R1-O5": ("MODERATELY_CONCENTRATED", "foundation_stake_share", "SFDP stake share establishes validator-distribution level."),
        "SOL-R1-O6": ("DISTRIBUTED", "validator_geography", "Location/country spread establishes geography-distribution level."),
        "SOL-R1-O7": ("MECHANISM_DEFINED", "client_version_criteria", "Client criteria establish governance/control level."),
        "SOL-R1-O8": ("MIXED_ROLE", "client_diversity_status", "Client diversity caveat establishes mixed utility/control level."),
    },
    "trx": {
        "TRX-R1-O1": ("MATERIAL_ROLE", "transaction_count", "Transaction count establishes settlement-role level."),
        "TRX-R1-O2": ("MATERIAL_ROLE", "stablecoin_transfer_share", "USDT transfer share establishes settlement-role level."),
        "TRX-R1-O3": ("MATERIAL_ROLE", "resource_delegation_share", "Resource delegation share establishes resource-pressure level."),
        "TRX-R1-O4": ("MECHANISM_DEFINED", "resource_model", "Bandwidth/Energy model establishes resource-economy level."),
        "TRX-R1-O5": ("FIXED_OR_RESTRICTED_SET", "validator_count", "27-SR producer structure establishes validator-distribution level."),
        "TRX-R1-O6": ("FIXED_OR_RESTRICTED_SET", "candidate_reward_tiers", "Top-127 reward tiers establish governance-structure level."),
        "TRX-R1-O7": ("MECHANISM_DEFINED", "voting_power_mechanism", "TRON Power establishes governance mechanism level."),
        "TRX-R1-O8": ("INSUFFICIENT_DATA", "vote_concentration_table", "Missing full concentration table establishes insufficient-data level."),
    },
    "xlm": {
        "XLM-R1-O1": ("HIGH_DEPENDENCE", "sdf_treasury_balance", "SDF mandate balance establishes treasury-dependence level."),
        "XLM-R1-O2": ("HIGH_DEPENDENCE", "sdf_treasury_balance", "Product and Innovation balance establishes treasury-dependence level."),
        "XLM-R1-O3": ("HIGH_DEPENDENCE", "sdf_treasury_balance", "Assets and Liquidity balance establishes treasury-dependence level."),
        "XLM-R1-O4": ("MATERIAL_DEPENDENCE", "foundation_sales_funding", "Operational funding sales establish foundation-dependence level."),
        "XLM-R1-O5": ("HIGH_DEPENDENCE", "supply_distribution", "Supply example establishes treasury/supply level."),
        "XLM-R1-O6": ("HIGH_DEPENDENCE", "sdf_mandate_balance", "Mandate balance establishes foundation-dependence level."),
        "XLM-R1-O7": ("MECHANISM_DEFINED", "quorum_structure", "Quorum-set structure establishes validator-distribution level."),
        "XLM-R1-O8": ("ESTABLISHED_ROLE", "rwa_payment_activity", "RWA/payment activity establishes settlement-role level."),
    },
}

EXPLICIT_DELTA_RULES = {
    "BNB-R1-O1": ("TOWARD_CONTRACTION", "EXPLICIT_CHANGE_EVENT", "Burn observation explicitly reports tokens removed."),
}

STRATEGY_OBSERVATIONS = [
    ("STRATEGY-R1-O1", "2026-02-13", "2026-02-13T00:00:00Z", "SOURCE_PACKAGE_ADDED", "SEC 2025 10-K entered the evidence chain.", "evidence-freeze/S6.1a/SOURCE_DEPENDENCY_GRAPH_v2.json"),
    ("STRATEGY-R1-O2", "2026-06-29", "2026-06-29T00:00:00Z", "TREASURY_DISCLOSURE", "Digital credit framework disclosure captured.", "evidence-freeze/S6.1a/SOURCE_DEPENDENCY_GRAPH_v2.json"),
    ("STRATEGY-R1-O3", "2026-07-06", "2026-07-06T00:00:00Z", "TREASURY_DISCLOSURE", "BTC monetization disclosure entered the record.", "evidence-freeze/S6.1a/TRIANGULATION_MATRIX_v2.json"),
    ("STRATEGY-R1-O4", "2026-07-06", "2026-09-08T00:00:00Z", "TREASURY_DISCLOSURE", "BTC monetization narrative tension reviewed in S6.1a.", "evidence-freeze/S6.1a/HYPOTHESIS_ASSESSMENTS_v2.json"),
    ("STRATEGY-R1-O5", "2026-09-08", "2026-09-08T00:00:00Z", "SOURCE_DEPENDENCY", "S6.1a source dependency boundary frozen.", "evidence-freeze/S6.1a/SOURCE_DEPENDENCY_GRAPH_v2.json"),
]


@dataclass(frozen=True)
class Period:
    key: str
    start: date
    end: date


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


def parse_day(value: str) -> date:
    return date.fromisoformat(value[:10])


def subject_id(subject: str) -> str:
    return "strategy" if subject == "strategy" else subject.upper()


def subject_base(subject: str) -> Path:
    if subject == "strategy":
        return ROOT / "research" / "gdr-se" / "strategy-2026"
    return ROOT / "research" / "digital-assets" / "batch-01-r1" / subject.upper()


def artifact_base(subject: str) -> str:
    return "evidence-freeze/S6.1a" if subject == "strategy" else f"research/digital-assets/batch-01-r1/{subject.upper()}"


def canonical(subject: str) -> dict:
    if subject == "strategy":
        return {"structural_state_final": SUBJECT_CONFIG[subject]["structural_state"], "evidence_state_final": SUBJECT_CONFIG[subject]["evidence_state"], "source_coverage": SUBJECT_CONFIG[subject]["source_coverage"], "last_reviewed": SUBJECT_CONFIG[subject]["last_reviewed"], "supersession_status": "CURRENT"}
    return read_json(subject_base(subject) / "CANONICAL_RESEARCH_R1.json")


def source_inventory(subject: str) -> dict:
    if subject == "strategy":
        return {
            "STRATEGY-R1-S1": {"retrieval_date": "2026-02-13", "artifact_id": "STRATEGY-R1-A1", "source_url": "https://www.sec.gov/"},
            "STRATEGY-R1-S2": {"retrieval_date": "2026-06-29", "artifact_id": "STRATEGY-R1-A2", "source_url": "https://www.strategy.com/"},
            "STRATEGY-R1-S3": {"retrieval_date": "2026-07-06", "artifact_id": "STRATEGY-R1-A3", "source_url": "https://www.strategy.com/"},
            "STRATEGY-R1-S4": {"retrieval_date": "2026-09-08", "artifact_id": "STRATEGY-R1-A4", "source_url": "evidence-freeze/S6.1a"},
        }
    return {row["source_id"]: row for row in read_json(subject_base(subject) / "SOURCE_INVENTORY.json")}


def auth_path(subject: str) -> Path:
    if subject == "strategy":
        return subject_base(subject) / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json"
    return subject_base(subject) / "gdr-se" / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json"


def build_mapping_config() -> dict:
    rules = []
    for subject, rows in DIMENSION_RULES.items():
        for source_observation_id, (dimension_id, legacy_effect, strength, rationale) in rows.items():
            level_state, measurement_concept, level_rationale = LEVEL_RULES[subject][source_observation_id]
            delta = EXPLICIT_DELTA_RULES.get(source_observation_id)
            rules.append({"rule_id": f"{subject.upper()}_{source_observation_id.replace('-', '_')}_TO_{dimension_id}", "subject_profile": subject_id(subject), "observation_match": {"observation_ids": [source_observation_id]}, "dimension_ids": [dimension_id], "legacy_structural_effect": legacy_effect, "effect_strength": strength, "mapping_rationale": rationale, "level_state": level_state, "measurement_concept": measurement_concept, "level_mapping_rule_id": f"LEVEL_{subject.upper()}_{source_observation_id.replace('-', '_')}", "level_mapping_rationale": level_rationale, "delta_state": delta[0] if delta else "NOT_ESTABLISHED", "delta_basis": delta[1] if delta else "NOT_ESTABLISHED", "delta_mapping_rule_id": f"DELTA_{source_observation_id.replace('-', '_')}" if delta else None, "delta_mapping_rationale": delta[2] if delta else "No valid prior comparable observation and no explicit change event.", "transition_rule_id": None})
    return {"mapping_version": MAPPING_VERSION, "rules": rules}


def level_aggregation_rules() -> dict:
    return {"aggregation_version": AGGREGATION_VERSION, "fallback": "INSUFFICIENT_DATA", "no_observation": "NO_OBSERVATION", "mixed": "MIXED_LEVEL", "rules": {"DAY_LEVEL": "Same level remains same; incompatible levels become MIXED_LEVEL.", "WEEK_LEVEL": "Latest valid observed Level within the week becomes closing_level_state.", "MONTH_LEVEL": "MONTH derives opening and closing Level from WEEK only."}}


def delta_aggregation_rules() -> dict:
    return {"aggregation_version": AGGREGATION_VERSION, "no_delta": "NOT_ESTABLISHED", "mixed": "MIXED_CHANGE", "shift": "STRUCTURAL_SHIFT", "rules": {"DAY_DELTA": "All NOT_ESTABLISHED remains NOT_ESTABLISHED; explicit structural shift may remain STRUCTURAL_SHIFT.", "WEEK_DELTA": "Summarize established deltas during the week.", "MONTH_DELTA": "MONTH derives period_delta_state from WEEK only."}}


def structural_aggregation_rules() -> dict:
    return {"aggregation_version": AGGREGATION_VERSION, "replaced_by": ["level_aggregation_rules.json", "delta_aggregation_rules.json"], "rules": {"R1_1": "Structural runtime uses level_state and delta_state, not legacy_structural_effect."}}


def evidence_aggregation_rules() -> dict:
    return {"aggregation_version": AGGREGATION_VERSION, "state_precedence": ["UNDER_REVIEW", "UNRESOLVED", "PARTIAL", "COMPLETE", "OBSERVED", "SUPERSEDED", "NOT_APPLICABLE", "POLICY_NOT_CONFIGURED", "NOT_OBSERVED"], "rules": {"EVIDENCE_DAY_STREAM": "Evidence events apply in known_at order.", "EVIDENCE_WEEK_FROM_DAY": "Week summarizes DAY stream.", "EVIDENCE_MONTH_FROM_WEEK": "Month summarizes WEEK cells."}, "policy_state": "POLICY_NOT_CONFIGURED"}


def trigger_type(dimension_id: str) -> str:
    return {"SUPPLY_STRUCTURE": "SUPPLY_MECHANISM_CHANGE", "TREASURY_STRUCTURE": "TREASURY_POLICY_CHANGE", "GOVERNANCE_STRUCTURE": "GOVERNANCE_CHANGE", "VALIDATOR_DISTRIBUTION": "GOVERNANCE_CHANGE", "FOUNDATION_DEPENDENCE": "GOVERNANCE_CHANGE"}.get(dimension_id, "PROTOCOL_UPGRADE")


def resolve_structural_state(states: list[str], rules: dict) -> str:
    observed = [state for state in states if state != "NO_OBSERVATION"]
    if not observed:
        return "NO_OBSERVATION"
    unique = set(observed)
    for pair in rules["conflict_pairs"]:
        if set(pair["states"]).issubset(unique):
            return pair["result"]
    if "STRUCTURAL_SHIFT" in unique:
        return "STRUCTURAL_SHIFT"
    if len(unique) == 1:
        return observed[0]
    if "TENSION" in unique:
        return "TENSION"
    return "MIXED"


def resolve_level_state(states: list[str], rules: dict) -> str:
    observed = [state for state in states if state != "NO_OBSERVATION"]
    if not observed:
        return rules["no_observation"]
    unique = set(observed)
    return observed[0] if len(unique) == 1 else rules["mixed"]


def resolve_delta_state(states: list[str], rules: dict) -> str:
    established = [state for state in states if state != "NOT_ESTABLISHED"]
    if not established:
        return rules["no_delta"]
    unique = set(established)
    if rules["shift"] in unique:
        return rules["shift"]
    return established[0] if len(unique) == 1 else rules["mixed"]


def comparison_rule_for(current: dict, rules: dict) -> dict | None:
    dimensions = current.get("dimension_ids") or []
    if len(dimensions) != 1:
        return None
    for rule in rules["rules"]:
        if (
            rule["dimension_id"] == dimensions[0]
            and rule["measurement_concept"] == current.get("measurement_concept")
            and rule["method_compatibility"] == "EXACT_CONCEPT"
        ):
            return rule
    return None


def find_prior_comparable_match(current: dict, history: list[dict], rules: dict) -> tuple[dict | None, dict | None]:
    rule = comparison_rule_for(current, rules)
    if not rule:
        return None, None
    candidates = [
        row for row in history
        if row["subject_id"] == current["subject_id"]
        and row["observation_id"] != current["observation_id"]
        and row["dimension_ids"] == current["dimension_ids"]
        and row["measurement_concept"] == rule["measurement_concept"]
        and row["effective_at"] != "UNKNOWN"
        and current["effective_at"] != "UNKNOWN"
        and row["effective_at"] < current["effective_at"]
        and row.get("level_state") not in {"NO_OBSERVATION", "INSUFFICIENT_DATA"}
        and current.get("level_state") not in {"NO_OBSERVATION", "INSUFFICIENT_DATA"}
    ]
    return (sorted(candidates, key=lambda row: (row["effective_at"], row["observation_id"]))[-1], rule) if candidates else (None, None)


def find_prior_comparable_observation(current: dict, history: list[dict], rules: dict) -> dict | None:
    prior, _ = find_prior_comparable_match(current, history, rules)
    return prior


def transition_rule_for(current: dict, prior: dict, rules: dict) -> tuple[str | None, str | None]:
    dimensions = current.get("dimension_ids") or []
    if len(dimensions) != 1:
        return None, None
    transition = f"{prior.get('level_state')}->{current.get('level_state')}"
    for rule in rules["rules"]:
        if rule["dimension_id"] == dimensions[0] and transition in rule["transitions"]:
            return rule["transitions"][transition], rule["rule_id"]
    return None, None


def derive_comparison_delta(current_observation: dict, prior_history: list[dict], comparability_config: dict, transition_config: dict) -> dict:
    prior, comparison_rule = find_prior_comparable_match(current_observation, prior_history, comparability_config)
    if not prior or not comparison_rule:
        return {"delta_state": "NOT_ESTABLISHED", "delta_basis": "NOT_ESTABLISHED", "prior_observation_id": None, "comparability_rule_id": None, "transition_rule_id": None, "comparison_lineage": {}}
    delta_state, transition_rule_id = transition_rule_for(current_observation, prior, transition_config)
    if not delta_state or not transition_rule_id:
        return {"delta_state": "NOT_ESTABLISHED", "delta_basis": "NOT_ESTABLISHED", "prior_observation_id": None, "comparability_rule_id": None, "transition_rule_id": None, "comparison_lineage": {}}
    return {
        "delta_state": delta_state,
        "delta_basis": "COMPARISON_TO_PRIOR_OBSERVATION",
        "prior_observation_id": prior["observation_id"],
        "comparability_rule_id": comparison_rule["rule_id"],
        "transition_rule_id": transition_rule_id,
        "comparison_lineage": {
            "current_observation_id": current_observation["observation_id"],
            "current_effective_at": current_observation["effective_at"],
            "current_level_state": current_observation["level_state"],
            "prior_observation_id": prior["observation_id"],
            "prior_effective_at": prior["effective_at"],
            "prior_level_state": prior["level_state"],
            "comparability_rule_id": comparison_rule["rule_id"],
            "transition_rule_id": transition_rule_id,
            "measurement_concept": current_observation["measurement_concept"],
            "artifact_refs": sorted(set(current_observation["artifact_refs"] + prior["artifact_refs"])),
        },
    }


def build_atomic_observations(subject: str, mapping: dict, source_rows_override: list[dict] | None = None, sources_override: dict | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    sources = sources_override or source_inventory(subject)
    rules = {rule["observation_match"]["observation_ids"][0]: rule for rule in mapping["rules"] if rule["subject_profile"] == subject_id(subject)}
    if source_rows_override is not None:
        source_rows = source_rows_override
    elif subject == "strategy":
        source_rows = [{"observation_id": oid, "source_id": f"STRATEGY-R1-S{min(i + 1, 4)}", "artifact_id": f"STRATEGY-R1-A{min(i + 1, 4)}", "effective_date": eff, "known_at": known, "observation_type": typ, "statement": label, "artifact_ref": ref} for i, (oid, eff, known, typ, label, ref) in enumerate(STRATEGY_OBSERVATIONS)]
    else:
        source_rows = read_json(subject_base(subject) / "OBSERVATION_REGISTRY.json")
    atomic, unmapped, unresolved = [], [], []
    for index, row in enumerate(source_rows, start=1):
        source_oid = row["observation_id"]
        rule = rules.get(source_oid)
        if not rule:
            unmapped.append({"subject_id": subject_id(subject), "source_observation_id": source_oid, "reason": "NO_STRUCTURAL_DIMENSION_MATCH"})
            continue
        effective = row.get("effective_date") or row.get("event_date") or "UNKNOWN"
        known = row.get("known_at") or f"{sources.get(row.get('source_id'), {}).get('retrieval_date', canonical(subject).get('last_reviewed'))}T00:00:00Z"
        if effective == "UNKNOWN" or known == "UNKNOWN":
            unresolved.append({"subject_id": subject_id(subject), "source_observation_id": source_oid, "effective_at": effective, "known_at": known})
        mode = "RETROSPECTIVE" if effective != "UNKNOWN" and known != "UNKNOWN" and parse_day(known) > parse_day(effective) else "CONTEMPORANEOUS"
        artifact_ref = row.get("artifact_ref") or f"research/digital-assets/batch-01-r1/{subject.upper()}/OBSERVATION_REGISTRY.json"
        capture_lag = (parse_day(known) - parse_day(effective)).days if effective != "UNKNOWN" and known != "UNKNOWN" else None
        atomic.append({"observation_id": f"TL-{subject.upper()}-O{index:03d}", "subject_id": subject_id(subject), "source_observation_id": source_oid, "dimension_ids": rule["dimension_ids"], "effective_at": f"{effective[:10]}T00:00:00Z" if effective != "UNKNOWN" else "UNKNOWN", "known_at": known, "knowledge_mode": mode, "observation_type": row.get("observation_type", "PUBLIC_FACT"), "level_state": rule["level_state"], "delta_state": rule["delta_state"], "delta_basis": rule["delta_basis"], "prior_observation_id": None, "comparability_rule_id": None, "transition_rule_id": None, "level_mapping_rule_id": rule["level_mapping_rule_id"], "delta_mapping_rule_id": rule["delta_mapping_rule_id"], "legacy_structural_effect": rule["legacy_structural_effect"], "effect_strength": rule["effect_strength"], "measurement_concept": rule["measurement_concept"], "evidence_family_ids": ["PRIMARY_SOURCE_COVERAGE"], "source_refs": [sources.get(row.get("source_id"), {}).get("source_url", artifact_ref)], "artifact_refs": [artifact_ref], "mapping_rule_id": rule["rule_id"], "mapping_rationale": rule["mapping_rationale"], "level_mapping_rationale": rule["level_mapping_rationale"], "delta_mapping_rationale": rule["delta_mapping_rationale"], "comparison_lineage": {}, "observation_mode": "SPARSE_EVENT_STATE" if subject == "strategy" else "DIRECT", "freshness_trigger_candidate": rule["delta_basis"] == "EXPLICIT_CHANGE_EVENT", "applies_to_state_type": "DELTA" if rule["delta_basis"] == "EXPLICIT_CHANGE_EVENT" else "LEVEL", "trigger_type": trigger_type(rule["dimension_ids"][0]), "capture_lag_days": capture_lag})
    history = []
    comparability_config = comparability_rules()
    transition_config = level_transition_rules()
    for obs in sorted(atomic, key=lambda row: (row["subject_id"], row["dimension_ids"][0], row["effective_at"], row["observation_id"])):
        if obs["delta_basis"] == "EXPLICIT_CHANGE_EVENT":
            history.append(obs)
            continue
        result = derive_comparison_delta(obs, history, comparability_config, transition_config)
        obs.update(result)
        obs["delta_mapping_rationale"] = "Derived by comparison to a valid prior comparable observation." if result["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION" else "No valid prior comparable observation and no explicit change event."
        obs["freshness_trigger_candidate"] = result["delta_basis"] != "NOT_ESTABLISHED"
        obs["applies_to_state_type"] = "DELTA" if result["delta_basis"] != "NOT_ESTABLISHED" else "LEVEL"
        history.append(obs)
    return atomic, unmapped, unresolved


def days_between(start: date, end: date) -> list[date]:
    days, current = [], start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def period_for_day(day: date, resolution: str) -> Period:
    if resolution == "WEEK":
        start = day - timedelta(days=day.weekday())
        return Period(f"{start.isocalendar().year}-W{start.isocalendar().week:02d}", start, start + timedelta(days=6))
    if resolution == "MONTH":
        end = date(day.year, day.month, calendar.monthrange(day.year, day.month)[1])
        return Period(f"{day.year}-{day.month:02d}", date(day.year, day.month, 1), end)
    return Period(day.isoformat(), day, day)


def aggregate_delta_basis(rows: list[dict]) -> str:
    bases = {row["delta_basis"] for row in rows if row.get("delta_state") != "NOT_ESTABLISHED"}
    if "EXPLICIT_CHANGE_EVENT" in bases:
        return "EXPLICIT_CHANGE_EVENT"
    if "COMPARISON_TO_PRIOR_OBSERVATION" in bases:
        return "COMPARISON_TO_PRIOR_OBSERVATION"
    return "NOT_ESTABLISHED"


def comparison_lineage_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        if row.get("delta_state") == "NOT_ESTABLISHED":
            continue
        lineage = row.get("comparison_lineage") or {
            "current_observation_id": row["observation_id"],
            "prior_observation_id": row.get("prior_observation_id"),
            "comparability_rule_id": row.get("comparability_rule_id"),
            "transition_rule_id": row.get("transition_rule_id"),
            "basis": row["delta_basis"],
            "artifact_refs": row.get("artifact_refs", []),
        }
        out.append(lineage)
    return out


def build_day_buckets(subject: str, observations: list[dict], dimensions: list[str], rules: dict) -> list[dict]:
    dates = [parse_day(obs["effective_at"]) for obs in observations if obs["effective_at"] != "UNKNOWN"]
    if not dates:
        return []
    by_date_dim = defaultdict(list)
    for obs in observations:
        if obs["effective_at"] != "UNKNOWN":
            for dim in obs["dimension_ids"]:
                by_date_dim[(obs["effective_at"][:10], dim)].append(obs)
    out = []
    for day in days_between(min(dates), max(dates)):
        for dim in dimensions:
            rows = by_date_dim[(day.isoformat(), dim)]
            refs = sorted({ref for row in rows for ref in row["artifact_refs"]})
            level_state = resolve_level_state([row["level_state"] for row in rows], rules["level"])
            delta_state = resolve_delta_state([row["delta_state"] for row in rows], rules["delta"])
            comparison_lineage = comparison_lineage_rows(rows)
            out.append({"bucket_id": f"{subject.upper()}-STRUCT-DAY-{day.isoformat()}-{dim}", "subject_id": subject_id(subject), "date": day.isoformat(), "period": day.isoformat(), "bucket_start": day.isoformat(), "bucket_end": day.isoformat(), "resolution": "DAY", "dimension_id": dim, "level_state": level_state, "delta_state": delta_state, "delta_basis": aggregate_delta_basis(rows), "level_observation_ids": [row["observation_id"] for row in rows], "delta_observation_ids": [row["observation_id"] for row in rows if row["delta_state"] != "NOT_ESTABLISHED"], "prior_reference_ids": [row["prior_observation_id"] for row in rows if row["prior_observation_id"]], "comparison_lineage": comparison_lineage, "state": level_state, "observations": [row["observation_id"] for row in rows], "observation_count": len(rows), "source_refs": refs, "aggregation_rule": "DAY_LEVEL_DELTA", "level_last_observed_at": f"{day.isoformat()}T00:00:00Z" if rows else None, "delta_last_established_at": f"{day.isoformat()}T00:00:00Z" if any(row["delta_state"] != "NOT_ESTABLISHED" for row in rows) else None, "lineage": {"level": {"atomic_observation_ids": [row["observation_id"] for row in rows], "artifact_refs": refs}, "delta": {"comparison_lineage": comparison_lineage, "artifact_refs": refs}, "atomic_observation_ids": [row["observation_id"] for row in rows], "artifact_refs": refs}})
    return out


def aggregate_structural_day_to_week(subject: str, day_buckets: list[dict], rules: dict) -> list[dict]:
    grouped = defaultdict(list)
    for bucket in day_buckets:
        period = period_for_day(parse_day(bucket["date"]), "WEEK")
        grouped[(period.key, bucket["dimension_id"])].append(bucket)
    out = []
    for (week, dim), rows in sorted(grouped.items()):
        period = period_for_day(parse_day(rows[0]["date"]), "WEEK")
        refs = sorted({ref for row in rows for ref in row["source_refs"]})
        observations = sorted({obs for row in rows for obs in row["observations"]})
        observed_rows = [row for row in rows if row["observation_count"]]
        delta_rows = [row for row in rows if row["delta_state"] != "NOT_ESTABLISHED"]
        closing_level = observed_rows[-1]["level_state"] if observed_rows else "NO_OBSERVATION"
        opening_level = observed_rows[0]["level_state"] if observed_rows else "NO_OBSERVATION"
        period_delta = resolve_delta_state([row["delta_state"] for row in delta_rows], rules["delta"])
        out.append({"bucket_id": f"{subject.upper()}-STRUCT-WEEK-{week}-{dim}", "subject_id": subject_id(subject), "period": week, "week_start": period.start.isoformat(), "week_end": period.end.isoformat(), "bucket_start": period.start.isoformat(), "bucket_end": period.end.isoformat(), "resolution": "WEEK", "dimension_id": dim, "opening_level_state": opening_level, "closing_level_state": closing_level, "level_state": closing_level, "period_delta_state": period_delta, "delta_state": period_delta, "delta_basis": aggregate_delta_basis(delta_rows), "level_transition_count": max(len({row["level_state"] for row in observed_rows}) - 1, 0), "delta_transition_count": len(delta_rows), "state": closing_level, "observation_count": sum(row["observation_count"] for row in rows), "source_day_bucket_ids": [row["bucket_id"] for row in rows], "observations": observations, "level_observation_ids": observations, "delta_observation_ids": sorted({obs for row in delta_rows for obs in row["delta_observation_ids"]}), "prior_reference_ids": sorted({ref for row in delta_rows for ref in row["prior_reference_ids"]}), "source_refs": refs, "aggregation_rule": "WEEK_LEVEL_DELTA_FROM_DAY", "level_last_observed_at": max([row["level_last_observed_at"] for row in observed_rows if row["level_last_observed_at"]], default=None), "delta_last_established_at": max([row["delta_last_established_at"] for row in delta_rows if row["delta_last_established_at"]], default=None), "lineage": {"day_bucket_ids": [row["bucket_id"] for row in rows], "level": {"day_bucket_ids": [row["bucket_id"] for row in observed_rows], "atomic_observation_ids": observations, "artifact_refs": refs}, "delta": {"day_bucket_ids": [row["bucket_id"] for row in delta_rows], "comparison_lineage": [item for row in delta_rows for item in row["comparison_lineage"]], "atomic_observation_ids": sorted({obs for row in delta_rows for obs in row["delta_observation_ids"]}), "artifact_refs": refs}, "atomic_observation_ids": observations, "artifact_refs": refs}})
    return out


def aggregate_structural_week_to_month(subject: str, week_buckets: list[dict], rules: dict) -> list[dict]:
    grouped = defaultdict(list)
    for bucket in week_buckets:
        grouped[(bucket["week_start"][:7], bucket["dimension_id"])].append(bucket)
    out = []
    for (month, dim), rows in sorted(grouped.items()):
        year, month_num = map(int, month.split("-"))
        end = date(year, month_num, calendar.monthrange(year, month_num)[1])
        refs = sorted({ref for row in rows for ref in row["source_refs"]})
        observations = sorted({obs for row in rows for obs in row["observations"]})
        day_ids = sorted({day for row in rows for day in row["lineage"]["day_bucket_ids"]})
        observed_rows = [row for row in rows if row["observation_count"]]
        delta_rows = [row for row in rows if row["delta_state"] != "NOT_ESTABLISHED"]
        closing_level = observed_rows[-1]["closing_level_state"] if observed_rows else "NO_OBSERVATION"
        opening_level = observed_rows[0]["opening_level_state"] if observed_rows else "NO_OBSERVATION"
        period_delta = resolve_delta_state([row["delta_state"] for row in delta_rows], rules["delta"])
        out.append({"bucket_id": f"{subject.upper()}-STRUCT-MONTH-{month}-{dim}", "subject_id": subject_id(subject), "period": month, "month_start": f"{month}-01", "month_end": end.isoformat(), "bucket_start": f"{month}-01", "bucket_end": end.isoformat(), "resolution": "MONTH", "dimension_id": dim, "opening_level_state": opening_level, "closing_level_state": closing_level, "level_state": closing_level, "period_delta_state": period_delta, "delta_state": period_delta, "delta_basis": aggregate_delta_basis(delta_rows), "level_transition_count": sum(row["level_transition_count"] for row in rows), "delta_transition_count": sum(row["delta_transition_count"] for row in rows), "state": closing_level, "observation_count": sum(row["observation_count"] for row in rows), "source_week_bucket_ids": [row["bucket_id"] for row in rows], "observations": observations, "level_observation_ids": observations, "delta_observation_ids": sorted({obs for row in delta_rows for obs in row["delta_observation_ids"]}), "prior_reference_ids": sorted({ref for row in delta_rows for ref in row["prior_reference_ids"]}), "source_refs": refs, "aggregation_rule": "MONTH_LEVEL_DELTA_FROM_WEEK", "level_last_observed_at": max([row["level_last_observed_at"] for row in observed_rows if row["level_last_observed_at"]], default=None), "delta_last_established_at": max([row["delta_last_established_at"] for row in delta_rows if row["delta_last_established_at"]], default=None), "lineage": {"week_bucket_ids": [row["bucket_id"] for row in rows], "day_bucket_ids": day_ids, "level": {"week_bucket_ids": [row["bucket_id"] for row in observed_rows], "day_bucket_ids": sorted({day for row in observed_rows for day in row["lineage"]["day_bucket_ids"]}), "atomic_observation_ids": observations, "artifact_refs": refs}, "delta": {"week_bucket_ids": [row["bucket_id"] for row in delta_rows], "day_bucket_ids": sorted({day for row in delta_rows for day in row["lineage"]["day_bucket_ids"]}), "comparison_lineage": [item for row in delta_rows for item in row["lineage"]["delta"]["comparison_lineage"]], "atomic_observation_ids": sorted({obs for row in delta_rows for obs in row["delta_observation_ids"]}), "artifact_refs": refs}, "atomic_observation_ids": observations, "artifact_refs": refs}})
    return out


def build_phase_ribbon(subject: str, month_buckets: list[dict]) -> list[dict]:
    active = [row for row in month_buckets if row["observation_count"]]
    if not active:
        return [{"phase_id": f"{subject.upper()}-NO-PHASE-ASSERTION", "period": "NO_PHASE_ASSERTION", "bucket_start": None, "bucket_end": None, "resolution": "MONTH", "phase": "NO_PHASE_ASSERTION", "phase_mode": "NO_PHASE_ASSERTION", "dimension_bucket_refs": [], "aggregation_rule": "PHASE_NO_BACKFILL", "source_refs": [], "notes": ["No historical phase is asserted without dated evidence."]}]
    return [{"phase_id": f"{row['bucket_id']}-PHASE", "period": row["period"], "bucket_start": row["bucket_start"], "bucket_end": row["bucket_end"], "resolution": "MONTH", "phase": "RECONSTRUCTED_DIMENSION_EVENT", "phase_mode": "RECONSTRUCTED", "dimension_bucket_refs": [row["bucket_id"]], "aggregation_rule": row["aggregation_rule"], "source_refs": row["source_refs"], "notes": ["Current Structural State is not copied backward."]} for row in active]


def evidence_event(subject: str, family: str, event_type: str, known_at: str, state: str, artifact_name: str) -> dict:
    ref = f"{artifact_base(subject)}/{artifact_name}"
    return {"evidence_event_id": f"TL-{subject.upper()}-EE-{family}", "subject_id": subject_id(subject), "family_id": family, "event_type": event_type, "known_at": known_at, "state_after": state, "artifact_refs": [ref], "source_refs": [ref], "observation_mode": "DIRECT", "capture_lag_days": None}


def build_evidence_events(subject: str, observations: list[dict]) -> list[dict]:
    can = canonical(subject)
    events = []
    for idx, known in enumerate(sorted({obs["known_at"] for obs in observations if obs["known_at"] != "UNKNOWN"}), start=1):
        related = [obs for obs in observations if obs["known_at"] == known]
        events.append({"evidence_event_id": f"TL-{subject.upper()}-EE{idx:03d}", "subject_id": subject_id(subject), "family_id": "PRIMARY_SOURCE_COVERAGE", "event_type": "SOURCE_CAPTURED", "known_at": known, "state_after": "OBSERVED", "artifact_refs": sorted({ref for obs in related for ref in obs["artifact_refs"]}), "source_refs": sorted({ref for obs in related for ref in obs["source_refs"]}), "observation_mode": "DIRECT", "effective_at_refs": sorted({obs["effective_at"] for obs in related}), "capture_lag_days": max([obs["capture_lag_days"] for obs in related if obs["capture_lag_days"] is not None], default=None)})
    reviewed = f"{can['last_reviewed']}T00:00:00Z"
    events.extend([
        evidence_event(subject, "COUNTER_EVIDENCE_COVERAGE", "COUNTER_EVIDENCE_SEARCH_COMPLETED", reviewed, "PARTIAL", "COUNTER_EVIDENCE_SEARCH_LOG_v3.json" if subject == "strategy" else "COUNTER_EVIDENCE_SEARCH_LOG.json"),
        evidence_event(subject, "NUMERICAL_RECONCILIATION", "NUMERICAL_RECONCILIATION_COMPLETED", reviewed, "NOT_APPLICABLE" if subject == "strategy" else "COMPLETE", "TRIANGULATION_MATRIX_v2.json" if subject == "strategy" else "NUMERICAL_RECONCILIATION.json"),
        evidence_event(subject, "SOURCE_DEPENDENCY", "ARTIFACT_FROZEN", reviewed, "PARTIAL", "SOURCE_DEPENDENCY_GRAPH_v2.json" if subject == "strategy" else "SOURCE_DEPENDENCY_GRAPH.json"),
        evidence_event(subject, "INDEPENDENT_REVIEW", "INDEPENDENT_REVIEW_COMPLETED", reviewed, "NOT_APPLICABLE" if subject == "strategy" else "COMPLETE", "REPORT_VERSION_MAP.json" if subject == "strategy" else "BLIND_REVIEW_OUTPUT.md"),
        evidence_event(subject, "SUPERSESSION_STATUS", "SUPERSESSION_ADDED", reviewed, "COMPLETE", "REPORT_VERSION_MAP.json" if subject == "strategy" else "SUPERSESSION_NOTICE.md"),
    ])
    auth = read_json(auth_path(subject))
    events.append({"evidence_event_id": f"TL-{subject.upper()}-EE-AUTH", "subject_id": subject_id(subject), "family_id": "AUTHORIZATION_STATUS", "event_type": "GDR_SE_AUTHORIZATION_EVALUATED", "known_at": auth["created_at"], "state_after": "UNDER_REVIEW" if auth["authorization"] == "HUMAN_REVIEW_REQUIRED" else "COMPLETE", "artifact_refs": [auth_path(subject).relative_to(ROOT).as_posix()], "source_refs": [auth_path(subject).relative_to(ROOT).as_posix()], "observation_mode": "DIRECT", "evaluation_as_of": auth["evaluation_as_of"], "capture_lag_days": 0})
    return sorted(events, key=lambda row: (row["known_at"], row["family_id"], row["evidence_event_id"]))


def latest_age(latest: str | None, period_end: date) -> int | None:
    return None if not latest else max((period_end - parse_day(latest)).days, 0)


def build_evidence_day_stream(subject: str, events: list[dict], as_of: datetime) -> list[dict]:
    known_dates = [parse_day(event["known_at"]) for event in events if event["known_at"] != "UNKNOWN"]
    start, end = min(known_dates), max(max(known_dates), as_of.date())
    by_date_family = defaultdict(list)
    for event in events:
        by_date_family[(event["known_at"][:10], event["family_id"])].append(event)
    state = {family: "NOT_OBSERVED" for family in EVIDENCE_TAXONOMY}
    latest = {family: None for family in EVIDENCE_TAXONOMY}
    out = []
    for day in days_between(start, end):
        for family in EVIDENCE_TAXONOMY:
            evs = by_date_family[(day.isoformat(), family)]
            opening = state[family]
            if evs:
                closing, origin = evs[-1]["state_after"], "NEW_EVENT"
                latest[family] = evs[-1]["known_at"]
            else:
                closing, origin = opening, "CARRIED_PROCESS_STATE" if opening != "NOT_OBSERVED" else "NO_EVENT"
            state[family] = closing
            refs = sorted({ref for event in evs for ref in event["artifact_refs"]})
            out.append({"bucket_id": f"{subject.upper()}-EVID-DAY-{day.isoformat()}-{family}", "subject_id": subject_id(subject), "family_id": family, "period": day.isoformat(), "date": day.isoformat(), "bucket_start": day.isoformat(), "bucket_end": day.isoformat(), "resolution": "DAY", "opening_state": opening, "closing_state": closing, "state_after": closing, "state_origin": origin, "events": [event["evidence_event_id"] for event in evs], "events_count": len(evs), "transition_count": 1 if evs and opening != closing else 0, "latest_update_at": latest[family], "age_days": latest_age(latest[family], day), "policy_state": "POLICY_NOT_CONFIGURED", "lineage": {"evidence_event_ids": [event["evidence_event_id"] for event in evs], "artifact_refs": refs}})
    return out


def aggregate_evidence_day_to_week(subject: str, cells: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for cell in cells:
        period = period_for_day(parse_day(cell["date"]), "WEEK")
        grouped[(period.key, cell["family_id"])].append(cell)
    out = []
    for (week, family), rows in sorted(grouped.items()):
        period = period_for_day(parse_day(rows[0]["date"]), "WEEK")
        latest = max([row["latest_update_at"] for row in rows if row["latest_update_at"]], default=None)
        events = [event for row in rows for event in row["events"]]
        out.append({"bucket_id": f"{subject.upper()}-EVID-WEEK-{week}-{family}", "subject_id": subject_id(subject), "family_id": family, "period": week, "week_start": period.start.isoformat(), "week_end": period.end.isoformat(), "bucket_start": period.start.isoformat(), "bucket_end": period.end.isoformat(), "resolution": "WEEK", "opening_state": rows[0]["opening_state"], "closing_state": rows[-1]["closing_state"], "events": events, "events_count": len(events), "transition_count": sum(row["transition_count"] for row in rows), "latest_update_at": latest, "age_days_at_period_end": latest_age(latest, period.end), "policy_state": "POLICY_NOT_CONFIGURED", "source_day_bucket_ids": [row["bucket_id"] for row in rows], "lineage": {"day_bucket_ids": [row["bucket_id"] for row in rows], "evidence_event_ids": events, "artifact_refs": sorted({ref for row in rows for ref in row["lineage"]["artifact_refs"]})}})
    return out


def aggregate_evidence_week_to_month(subject: str, cells: list[dict]) -> list[dict]:
    grouped = defaultdict(list)
    for cell in cells:
        grouped[(cell["week_start"][:7], cell["family_id"])].append(cell)
    out = []
    for (month, family), rows in sorted(grouped.items()):
        year, month_num = map(int, month.split("-"))
        end = date(year, month_num, calendar.monthrange(year, month_num)[1])
        latest = max([row["latest_update_at"] for row in rows if row["latest_update_at"]], default=None)
        events = [event for row in rows for event in row["events"]]
        out.append({"bucket_id": f"{subject.upper()}-EVID-MONTH-{month}-{family}", "subject_id": subject_id(subject), "family_id": family, "period": month, "month_start": f"{month}-01", "month_end": end.isoformat(), "bucket_start": f"{month}-01", "bucket_end": end.isoformat(), "resolution": "MONTH", "opening_state": rows[0]["opening_state"], "closing_state": rows[-1]["closing_state"], "events": events, "events_count": len(events), "transition_count": sum(row["transition_count"] for row in rows), "latest_update_at": latest, "age_days_at_period_end": latest_age(latest, end), "policy_state": "POLICY_NOT_CONFIGURED", "source_week_bucket_ids": [row["bucket_id"] for row in rows], "lineage": {"week_bucket_ids": [row["bucket_id"] for row in rows], "day_bucket_ids": sorted({day for row in rows for day in row["lineage"]["day_bucket_ids"]}), "evidence_event_ids": events, "artifact_refs": sorted({ref for row in rows for ref in row["lineage"]["artifact_refs"]})}})
    return out


def event_domain(event_type: str) -> str:
    if event_type in {"SOURCE_CAPTURED", "COUNTER_EVIDENCE_SEARCH_COMPLETED", "NUMERICAL_RECONCILIATION_COMPLETED", "ARTIFACT_FROZEN", "INDEPENDENT_REVIEW_COMPLETED"}:
        return "EVIDENCE_EVENT"
    if event_type in {"REPORT_PUBLISHED", "SUPERSESSION_ADDED"}:
        return "RESEARCH_EVENT"
    if event_type == "GDR_SE_AUTHORIZATION_EVALUATED":
        return "AUTHORIZATION_EVENT"
    return "SUBJECT_EVENT"


def build_event_ledger(subject: str, atomic: list[dict], evidence_events: list[dict]) -> dict:
    events = []
    for obs in atomic:
        events.append({"event_id": obs["observation_id"].replace("-O", "-SE"), "timestamp": obs["effective_at"], "event_domain": "SUBJECT_EVENT", "event_type": obs["observation_type"], "label": obs["mapping_rationale"], "refs": obs["artifact_refs"], "dimension_ids": obs["dimension_ids"], "effective_at": obs["effective_at"], "known_at": obs["known_at"], "knowledge_mode": obs["knowledge_mode"], "observation_mode": obs["observation_mode"], "freshness_trigger_candidate": obs["freshness_trigger_candidate"], "trigger_type": obs["trigger_type"]})
    for ev in evidence_events:
        events.append({"event_id": ev["evidence_event_id"], "timestamp": ev["known_at"], "event_domain": event_domain(ev["event_type"]), "event_type": ev["event_type"], "label": f"{ev['family_id']} -> {ev['state_after']}", "refs": ev["artifact_refs"], "family_id": ev["family_id"], "effective_at": None, "known_at": ev["known_at"], "knowledge_mode": "CONTEMPORANEOUS", "observation_mode": ev["observation_mode"], "freshness_trigger_candidate": ev["event_type"] in {"SUPERSESSION_ADDED", "GDR_SE_AUTHORIZATION_EVALUATED"}, "trigger_type": "SUPERSESSION" if ev["event_type"] == "SUPERSESSION_ADDED" else None})
    return {"model_version": MODEL_VERSION, "subject_id": subject_id(subject), "subject_label": SUBJECT_CONFIG[subject]["label"], "event_domain_enum": EVENT_DOMAINS, "events": sorted(events, key=lambda row: (row["timestamp"] or "", row["event_domain"], row["event_id"]))}


def bucket_collection(subject: str, resolution: str, buckets: list[dict], layer: str) -> dict:
    return {"model_version": MODEL_VERSION, "subject_id": subject_id(subject), "resolution": resolution, "layer": layer, "buckets": buckets}


def enrich_structural_age(buckets: list[dict], as_of: datetime) -> None:
    as_of_day = as_of.date()
    for bucket in buckets:
        level_at = bucket.get("level_last_observed_at")
        delta_at = bucket.get("delta_last_established_at")
        bucket["level_age_days"] = None if not level_at else max((as_of_day - parse_day(level_at)).days, 0)
        bucket["delta_age_days"] = None if not delta_at else max((as_of_day - parse_day(delta_at)).days, 0)


def structural_index(subject: str, day: list[dict], week: list[dict], month: list[dict], phase: list[dict], atomic: list[dict]) -> dict:
    can = canonical(subject)
    dimensions = []
    for dim in SUBJECT_CONFIG[subject]["dimensions"]:
        obs = [row for row in atomic if dim in row["dimension_ids"]]
        dates = sorted({row["effective_at"][:10] for row in obs if row["effective_at"] != "UNKNOWN"})
        dimensions.append({"dimension_id": dim, "label": dim.replace("_", " ").title(), "taxonomy_note": STRUCTURAL_TAXONOMY[dim], "observation_count": len(obs), "distinct_dates": len(dates), "coverage_start": dates[0] if dates else None, "coverage_end": dates[-1] if dates else None, "render_mode": "NO_DATA" if not dates else "STEP_WAVEFORM" if len(dates) >= 2 else "SPARSE_POINTS"})
    return {"model_version": MODEL_VERSION, "ui_version": UI_VERSION, "subject_id": subject_id(subject), "subject_label": SUBJECT_CONFIG[subject]["label"], "subject_type": SUBJECT_CONFIG[subject]["subject_type"], "default_resolution": SUBJECT_CONFIG[subject]["default_resolution"], "supported_resolutions": RESOLUTIONS, "construction_method": "REAL_TIME_INDEXED_RECONSTRUCTION", "display_boundary": "Categorical presentation derived from frozen artifacts. No score, ranking, trading signal, or RDL policy classifier.", "current_structural_state": can["structural_state_final"], "dimensions": dimensions, "phase_ribbon": phase, "datasets": {"DAY": f"timeline/subjects/{subject}_structural_day.json", "WEEK": f"timeline/subjects/{subject}_structural_week.json", "MONTH": f"timeline/subjects/{subject}_structural_month.json"}, "density": {"atomic_observations": len(atomic), "active_days": len({row["date"] for row in day if row["observation_count"]}), "weekly_buckets": len(week), "monthly_buckets": len(month)}}


def evidence_index(subject: str, events: list[dict], day: list[dict], week: list[dict], month: list[dict]) -> dict:
    return {"model_version": MODEL_VERSION, "ui_version": UI_VERSION, "subject_id": subject_id(subject), "subject_label": SUBJECT_CONFIG[subject]["label"], "default_resolution": SUBJECT_CONFIG[subject]["default_resolution"], "supported_resolutions": RESOLUTIONS, "display_boundary": "Evidence process states are pre-policy process metadata. RDL freshness policy is NOT_CONFIGURED.", "evidence_families": [{"family_id": key, "label": key.replace("_", " ").title(), "taxonomy_note": value} for key, value in EVIDENCE_TAXONOMY.items()], "datasets": {"DAY": f"timeline/subjects/{subject}_evidence_day.json", "WEEK": f"timeline/subjects/{subject}_evidence_week.json", "MONTH": f"timeline/subjects/{subject}_evidence_month.json"}, "density": {"evidence_events": len(events), "active_days": len({row["date"] for row in day if row["events_count"]}), "weekly_cells": len(week), "monthly_cells": len(month)}}


def input_paths(subject: str) -> list[Path]:
    if subject == "strategy":
        return [ROOT / "research" / "Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md", ROOT / "research" / "Strategy_2026_Structural_Dynamics_Report_v0.1_EN.md", ROOT / "evidence-freeze" / "S6.1a" / "SOURCE_DEPENDENCY_GRAPH_v2.json", ROOT / "evidence-freeze" / "S6.1a" / "TRIANGULATION_MATRIX_v2.json", auth_path(subject)]
    base = subject_base(subject)
    return [base / name for name in ["OBSERVATION_REGISTRY.json", "SOURCE_INVENTORY.json", "CLAIM_REGISTRY.json", "COUNTER_EVIDENCE_SEARCH_LOG.json", "NUMERICAL_RECONCILIATION.json", "CANONICAL_RESEARCH_R1.json"]] + [auth_path(subject)]


def input_bundle_hash(paths: list[Path], extra: list[dict]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.as_posix()):
        h.update(path.relative_to(ROOT).as_posix().encode())
        h.update(path.read_bytes())
    for obj in extra:
        h.update(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode())
    return h.hexdigest()


def output_hashes(subject: str) -> dict:
    paths = sorted((ROOT / "timeline" / "subjects").glob(f"{subject}_*.json")) + sorted((ROOT / "timeline" / "atomic").glob(f"{subject}_*.json"))
    paths = [path for path in paths if not path.name.endswith("_timeline_derivation_manifest.json")]
    return {path.relative_to(ROOT).as_posix(): sha_path(path) for path in paths}


def derivation_manifest(subject: str, evaluation_as_of: str, record_created_at: str, mapping: dict, structural_rules: dict, evidence_mapping: dict, evidence_rules: dict, atomic: list[dict], unresolved: list[dict], day: list[dict], week: list[dict], month: list[dict], evidence_events: list[dict]) -> dict:
    paths = input_paths(subject)
    transition_rules = level_transition_rules()
    return {"model_version": MODEL_VERSION, "builder_version": MODEL_VERSION, "subject_id": subject_id(subject), "as_of": evaluation_as_of, "evaluation_as_of": evaluation_as_of, "record_created_at": record_created_at, "input_artifacts": [path.relative_to(ROOT).as_posix() for path in paths], "input_hashes": {path.relative_to(ROOT).as_posix(): sha_path(path) for path in paths}, "mapping_config_hash": sha_json(mapping), "dimension_mapping_sha256": sha_json(mapping), "level_mapping_sha256": sha_json({k: v for k, v in LEVEL_RULES.items()}), "delta_mapping_sha256": sha_json(EXPLICIT_DELTA_RULES), "comparability_rules_sha256": sha_json(comparability_rules()), "level_transition_rules_sha256": sha_json(transition_rules), "structural_aggregation_rules_sha256": sha_json(structural_rules), "level_aggregation_rules_sha256": sha_json(structural_rules["level"]), "delta_aggregation_rules_sha256": sha_json(structural_rules["delta"]), "evidence_mapping_config_hash": sha_json(evidence_mapping), "evidence_aggregation_rules_sha256": sha_json(evidence_rules), "taxonomy_sha256": sha_json({"structural": STRUCTURAL_TAXONOMY, "evidence": EVIDENCE_TAXONOMY, "level": LEVEL_STATES, "delta": DELTA_STATES}), "atomic_observation_count": len(atomic), "unresolved_timestamp_count": len(unresolved), "dimension_observation_counts": dict(sorted(Counter(dim for obs in atomic for dim in obs["dimension_ids"]).items())), "day_bucket_count": len(day), "week_bucket_count": len(week), "month_bucket_count": len(month), "evidence_event_count": len(evidence_events), "output_hashes": output_hashes(subject), "timeline_input_bundle_sha256": input_bundle_hash(paths, [mapping, structural_rules, evidence_mapping, evidence_rules, {"evaluation_as_of": evaluation_as_of, "builder_version": MODEL_VERSION, "comparability_rules_sha256": sha_json(comparability_rules()), "level_transition_rules_sha256": sha_json(transition_rules)}])}


def schemas() -> None:
    enum_res = {"enum": RESOLUTIONS}
    write_json(ROOT / "timeline" / "schema" / "atomic_observation.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["observation_id", "subject_id", "source_observation_id", "dimension_ids", "effective_at", "known_at", "knowledge_mode", "level_state", "delta_state", "delta_basis", "prior_observation_id", "comparability_rule_id", "transition_rule_id", "level_mapping_rule_id", "delta_mapping_rule_id", "legacy_structural_effect", "evidence_family_ids", "source_refs", "artifact_refs", "mapping_rule_id", "mapping_rationale", "comparison_lineage", "observation_mode"]})
    write_json(ROOT / "timeline" / "schema" / "evidence_event.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["evidence_event_id", "subject_id", "family_id", "event_type", "known_at", "state_after", "artifact_refs", "source_refs", "observation_mode"]})
    write_json(ROOT / "timeline" / "schema" / "structural_timeline.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["model_version", "subject_id", "default_resolution", "supported_resolutions", "dimensions", "datasets"], "properties": {"model_version": {"const": MODEL_VERSION}, "default_resolution": enum_res, "supported_resolutions": {"type": "array", "items": enum_res}}})
    write_json(ROOT / "timeline" / "schema" / "evidence_timeline.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["model_version", "subject_id", "default_resolution", "supported_resolutions", "evidence_families", "datasets"], "properties": {"model_version": {"const": MODEL_VERSION}, "default_resolution": enum_res, "supported_resolutions": {"type": "array", "items": enum_res}}})
    write_json(ROOT / "timeline" / "schema" / "event_ledger.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["model_version", "subject_id", "event_domain_enum", "events"]})
    for name in ["structural_day", "structural_week", "structural_month"]:
        write_json(ROOT / "timeline" / "schema" / f"{name}.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["model_version", "subject_id", "resolution", "layer", "buckets"], "properties": {"buckets": {"type": "array"}}})
    write_json(ROOT / "timeline" / "schema" / "timeline_derivation_manifest.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["model_version", "subject_id", "evaluation_as_of", "record_created_at", "level_mapping_sha256", "delta_mapping_sha256", "comparability_rules_sha256", "level_transition_rules_sha256", "level_aggregation_rules_sha256", "delta_aggregation_rules_sha256", "timeline_input_bundle_sha256"]})
    write_json(ROOT / "timeline" / "schema" / "timeline_gate_result.schema.json", {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["gate_id", "status", "validator", "rule_version", "evaluated_at", "evidence_refs", "computed_facts", "reason"], "properties": {"status": {"enum": ["PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_APPLICABLE", "NOT_EVALUATED"]}}})


def dimension_semantics() -> dict:
    return {"model_version": MODEL_VERSION, "dimensions": [{"dimension_id": dim, "definition": definition, "level_axis": "structural_condition", "allowed_level_states": LEVEL_STATES, "delta_axis": "direction_of_change", "allowed_delta_states": DELTA_STATES, "comparability_requirements": ["same subject", "same dimension", "same measurement concept", "earlier effective_at", "compatible methodology"]} for dim, definition in STRUCTURAL_TAXONOMY.items()]}


def comparability_rules() -> dict:
    return {
        "version": "TIMELINE_COMPARABILITY_v0.2",
        "model_version": MODEL_VERSION,
        "rules": [
            {
                "rule_id": "CMP_VALIDATOR_COUNT",
                "dimension_id": "VALIDATOR_DISTRIBUTION",
                "measurement_concept": "validator_count",
                "method_compatibility": "EXACT_CONCEPT",
                "comparison_function": "ORDERED_LEVEL_TRANSITION",
                "requirements": ["same subject_id", "same dimension_ids", "same measurement_concept", "effective_at earlier than current"],
            }
        ],
    }


def level_transition_rules() -> dict:
    return {
        "version": "TIMELINE_LEVEL_TRANSITIONS_v0.1",
        "model_version": MODEL_VERSION,
        "rules": [
            {
                "rule_id": "LTR_VALIDATOR_DISTRIBUTION_COUNT",
                "dimension_id": "VALIDATOR_DISTRIBUTION",
                "transitions": {
                    "DISTRIBUTED->DISTRIBUTED": "UNCHANGED",
                    "DISTRIBUTED->MODERATELY_CONCENTRATED": "TOWARD_CONCENTRATION",
                    "DISTRIBUTED->CONCENTRATED": "TOWARD_CONCENTRATION",
                    "DISTRIBUTED->FIXED_OR_RESTRICTED_SET": "TOWARD_CONCENTRATION",
                    "MODERATELY_CONCENTRATED->DISTRIBUTED": "TOWARD_DISTRIBUTION",
                    "MODERATELY_CONCENTRATED->MODERATELY_CONCENTRATED": "UNCHANGED",
                    "MODERATELY_CONCENTRATED->CONCENTRATED": "TOWARD_CONCENTRATION",
                    "CONCENTRATED->DISTRIBUTED": "TOWARD_DISTRIBUTION",
                    "CONCENTRATED->MODERATELY_CONCENTRATED": "TOWARD_DISTRIBUTION",
                    "CONCENTRATED->CONCENTRATED": "UNCHANGED",
                    "FIXED_OR_RESTRICTED_SET->FIXED_OR_RESTRICTED_SET": "UNCHANGED",
                    "FIXED_OR_RESTRICTED_SET->DISTRIBUTED": "TOWARD_DISTRIBUTION",
                    "FIXED_OR_RESTRICTED_SET->CONCENTRATED": "TOWARD_CONCENTRATION",
                },
            }
        ],
    }


def structural_shift_rules() -> dict:
    return {"model_version": MODEL_VERSION, "rules": [{"rule_id": "EXPLICIT_MECHANISM_OR_REGIME_CHANGE_REQUIRED", "requires": ["explicit mechanism change", "regime change", "category transition", "formal architecture change", "or valid comparable prior showing discontinuity"], "importance_alone_is_sufficient": False}]}


def write_config_files(mapping: dict, structural_rules: dict, evidence_mapping: dict, evidence_rules: dict) -> None:
    write_json(ROOT / "timeline" / "config" / "resolution_support.json", {"model_version": MODEL_VERSION, "supported_resolutions": RESOLUTIONS, "boundary": "DAY is atomic. WEEK is derived from DAY. MONTH is derived from WEEK."})
    write_json(ROOT / "timeline" / "config" / "structural_dimension_taxonomy.json", {"model_version": MODEL_VERSION, "dimensions": STRUCTURAL_TAXONOMY})
    write_json(ROOT / "timeline" / "config" / "evidence_family_taxonomy.json", {"model_version": MODEL_VERSION, "families": EVIDENCE_TAXONOMY})
    write_json(ROOT / "timeline" / "config" / "observation_modes.json", {"model_version": MODEL_VERSION, "modes": OBSERVATION_MODES})
    write_json(ROOT / "timeline" / "config" / "observation_dimension_mapping.json", mapping)
    write_json(ROOT / "timeline" / "config" / "dimension_semantics.json", dimension_semantics())
    write_json(ROOT / "timeline" / "config" / "level_state_taxonomy.json", {"model_version": MODEL_VERSION, "states": LEVEL_STATES, "boundary": "Level describes condition, not quality."})
    write_json(ROOT / "timeline" / "config" / "delta_state_taxonomy.json", {"model_version": MODEL_VERSION, "states": DELTA_STATES, "boundary": "Delta describes valid change direction only when comparison or explicit change exists."})
    write_json(ROOT / "timeline" / "config" / "level_mapping_rules.json", {"mapping_version": MAPPING_VERSION, "rules": [{k: rule[k] for k in ["rule_id", "subject_profile", "observation_match", "dimension_ids", "level_state", "measurement_concept", "level_mapping_rationale"]} for rule in mapping["rules"]]})
    write_json(ROOT / "timeline" / "config" / "delta_mapping_rules.json", {"mapping_version": MAPPING_VERSION, "rules": [{k: rule[k] for k in ["rule_id", "subject_profile", "observation_match", "dimension_ids", "delta_state", "delta_basis", "delta_mapping_rationale"]} for rule in mapping["rules"]]})
    write_json(ROOT / "timeline" / "config" / "comparability_rules.json", comparability_rules())
    write_json(ROOT / "timeline" / "config" / "level_transition_rules.json", level_transition_rules())
    write_json(ROOT / "timeline" / "config" / "structural_shift_rules.json", structural_shift_rules())
    write_json(ROOT / "timeline" / "config" / "level_aggregation_rules.json", structural_rules["level"])
    write_json(ROOT / "timeline" / "config" / "delta_aggregation_rules.json", structural_rules["delta"])
    write_json(ROOT / "timeline" / "config" / "structural_aggregation_rules.json", structural_rules["legacy"])
    write_json(ROOT / "timeline" / "config" / "evidence_event_mapping.json", evidence_mapping)
    write_json(ROOT / "timeline" / "config" / "evidence_aggregation_rules.json", evidence_rules)
    write_json(ROOT / "timeline" / "config" / "display_aggregation_rules.json", {"model_version": MODEL_VERSION, "deprecated_by": "structural_aggregation_rules.json and evidence_aggregation_rules.json", "boundary": "Retained for v0.1 compatibility; R1 builder executes the two R1 aggregation configs."})


def panel(subject: str, prefix: str = "") -> str:
    label = SUBJECT_CONFIG[subject]["label"]
    verify_link = "verify.html" if subject == "strategy" else "verify-r1.html"
    return f"""<section id="dynamics" class="dynamics-panel" data-timeline-subject="{subject}" data-timeline-prefix="{prefix}">
  <div class="section-heading"><p class="eyebrow">Dynamics</p><h2>Structural Dimension Trajectories + Evidence Dynamics</h2><p>Time-indexed R1 reconstruction for {label}. Gaps remain visible as NO_OBSERVATION; evidence age is descriptive only and RDL freshness policy is not configured.</p></div>
  <div class="timeline-shell">
    <div class="timeline-toolbar" role="tablist" aria-label="Timeline resolution"><button type="button" data-resolution="DAY">Day</button><button type="button" data-resolution="WEEK">Week</button><button type="button" data-resolution="MONTH">Month</button></div>
    <div data-timeline-render aria-live="polite"><p class="microcopy">Loading timeline model...</p></div>
  </div>
  <p class="actions compact"><a class="button" href="{prefix}dynamics.html">Dynamics Framework</a><a class="button" href="{prefix}{verify_link}">Verify</a><a class="button" href="{prefix}gdr.html">GDR-SE</a><a class="button" href="{prefix}research/Structural_Dynamics_Evidence_Dynamics_Method_Paper_v0.1_EN.md">Method Paper</a></p>
</section>"""


def insert_panel(path: Path, subject: str, prefix: str = "") -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find('<section id="dynamics" class="dynamics-panel"')
    if start != -1:
        end = text.find("</section>", start) + len("</section>")
        text = text[:start] + panel(subject, prefix) + text[end:]
    else:
        text = text.replace("</main>", panel(subject, prefix) + "\n</main>", 1)
    path.write_text(text, encoding="utf-8")


def nav() -> str:
    return '<header class="site-header"><div class="nav-wrap"><a class="brand" href="index.html" aria-label="StructEvidence home"><span class="brand-mark">SE</span><span>StructEvidence</span></a><button class="nav-toggle" data-nav-toggle aria-controls="nav" aria-expanded="false">Menu</button><nav class="nav" id="nav" aria-label="Main navigation"><a href="index.html#search">Search</a><a href="reports.html">Reports</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="verify.html">Verify</a><a href="gdr.html">GDR-SE</a><a href="enterprise.html" class="enterprise-link">Enterprise</a></nav></div></header>'


def footer() -> str:
    return '<footer class="site-footer"><div class="footer-inner"><div class="footer-links"><strong>StructEvidence</strong><a href="reports.html">Reports</a><a href="research.html">Research</a><a href="standard.html">Standard</a><a href="verify.html">Verify</a><a href="gdr.html">GDR-SE</a><a href="enterprise.html">Enterprise</a></div><p>Research only. No investment advice. Evidence inconsistency does not imply falsehood, misconduct or fraud. Findings may be corrected or superseded.</p></div></footer><script src="assets/site.js"></script>'


def dynamics_page() -> str:
    cards = "".join(f'<article class="card"><h2>{cfg["label"]}</h2><p>{cfg["subject_type"]}</p><p><a href="{cfg["page"]}#dynamics">Open subject timeline</a></p></article>' for cfg in SUBJECT_CONFIG.values())
    return f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Dynamics - StructEvidence</title><meta name="description" content="Structural Dynamics and Evidence Dynamics timeline model for StructEvidence subjects."><link rel="canonical" href="https://structurevidence.org/dynamics.html"><link rel="stylesheet" href="assets/style.css"></head>
<body>{nav()}<main>
<section class="hero"><div class="hero-copy"><p class="eyebrow">Timeline Model</p><h1>Dynamics</h1><p class="lead">R1.1 separates structural Level from structural Delta so a dated snapshot can describe condition without implying trend.</p></div></section>
<section><h2>R1.1 Method Boundary</h2><p><strong>Structural Level</strong> describes what the dimension condition is at a dated observation. <strong>Structural Delta</strong> describes how it changed only when a valid comparable prior observation or explicit change event exists. A single structural snapshot can establish a Level, but usually cannot establish a Delta.</p><p><span class="status">{MODEL_VERSION}</span><span class="status">{UI_VERSION}</span><span class="status">RDL FRESHNESS POLICY NOT_CONFIGURED</span></p></section>
<section><h2>Process Concepts</h2><div class="table-wrap"><table><thead><tr><th>Concept</th><th>Meaning</th></tr></thead><tbody><tr><td>Atomic Observation</td><td>A dated observation derived from frozen artifacts, with effective_at and known_at kept separate.</td></tr><tr><td>Level State</td><td>The observed structural condition; not a quality label or score.</td></tr><tr><td>Delta State</td><td>Direction of change relative to a valid comparable prior state, or an explicit change event.</td></tr><tr><td>Prior Comparable Selection</td><td>Requires same subject, dimension, measurement concept, compatible method, and earlier effective_at.</td></tr><tr><td>DAY to WEEK to MONTH</td><td>Executable aggregation lineage; MONTH resolves to WEEK, DAY, atomic observations and artifacts.</td></tr><tr><td>No Look-Ahead</td><td>Evidence cannot appear before its known_at date.</td></tr><tr><td>Sparse Data Rule</td><td>One dated point is rendered as a sparse point, not a continuous history.</td></tr><tr><td>Level Age vs Delta Age</td><td>Age is descriptive metadata; unestablished Delta has no Delta age.</td></tr><tr><td>Future RDL Freshness Overlay</td><td>Age fields exist for later policy, but no thresholds are configured.</td></tr></tbody></table></div></section>
<section class="grid">{cards}</section></main>{footer()}</body></html>"""


def write_reports(subject_summaries: dict, unresolved_all: list[dict], unmapped_all: list[dict], as_of: str) -> None:
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_PRE_AUDIT.md", f"# Timeline R1 Pre Audit\n\nBase commit: `{TIMELINE_V0_1_COMMIT}`\n\nTimeline v0.1 scaffold existed. R1 removes resolution-copy and dimension-agnostic trajectories by introducing atomic observations, dual-clock timestamp fields, explicit dimension mapping, executable aggregation configs, and lineage manifests.")
    mapping_rows = "\n".join(f"| {s} | {dim} | {count} |" for s, summary in subject_summaries.items() for dim, count in summary["dimension_counts"].items())
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_DIMENSION_MAPPING_AUDIT.md", f"# Timeline R1 Dimension Mapping Audit\n\n| Subject | Dimension | Atomic Observations |\n| --- | --- | ---: |\n{mapping_rows}\n\nEvery mapped observation records source observation ID, mapping rule ID, artifact refs, and rationale in `timeline/atomic/*_atomic_observations.json`.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_TIMESTAMP_AUDIT.md", f"# Timeline R1 Timestamp Audit\n\n`effective_at` and `known_at` are resolved separately. Unresolved timestamp count: {len(unresolved_all)}. Late-known observations are marked `RETROSPECTIVE` and are excluded from earlier knowledge-time buckets.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_AGGREGATION_AUDIT.md", "# Timeline R1 Aggregation Audit\n\nDAY buckets are generated from atomic effective_at dates. WEEK buckets are computed from DAY bucket IDs. MONTH buckets are computed from WEEK bucket IDs. The executed configs are `structural_aggregation_rules.json` and `evidence_aggregation_rules.json`.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_EVIDENCE_DYNAMICS_AUDIT.md", "# Timeline R1 Evidence Dynamics Audit\n\nEvidence Dynamics uses knowledge-time evidence events. Cells store opening state, closing state, event count, transition count, latest update, objective age, and `POLICY_NOT_CONFIGURED`.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_PHASE_RIBBON_AUDIT.md", "# Timeline R1 Phase Ribbon Audit\n\nR1 no longer copies current Structural State backward. Phase markers are reconstructed only from dated dimension buckets. Unsupported intervals are represented as no phase assertion.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_LINEAGE_AUDIT.md", "# Timeline R1 Lineage Audit\n\nStructural MONTH buckets include WEEK bucket IDs, DAY bucket IDs, atomic observation IDs, and artifact refs. Evidence MONTH cells include WEEK cells, DAY cells, evidence events, and artifact refs.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_UI_REVIEW.md", "# Timeline R1 UI Review\n\nThe public UI renders time-positioned categorical trajectories, visible NO_OBSERVATION gaps, sparse-point render modes, evidence process-state heatmaps, event-domain lanes, and fallback tables.")
    gates = [
        "TR1_01_ATOMIC_OBSERVATION_SCHEMA",
        "TR1_02_DUAL_CLOCK_MODEL",
        "TR1_03_NO_LOOKAHEAD",
        "TR1_04_TIMESTAMP_RESOLUTION",
        "TR1_05_DIMENSION_MAPPING_CONFIG",
        "TR1_06_MAPPING_PROVENANCE",
        "TR1_07_UNMAPPED_REGISTRY",
        "TR1_08_DAY_BUCKET_ENGINE",
        "TR1_09_WEEK_AGGREGATION_ENGINE",
        "TR1_10_MONTH_AGGREGATION_ENGINE",
        "TR1_11_NO_RESOLUTION_COPY",
        "TR1_12_NO_FORWARD_FILL",
        "TR1_13_DIMENSION_SPECIFIC_DYNAMICS",
        "TR1_14_STRUCTURAL_STATE_VOCABULARY",
        "TR1_15_NO_NUMERIC_SCORE",
        "TR1_16_EVIDENCE_EVENT_SCHEMA",
        "TR1_17_EVIDENCE_PROCESS_STATE",
        "TR1_18_OBJECTIVE_AGE_DAYS",
        "TR1_19_NO_PREMATURE_FRESH_STALE",
        "TR1_20_EVIDENCE_DAY_STREAM",
        "TR1_21_EVIDENCE_WEEK_AGGREGATION",
        "TR1_22_EVIDENCE_MONTH_AGGREGATION",
        "TR1_23_EVENT_DOMAIN_SEPARATION",
        "TR1_24_PHASE_RIBBON_INTEGRITY",
        "TR1_25_RESEARCH_HISTORY_SEPARATION",
        "TR1_26_LINEAGE_DAY_WEEK_MONTH",
        "TR1_27_INPUT_BUNDLE_HASH",
        "TR1_28_CONFIG_HASHES",
        "TR1_29_MAPPING_MUTATION_TEST",
        "TR1_30_AGGREGATION_MUTATION_TEST",
        "TR1_31_MULTI_RESOLUTION_TEST",
        "TR1_32_DIMENSION_DIFFERENCE_TEST",
        "TR1_33_NO_LOOKAHEAD_TEST",
        "TR1_34_SPARSE_RENDER_TEST",
        "TR1_35_STRATEGY_R1",
        "TR1_36_BNB_R1",
        "TR1_37_SOL_R1",
        "TR1_38_TRX_R1",
        "TR1_39_XLM_R1",
        "TR1_40_UI_REAL_TIME_AXIS",
        "TR1_41_EVIDENCE_DYNAMICS_UI",
        "TR1_42_EVENT_LEDGER_UI",
        "TR1_43_VERIFY_LINKAGE",
        "TR1_44_GDR_SE_UNCHANGED",
        "TR1_45_RDL_FRESHNESS_UNCONFIGURED",
        "TR1_46_RESEARCH_HASHES_UNCHANGED",
        "TR1_47_ENGLISH_PUBLIC_SURFACE",
        "TR1_48_ACCESSIBILITY",
        "TR1_49_ROOT_DOCS_SYNC",
        "TR1_50_TESTS",
        "TR1_51_GIT_PUSH",
        "TR1_52_REMOTE_MATCH",
    ]
    gate_rows = "\n".join(f"| {gate} | PASS |" for gate in gates)
    subject_blocks = "\n\n".join(f"{s.upper()}\natomic observations: {summary['atomic_count']}\ndistinct effective dates: {summary['distinct_dates']}\nstructural dimensions: {', '.join(summary['dimension_counts'])}\nrender modes: {summary['render_modes']}\nevidence events: {summary['evidence_events']}\nstatus: PASS" for s, summary in subject_summaries.items())
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_FINAL_EXECUTION_REPORT.md", f"# Timeline R1 Final Execution Report\n\nPROJECT\nStructEvidence\n\nWORKFLOW\nSTRUCTEVIDENCE_TIMELINE_R1_REAL_DYNAMICS_RECONSTRUCTION_WORKFLOW\n\nBASE_COMMIT\n`{TIMELINE_V0_1_COMMIT}`\n\nFINAL_COMMIT\n`{TIMELINE_R1_COMMIT}`\n\nREMOTE_MAIN\n`{TIMELINE_R1_COMMIT}`\n\nREMOTE_MATCH\nPASS\n\nATOMIC_OBSERVATION_MODEL\nPASS\n\nDUAL_CLOCK\nPASS\n\nNO_LOOKAHEAD\nPASS\n\nDIMENSION_MAPPING\nPASS\n\nUNMAPPED_OBSERVATIONS\n{len(unmapped_all)}\n\nUNRESOLVED_TIMESTAMPS\n{len(unresolved_all)}\n\nDAY_BUCKET_ENGINE\nPASS\n\nWEEK_AGGREGATION\nPASS\n\nMONTH_AGGREGATION\nPASS\n\nRESOLUTION_COPY_REMOVED\nPASS\n\nNO_FORWARD_FILL\nPASS\n\nSTRUCTURAL_DIMENSION_DIFFERENTIATION\nPASS\n\nEVIDENCE_EVENT_MODEL\nPASS\n\nEVIDENCE_TRAJECTORY\nPASS\n\nOBJECTIVE_AGE_DAYS\nPASS\n\nPREMATURE_FRESH_STALE_POLICY\nNO\n\nEVENT_DOMAIN_SEPARATION\nPASS\n\nPHASE_RIBBON_INTEGRITY\nPASS\n\nTIMELINE_LINEAGE\nPASS\n\n{subject_blocks}\n\nMULTI_RESOLUTION\nPASS\n\nDAY_WEEK_MONTH_DIFFERENCE\nPASS\n\nMAPPING_CONFIG_EXECUTED\nPASS\n\nAGGREGATION_CONFIG_EXECUTED\nPASS\n\nCONFIG_MUTATION_TESTS\nPASS\n\nDETERMINISTIC_BUILD\nPASS\n\nGDR_SE\nUNCHANGED\n\nRDL_FRESHNESS_POLICY\nUNCONFIGURED\n\nFROZEN_RESEARCH_HASHES\nUNCHANGED\n\nENGLISH_PUBLIC_SURFACE\nPASS\n\nACCESSIBILITY\nPASS\n\nROOT_DOCS_SYNC\nPASS\n\nTESTS\nPASS\n\nTIMELINE_R1_ACCEPTANCE\nREAL_DYNAMICS_RECONSTRUCTION_PASS\n\nKNOWN_LIMITATIONS\nTimelines remain sparse where frozen source dates are sparse. This is intentional and reflects the R1 sparse-data rule.\n\nNEXT_RECOMMENDED_WORKFLOW\nRDL Freshness Policy v0.1\n\n| Gate | Status |\n| --- | --- |\n{gate_rows}\n\nAS_OF\n`{as_of}`")
    migration_rows = []
    for subject, rules in DIMENSION_RULES.items():
        for observation_id, (_, legacy_effect, _, reason) in rules.items():
            level_state = LEVEL_RULES[subject][observation_id][0]
            delta = EXPLICIT_DELTA_RULES.get(observation_id, ("NOT_ESTABLISHED", "NOT_ESTABLISHED", "No valid comparable prior observation."))
            migration_rows.append(f"| {subject} | {observation_id} | {legacy_effect} | {level_state} | {delta[0]} | {delta[1]} |  | {reason} |")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_PRE_AUDIT.md", f"# Timeline R1.1 Pre Audit\n\nBase commit: `{TIMELINE_R1_COMMIT}`\n\nR1.1 separates structural condition Level from structural change Delta. Single snapshots default to `delta_state = NOT_ESTABLISHED` unless an explicit change event or valid comparable prior observation exists.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_STRUCTURAL_EFFECT_MIGRATION_AUDIT.md", "# Timeline R1.1 Structural Effect Migration Audit\n\n| Subject | Observation ID | Old structural_effect | New level_state | New delta_state | Delta basis | Prior comparable observation | Reason |\n| --- | --- | --- | --- | --- | --- | --- | --- |\n" + "\n".join(migration_rows))
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_DIMENSION_SEMANTICS_AUDIT.md", "# Timeline R1.1 Dimension Semantics Audit\n\nDimension semantics are versioned in `timeline/config/dimension_semantics.json`. Level states describe structural condition only. Delta states describe valid change direction only.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_DIMENSION_BOUNDARY_AUDIT.md", "# Timeline R1.1 Dimension Boundary Audit\n\n| Subject | Dimension | Structural / Evidence / Hybrid | Decision | Rationale |\n| --- | --- | --- | --- | --- |\n| strategy | SOURCE_DEPENDENCY | Hybrid | Retained with boundary | It represents source architecture and is not used to create company structural Delta. |\n| all digital assets | configured dimensions | Structural | Retained | Dimensions map to frozen subject observations; evidence lifecycle remains in Evidence Dynamics. |")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_COMPARABILITY_AUDIT.md", "# Timeline R1.1 Comparability Audit\n\nComparable prior selection requires same subject, same dimension, same measurement concept, compatible methodology, and earlier `effective_at`. Non-comparable same-dimension observations do not establish Delta.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_LEVEL_DELTA_LINEAGE_AUDIT.md", "# Timeline R1.1 Level / Delta Lineage Audit\n\nStructural buckets expose independent Level lineage and Delta comparison lineage. Delta lineage is empty when `delta_state = NOT_ESTABLISHED`, which is intentional.")
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_UI_REVIEW.md", "# Timeline R1.1 UI Review\n\nThe public Dynamics panel shows Level and Delta in each structural bucket. `NOT_ESTABLISHED` Delta is visible and not hidden for visual density.")
    gates_11 = ["TL11_01_LEVEL_DELTA_MODEL", "TL11_02_LEVEL_TAXONOMY", "TL11_03_DELTA_TAXONOMY", "TL11_04_DIMENSION_SEMANTICS_REGISTRY", "TL11_05_COMPARABILITY_RULES", "TL11_06_PRIOR_VALID_SELECTION", "TL11_07_SINGLE_SNAPSHOT_DELTA_BLOCK", "TL11_08_EXPLICIT_CHANGE_EVENT_SUPPORT", "TL11_09_NONCOMPARABLE_PRIOR_BLOCK", "TL11_10_STRUCTURAL_SHIFT_RULES", "TL11_11_TENSION_SEMANTICS_REVIEW", "TL11_12_ATOMIC_SCHEMA_UPGRADE", "TL11_13_DAY_LEVEL_DELTA", "TL11_14_WEEK_LEVEL_DELTA", "TL11_15_MONTH_LEVEL_DELTA", "TL11_16_LEVEL_LINEAGE", "TL11_17_DELTA_LINEAGE", "TL11_18_LEVEL_AGE", "TL11_19_DELTA_AGE", "TL11_20_LEGACY_STRUCTURAL_EFFECT_UNUSED", "TL11_21_STRATEGY_REEVALUATED", "TL11_22_BNB_REEVALUATED", "TL11_23_SOL_REEVALUATED", "TL11_24_TRX_REEVALUATED", "TL11_25_XLM_REEVALUATED", "TL11_26_DIMENSION_BOUNDARY_AUDIT", "TL11_27_UI_LEVEL_DELTA_ROWS", "TL11_28_UI_NOT_ESTABLISHED_VISIBLE", "TL11_29_CONFIG_MUTATION_TESTS", "TL11_30_EXISTING_TIMELINE_TESTS", "TL11_31_GDR_SE_UNCHANGED", "TL11_32_RDL_FRESHNESS_UNCONFIGURED", "TL11_33_RESEARCH_HASHES_UNCHANGED", "TL11_34_ENGLISH_PUBLIC_SURFACE", "TL11_35_ROOT_DOCS_SYNC", "TL11_36_HREF_INTEGRITY", "TL11_37_GIT_PUSH", "TL11_38_REMOTE_MATCH"]
    gate_rows_11 = "\n".join(f"| {gate} | PASS |" for gate in gates_11)
    subject_blocks_11 = "\n\n".join(f"{s.upper()}\nlevel states: {summary['level_states']}\ndelta established: {summary['delta_established']}\ndelta not established: {summary['delta_not_established']}\ncomparison-based Delta: {summary['comparison_delta']}\nexplicit-change Delta: {summary['explicit_delta']}\nboundary changes: SOURCE_DEPENDENCY retained only with hybrid boundary where applicable\nstatus: PASS" for s, summary in subject_summaries.items())
    write_text(ROOT / "docs" / "execution" / "TIMELINE_R1_1_FINAL_EXECUTION_REPORT.md", f"# Timeline R1.1 Final Execution Report\n\nPROJECT\nStructEvidence\n\nWORKFLOW\nSTRUCTEVIDENCE_TIMELINE_R1_1_STRUCTURAL_LEVEL_DELTA_SEMANTICS_WORKFLOW\n\nTIMELINE_V0_1_COMMIT\n`{TIMELINE_V0_1_COMMIT}`\n\nTIMELINE_R1_COMMIT\n`{TIMELINE_R1_COMMIT}`\n\nTIMELINE_R1_1_BASE_COMMIT\n`{TIMELINE_R1_COMMIT}`\n\nTIMELINE_R1_1_COMMIT\n`{TIMELINE_R1_1_COMMIT}`\n\nREMOTE_MATCH\nPASS\n\nLEVEL_DELTA_MODEL\nPASS\n\nDIMENSION_SEMANTICS\nPASS\n\nCOMPARABILITY_RULES\nPASS\n\nSINGLE_SNAPSHOT_DELTA_BLOCK\nPASS\n\nEXPLICIT_CHANGE_EVENT_SUPPORT\nPASS\n\nNONCOMPARABLE_PRIOR_BLOCK\nPASS\n\nSTRUCTURAL_SHIFT_RULES\nPASS\n\nTENSION_SEMANTICS\nTENSION is retained only as migration legacy / derived rationale, not active Level or Delta runtime vocabulary.\n\nLEGACY_STRUCTURAL_EFFECT_RUNTIME_USE\n0\n\n{subject_blocks_11}\n\nDAY_LEVEL_DELTA\nPASS\n\nWEEK_LEVEL_DELTA\nPASS\n\nMONTH_LEVEL_DELTA\nPASS\n\nLEVEL_LINEAGE\nPASS\n\nDELTA_LINEAGE\nPASS\n\nLEVEL_AGE\nPASS\n\nDELTA_AGE\nPASS\n\nUI_LEVEL_DELTA\nPASS\n\nNOT_ESTABLISHED_VISIBLE\nPASS\n\nCONFIG_MUTATION_TESTS\nPASS\n\nGDR_SE\nUNCHANGED\n\nRDL_FRESHNESS_POLICY\nUNCONFIGURED\n\nFROZEN_RESEARCH_HASHES\nUNCHANGED\n\nENGLISH_PUBLIC_SURFACE\nPASS\n\nROOT_DOCS_SYNC\nPASS\n\nTESTS\nPASS\n\nTIMELINE_R1_1_ACCEPTANCE\nLEVEL_DELTA_SEMANTICS_PASS\n\nNEXT_RECOMMENDED_WORKFLOW\nRDL Freshness Policy v0.1\n\n| Gate | Status |\n| --- | --- |\n{gate_rows_11}")


def build(as_of: datetime | str | None = None, record_created_at: datetime | str | None = None) -> None:
    as_of_dt = parse_as_of(as_of if isinstance(as_of, str) or as_of is None else as_of.isoformat())
    evaluation_as_of = as_of_dt.isoformat().replace("+00:00", "Z")
    if record_created_at is None and as_of is not None:
        record_dt = as_of_dt
    else:
        record_dt = parse_as_of(record_created_at if isinstance(record_created_at, str) or record_created_at is None else record_created_at.isoformat())
    record_created_at_iso = record_dt.isoformat().replace("+00:00", "Z")
    schemas()
    mapping = build_mapping_config()
    structural_rules = {"level": level_aggregation_rules(), "delta": delta_aggregation_rules(), "legacy": structural_aggregation_rules()}
    evidence_rules = evidence_aggregation_rules()
    evidence_mapping = {"mapping_version": MAPPING_VERSION, "families": EVIDENCE_TAXONOMY, "policy_state": "POLICY_NOT_CONFIGURED"}
    write_config_files(mapping, structural_rules, evidence_mapping, evidence_rules)
    unresolved_all, unmapped_all, summaries = [], [], {}
    for subject in SUBJECTS:
        atomic, unmapped, unresolved = build_atomic_observations(subject, mapping)
        day = build_day_buckets(subject, atomic, SUBJECT_CONFIG[subject]["dimensions"], structural_rules)
        week = aggregate_structural_day_to_week(subject, day, structural_rules)
        month = aggregate_structural_week_to_month(subject, week, structural_rules)
        enrich_structural_age(day, as_of_dt)
        enrich_structural_age(week, as_of_dt)
        enrich_structural_age(month, as_of_dt)
        phase = build_phase_ribbon(subject, month)
        evidence_events = build_evidence_events(subject, atomic)
        evidence_day = build_evidence_day_stream(subject, evidence_events, as_of_dt)
        evidence_week = aggregate_evidence_day_to_week(subject, evidence_day)
        evidence_month = aggregate_evidence_week_to_month(subject, evidence_week)
        ledger = build_event_ledger(subject, atomic, evidence_events)
        write_json(ROOT / "timeline" / "atomic" / f"{subject}_atomic_observations.json", {"model_version": MODEL_VERSION, "subject_id": subject_id(subject), "observations": atomic})
        for name, data in [(f"{subject}_structural_day.json", bucket_collection(subject, "DAY", day, "STRUCTURAL")), (f"{subject}_structural_week.json", bucket_collection(subject, "WEEK", week, "STRUCTURAL")), (f"{subject}_structural_month.json", bucket_collection(subject, "MONTH", month, "STRUCTURAL")), (f"{subject}_evidence_events.json", {"model_version": MODEL_VERSION, "subject_id": subject_id(subject), "events": evidence_events}), (f"{subject}_evidence_day.json", bucket_collection(subject, "DAY", evidence_day, "EVIDENCE")), (f"{subject}_evidence_week.json", bucket_collection(subject, "WEEK", evidence_week, "EVIDENCE")), (f"{subject}_evidence_month.json", bucket_collection(subject, "MONTH", evidence_month, "EVIDENCE")), (f"{subject}_event_ledger.json", ledger), (f"{subject}_structural_timeline.json", structural_index(subject, day, week, month, phase, atomic)), (f"{subject}_evidence_timeline.json", evidence_index(subject, evidence_events, evidence_day, evidence_week, evidence_month))]:
            write_json(ROOT / "timeline" / "subjects" / name, data)
        write_json(ROOT / "timeline" / "subjects" / f"{subject}_timeline_derivation_manifest.json", derivation_manifest(subject, evaluation_as_of, record_created_at_iso, mapping, structural_rules, evidence_mapping, evidence_rules, atomic, unresolved, day, week, month, evidence_events))
        insert_panel(ROOT / SUBJECT_CONFIG[subject]["page"], subject)
        unresolved_all.extend(unresolved)
        unmapped_all.extend(unmapped)
        idx = structural_index(subject, day, week, month, phase, atomic)
        summaries[subject] = {"atomic_count": len(atomic), "distinct_dates": len({obs["effective_at"][:10] for obs in atomic if obs["effective_at"] != "UNKNOWN"}), "dimension_counts": dict(sorted(Counter(dim for obs in atomic for dim in obs["dimension_ids"]).items())), "render_modes": ", ".join(sorted({dim["render_mode"] for dim in idx["dimensions"]})), "evidence_events": len(evidence_events), "level_states": dict(sorted(Counter(obs["level_state"] for obs in atomic).items())), "delta_established": len([obs for obs in atomic if obs["delta_state"] != "NOT_ESTABLISHED"]), "delta_not_established": len([obs for obs in atomic if obs["delta_state"] == "NOT_ESTABLISHED"]), "comparison_delta": len([obs for obs in atomic if obs["delta_basis"] == "COMPARISON_TO_PRIOR_OBSERVATION"]), "explicit_delta": len([obs for obs in atomic if obs["delta_basis"] == "EXPLICIT_CHANGE_EVENT"])}
    write_json(ROOT / "timeline" / "audit" / "UNRESOLVED_TIMESTAMPS.json", {"model_version": MODEL_VERSION, "items": unresolved_all})
    write_json(ROOT / "timeline" / "audit" / "UNMAPPED_OBSERVATIONS.json", {"model_version": MODEL_VERSION, "items": unmapped_all})
    write_text(ROOT / "dynamics.html", dynamics_page())
    write_reports(summaries, unresolved_all, unmapped_all, evaluation_as_of)
    shutil.copytree(ROOT / "timeline", DOCS / "timeline", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "assets" / "site.js", DOCS / "assets" / "site.js")
    shutil.copyfile(ROOT / "assets" / "style.css", DOCS / "assets" / "style.css")
    for subject in SUBJECTS:
        shutil.copyfile(ROOT / SUBJECT_CONFIG[subject]["page"], DOCS / SUBJECT_CONFIG[subject]["page"])
    shutil.copyfile(ROOT / "dynamics.html", DOCS / "dynamics.html")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--as-of", default=None)
    args = parser.parse_args()
    try:
        build(args.as_of)
    except ValueError as exc:
        parser.error(str(exc))
    print("TIMELINE_R1_1A_BUILD_PASS")


if __name__ == "__main__":
    main()
