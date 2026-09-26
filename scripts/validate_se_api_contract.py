#!/usr/bin/env python3
"""Check the OpenAPI contract against the Worker's operation manifest."""
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs" / "api" / "SE_API_v1.openapi.yaml"
IMPLEMENTATION = ROOT / "deploy" / "cloudflare-landing" / "se-api-v1.js"


def operation_manifest() -> set[tuple[str, str]]:
    source = IMPLEMENTATION.read_text(encoding="utf-8")
    match = re.search(r"SE_API_V1_OPERATIONS\s*=\s*Object\.freeze\((\[.*?\])\s*\);", source, re.DOTALL)
    if not match:
        raise ValueError("implementation operation manifest missing")
    return {(method.lower(), path) for method, path in json.loads(match.group(1))}


def validate_contract() -> dict[str, int | str]:
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    if spec.get("openapi") != "3.1.0" or spec.get("info", {}).get("version") != "SE_API_v1":
        raise ValueError("OpenAPI or API version mismatch")
    documented = {(method, path) for path, item in spec["paths"].items() for method in item if method in {"get", "post", "put", "patch", "delete"}}
    implemented = operation_manifest()
    if documented != implemented:
        raise ValueError(f"operation mismatch documented_only={sorted(documented - implemented)} implemented_only={sorted(implemented - documented)}")
    for method, path in sorted(documented):
        operation = spec["paths"][path][method]
        if not operation.get("operationId") or not operation.get("responses"):
            raise ValueError(f"operation contract incomplete: {method.upper()} {path}")
        expected = "201" if method == "post" and path in {"/requests", "/challenges", "/outcomes", "/admin/proposals"} else "200"
        if expected not in operation["responses"]:
            raise ValueError(f"documented success status missing: {method.upper()} {path} {expected}")
    expected_inputs = {
        "RequestInput": {"subject", "question", "decision_context", "urgency", "requested_output", "public_case_permission"},
        "ChallengeInput": {"state_id", "claim", "evidence_url", "notes"},
        "OutcomeInput": {"request_id", "state_id_used", "action", "reported_result", "authorization_for_public_use"},
        "ProposalInput": {"subject_id", "proposed_evidence_ids", "previous_state_id", "proposed_state", "proposed_change_event"},
    }
    schemas = spec["components"]["schemas"]
    for name, fields in expected_inputs.items():
        if set(schemas[name].get("required", [])) != fields or schemas[name].get("additionalProperties") is not False:
            raise ValueError(f"input allowlist mismatch: {name}")
    public = sum(1 for method, path in documented if method == "get" and not path.startswith("/requests/") and not path.startswith("/admin/"))
    protected = len(documented) - public
    return {"documented_operations": len(documented), "public_endpoints": public, "protected_endpoints": protected, "result": "PASS"}


def main() -> int:
    try:
        result = validate_contract()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print("RESULT FAIL")
        print(f"ERROR {exc}")
        return 1
    for key, value in result.items():
        print(f"{key.upper()} {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
