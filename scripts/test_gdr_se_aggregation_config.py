from __future__ import annotations

import copy
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from aggregation import aggregate, load_rules, validate_rules  # noqa: E402


def fail(message: str) -> None:
    raise SystemExit(f"GDR_SE_AGGREGATION_CONFIG_TEST_FAIL: {message}")


def main() -> None:
    rules = load_rules(ROOT / "gdr-se" / "config" / "aggregation_rules.json")
    validate_rules(rules)
    partial_gate = [{"gate_id": "G1_SCHEMA_INTEGRITY", "status": "PARTIAL", "severity": "HARD", "computed_facts": {}}]
    if aggregate(partial_gate, rules) != "ALLOW_WITH_LIMITATIONS":
        fail("default partial effect did not allow with limitations")
    mutated = copy.deepcopy(rules)
    mutated["effects"]["partial"] = "HUMAN_REVIEW_REQUIRED"
    if aggregate(partial_gate, mutated) != "HUMAN_REVIEW_REQUIRED":
        fail("effect mutation did not change authorization")
    precedence = copy.deepcopy(rules)
    precedence["precedence"] = ["VETO", "ALLOW_WITH_LIMITATIONS", "HUMAN_REVIEW_REQUIRED", "REFRESH_REQUIRED", "ABSTAIN", "ALLOW_PUBLICATION"]
    mixed = [
        {"gate_id": "G3_EVIDENCE_FRESHNESS", "status": "UNRESOLVED", "severity": "SOFT", "computed_facts": {}},
        {"gate_id": "G4_SOURCE_DEPENDENCY", "status": "PARTIAL", "severity": "SOFT", "computed_facts": {}},
    ]
    if aggregate(mixed, precedence) != "ALLOW_WITH_LIMITATIONS":
        fail("precedence mutation was not executed")
    invalid = copy.deepcopy(rules)
    del invalid["effects"]["partial"]
    try:
        validate_rules(invalid)
    except ValueError:
        pass
    else:
        fail("invalid aggregation config did not block")
    print("GDR_SE_AGGREGATION_CONFIG_TESTS_PASS")


if __name__ == "__main__":
    main()
