from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "gdr-se" / "config" / "aggregation_rules.json"
MANDATORY_EFFECTS = {
    "hard_fail",
    "superseded",
    "human_review_required",
    "unresolved",
    "stale",
    "archived",
    "insufficient_data",
    "partial",
    "limited",
    "all_clear",
}
PUBLIC_STATUS = {
    "ALLOW_PUBLICATION": "CURRENT",
    "ALLOW_WITH_LIMITATIONS": "CURRENT_WITH_LIMITATIONS",
    "REFRESH_REQUIRED": "REFRESH_REQUIRED",
    "HUMAN_REVIEW_REQUIRED": "UNDER_REVIEW",
    "ABSTAIN": "WITHHELD",
    "VETO": "WITHHELD",
}


def load_rules(path: Path = CONFIG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_rules(rules: dict) -> None:
    if not rules.get("rule_version"):
        raise ValueError("GDR_SE_AGGREGATION_RULE_VERSION_REQUIRED")
    precedence = rules.get("precedence")
    if not isinstance(precedence, list) or not precedence:
        raise ValueError("GDR_SE_AGGREGATION_PRECEDENCE_REQUIRED")
    if len(precedence) != len(set(precedence)):
        raise ValueError("GDR_SE_AGGREGATION_PRECEDENCE_NOT_UNIQUE")
    allowed = set(PUBLIC_STATUS)
    unknown = sorted(set(precedence) - allowed)
    if unknown:
        raise ValueError(f"GDR_SE_UNKNOWN_AUTHORIZATION:{','.join(unknown)}")
    effects = rules.get("effects")
    if not isinstance(effects, dict):
        raise ValueError("GDR_SE_AGGREGATION_EFFECTS_REQUIRED")
    missing = sorted(MANDATORY_EFFECTS - set(effects))
    if missing:
        raise ValueError(f"GDR_SE_AGGREGATION_EFFECTS_MISSING:{','.join(missing)}")
    unknown_outputs = sorted({effects[name] for name in MANDATORY_EFFECTS} - set(precedence))
    if unknown_outputs:
        raise ValueError(f"GDR_SE_AGGREGATION_EFFECT_OUTPUT_NOT_IN_PRECEDENCE:{','.join(unknown_outputs)}")


def candidate_effects(gate_results: list[dict]) -> list[str]:
    by_id = {row["gate_id"]: row for row in gate_results}
    effects: list[str] = []
    if any(row["status"] in {"FAIL", "BLOCKED"} and row["severity"] == "HARD" for row in gate_results):
        effects.append("hard_fail")
    g10 = by_id.get("G10_EXPIRY_SUPERSESSION", {})
    if g10.get("status") in {"SUPERSEDED", "FAIL"}:
        effects.append("superseded")
    if any(row.get("computed_facts", {}).get("human_review_required") for row in gate_results):
        effects.append("human_review_required")
    if any(row["status"] == "UNRESOLVED" for row in gate_results):
        effects.append("unresolved")
    g3 = by_id.get("G3_EVIDENCE_FRESHNESS", {})
    if g3.get("status") == "STALE":
        effects.append("stale")
    if g3.get("status") == "ARCHIVED":
        effects.append("archived")
    g6 = by_id.get("G6_ECL_CONSISTENCY", {})
    if g6.get("status") == "INSUFFICIENT_DATA":
        effects.append("insufficient_data")
    if any(row["status"] == "PARTIAL" for row in gate_results):
        effects.append("partial")
    if any(row["status"] == "LIMITED" for row in gate_results):
        effects.append("limited")
    return effects or ["all_clear"]


def aggregate(gate_results: list[dict], rules: dict | None = None) -> str:
    rules = rules or load_rules()
    validate_rules(rules)
    precedence = {name: index for index, name in enumerate(rules["precedence"])}
    candidates = [rules["effects"][effect] for effect in candidate_effects(gate_results)]
    return min(candidates, key=lambda candidate: precedence[candidate])


def public_status(authorization: str) -> str:
    return PUBLIC_STATUS[authorization]
