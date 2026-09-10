from __future__ import annotations

import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "gdr-se" / "config" / "category_freshness.json"


def load_config(path: Path = CONFIG_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_freshness(category: str, last_reviewed: str, as_of: date, config: dict | None = None) -> tuple[str, str, dict]:
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
