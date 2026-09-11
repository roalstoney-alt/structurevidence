from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"RDL_FRESHNESS_POLICY_TEST_FAIL: {message}")


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main() -> None:
    profiles = read_json("rdl/freshness/config/freshness_profiles.json")
    text = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "rdl/freshness/config").rglob("*.json"))
    if "GLOBAL_MAX_AGE_DAYS" in text or "DEFAULT_MAX_AGE_DAYS" in text:
        fail("global freshness threshold found")
    configured = [row for row in profiles["profiles"] if row["status"] == "CONFIGURED"]
    unconfigured = [row for row in profiles["profiles"] if row["status"] != "CONFIGURED"]
    if len(configured) < 4 or not unconfigured:
        fail("configured/unconfigured rule split is missing")
    if not any(row["state_type"] == "DELTA" and row["status"] == "UNCONFIGURED" for row in profiles["profiles"]):
        fail("Delta sparse policy is not explicit")
    precedence = read_json("rdl/freshness/config/freshness_precedence.json")["precedence"]
    if precedence[:3] != ["SUPERSEDED", "EVENT_INVALIDATED", "UNDER_REVIEW"]:
        fail("policy precedence does not protect invalidation states")
    criticality = read_json("rdl/freshness/config/evidence_family_criticality.json")
    paid_rule = any(
        row["product_context"] == "PAID_VERIFIED_REPORT"
        and row["family_id"] == "INDEPENDENT_REVIEW"
        and row["criticality"] == "CRITICAL"
        for row in criticality["rules"]
    )
    if not paid_rule:
        fail("paid product criticality is not stricter")
    print("RDL_FRESHNESS_POLICY_TESTS_PASS")


if __name__ == "__main__":
    main()
