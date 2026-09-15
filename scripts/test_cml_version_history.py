#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = [json.loads(line) for line in (ROOT / "technical-risk/CML_VERSION_HISTORY.jsonl").read_text().splitlines() if line.strip()]
assert len(rows) >= 2
assert rows[0]["protocol_version"] == "CML_v0.1"
audit = [row for row in rows if row.get("audit_policy_version") == "CML_AUDIT_v0.1a"]
assert len(audit) == 1
assert audit[0]["protocol_version"] == "CML_v0.1"
assert audit[0]["site_integration_version"] == "CML_SITE_INTEGRATION_v0.1a"
assert len(audit[0]["implementation_commit"]) == 40
print("CML_VERSION_HISTORY_PASS")
