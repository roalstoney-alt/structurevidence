#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
allowed = set(json.loads((ROOT / "rdl/freshness/config/freshness_precedence.json").read_text())["precedence"])
records = list((ROOT / "technical-risk/records").glob("*/11_PUBLIC_RECORD.json"))
assert len(records) == 4
for path in records:
    cml = json.loads(path.read_text())["cml"]
    assert cml["freshness_state"] in allowed, path
    assert cml["freshness_reason"], path
    assert cml["freshness_rule_type"] in {"EVENT_DRIVEN", "REVISION_DRIVEN", "REVISION_AND_EXPIRY_DRIVEN", "SCOPE_AND_REVISION_DRIVEN", "UNCONFIGURED"}, path
print("CML_FRESHNESS_VOCABULARY_PASS")
