#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
registry = json.loads((ROOT / "technical-risk/validation/CML_GATE_RESULTS.json").read_text())
assert len(registry["results"]) == 40
assert len({row["validator"] for row in registry["results"]}) == 40
for row in registry["results"]:
    assert row["computed_facts"]
    assert row["reason"] != "Validated by CML v0.1 runtime and negative-test suite."
assert registry["summary"] == {"PASS": 40, "FAIL": 0, "NOT_EVALUATED": 0}
print("CML_GATE_REGISTRY_PASS")
