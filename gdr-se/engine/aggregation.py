from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "gdr-se" / "config" / "aggregation_rules.json"
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


def aggregate(gate_results: list[dict], rules: dict | None = None) -> str:
    rules = rules or load_rules()
    by_id = {row["gate_id"]: row for row in gate_results}
    if any(row["status"] in {"FAIL", "BLOCKED"} and row["severity"] == "HARD" for row in gate_results):
        return "VETO"
    g10 = by_id.get("G10_EXPIRY_SUPERSESSION", {})
    if g10.get("status") in {"SUPERSEDED", "FAIL"}:
        return "VETO"
    if any(row["status"] == "UNRESOLVED" or row.get("computed_facts", {}).get("human_review_required") for row in gate_results):
        return "HUMAN_REVIEW_REQUIRED"
    g3 = by_id.get("G3_EVIDENCE_FRESHNESS", {})
    if g3.get("status") in {"STALE", "ARCHIVED"}:
        return "REFRESH_REQUIRED"
    g6 = by_id.get("G6_ECL_CONSISTENCY", {})
    if g6.get("status") == "INSUFFICIENT_DATA":
        return "ABSTAIN"
    if any(row["status"] in {"PARTIAL", "LIMITED"} for row in gate_results):
        return "ALLOW_WITH_LIMITATIONS"
    return "ALLOW_PUBLICATION"


def public_status(authorization: str) -> str:
    return PUBLIC_STATUS[authorization]
