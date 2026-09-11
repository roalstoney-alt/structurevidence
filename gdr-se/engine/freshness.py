from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "gdr-se" / "config" / "category_freshness.json"
RDL_ADAPTER_PATH = ROOT / "rdl" / "freshness" / "gdr_g3_adapter.json"
SUBJECT_BY_CATEGORY = {
    "CORPORATE_TREASURY": "strategy",
    "L1_NETWORK": None,
}


def load_config(path: Path = CONFIG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_rdl_freshness(subject: str | None, category: str) -> tuple[str, str, dict] | None:
    if not RDL_ADAPTER_PATH.exists():
        return None
    adapter = json.loads(RDL_ADAPTER_PATH.read_text(encoding="utf-8"))
    key = (subject or "").lower()
    if not key:
        key = SUBJECT_BY_CATEGORY.get(category)
    if not key or key not in adapter.get("subjects", {}):
        return None
    entry = adapter["subjects"][key]
    record_path = ROOT / entry["record_path"]
    if not record_path.exists():
        return None
    record = json.loads(record_path.read_text(encoding="utf-8"))
    freshness_state = record["release_result"]["release_freshness_state"]
    status = adapter["mapping"].get(freshness_state, "UNRESOLVED")
    facts = {
        "policy_version": adapter["policy_version"],
        "subject": key,
        "release_freshness_state": freshness_state,
        "record_path": entry["record_path"],
        "input_bundle_hash": record["input_bundle_hash"],
        "configured_profile_count": sum(1 for row in record["dimension_level_results"] if row["freshness_state"] != "POLICY_NOT_CONFIGURED"),
    }
    return status, f"G3 consumed RDL Freshness Policy v0.1 release state {freshness_state}.", facts


def evaluate_freshness(category: str, last_reviewed: str, as_of: date, config: dict | None = None, subject: str | None = None) -> tuple[str, str, dict]:
    rdl = evaluate_rdl_freshness(subject, category)
    if rdl is not None:
        return rdl
    config = config or load_config()
    policy = (config.get("categories") or {}).get(category)
    if not policy:
        return "UNRESOLVED", f"No RDL freshness policy exists for category {category}.", {"category": category, "policy_status": "ABSENT"}
    status = policy.get("status")
    facts = {"category": category, "policy_status": status, "threshold_configured": status == "CONFIGURED"}
    if status == "UNCONFIGURED":
        return "UNRESOLVED", f"RDL freshness policy not configured for category {category}.", facts
    if status != "CONFIGURED":
        return "UNRESOLVED", f"Unknown freshness policy status for category {category}: {status}.", facts
    try:
        reviewed = date.fromisoformat(last_reviewed)
    except ValueError:
        facts["date_parse_error"] = last_reviewed
        return "UNRESOLVED", "Cannot parse last_reviewed date.", facts
    max_age = int(policy["max_age_days"])
    age_days = (as_of - reviewed).days
    facts.update({"last_reviewed": last_reviewed, "age_days": age_days, "max_age_days": max_age})
    if age_days <= max_age:
        return "PASS", "Evidence freshness is within the configured category threshold.", facts
    return "STALE", "Evidence is older than the configured category threshold.", facts
