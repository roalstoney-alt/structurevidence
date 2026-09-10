from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


STATUSES = {"PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_APPLICABLE", "NOT_EVALUATED"}
REQUIRED_GATES = [
    "TL11A_01_PRIOR_COMPARISON_RUNTIME",
    "TL11A_02_APPEND_SIMULATION",
    "TL11A_03_COMPARISON_LINEAGE",
    "TL11A_04_NONCOMPARABLE_PRIOR_BLOCK",
    "TL11A_05_EXPLICIT_CHANGE_PRECEDENCE",
    "TL11A_06_REAL_UTC_AS_OF",
    "TL11A_07_EXPLICIT_AS_OF_REPRODUCTION",
    "TL11A_08_NAIVE_TIMESTAMP_REJECT",
    "TL11A_09_AGE_PROGRESSION",
    "TL11A_10_NO_ACTIVE_FIXED_AS_OF",
    "TL11A_11_GATE_REGISTRY",
    "TL11A_12_NO_DEFAULT_PASS",
    "TL11A_13_REPORT_FROM_GATE_RESULTS",
    "TL11A_14_GATE_EVIDENCE_REFS",
    "TL11A_15_BASE_COMMIT_LINEAGE",
    "TL11A_16_EXISTING_LEVEL_DELTA_REGRESSION",
    "TL11A_17_EXISTING_EVIDENCE_DYNAMICS_REGRESSION",
    "TL11A_18_GDR_SE_UNCHANGED",
    "TL11A_19_RDL_FRESHNESS_UNCONFIGURED",
    "TL11A_20_RESEARCH_HASHES_UNCHANGED",
    "TL11A_21_ENGLISH_PUBLIC_SURFACE",
    "TL11A_22_ROOT_DOCS_SYNC",
    "TL11A_23_HREF_INTEGRITY",
    "TL11A_24_TESTS",
    "TL11A_25_GIT_PUSH",
    "TL11A_26_REMOTE_MATCH",
]


@dataclass
class GateResult:
    gate_id: str
    status: str
    validator: str
    rule_version: str
    evidence_refs: list[str]
    computed_facts: dict = field(default_factory=dict)
    reason: str = ""
    evaluated_at: str = ""

    def to_dict(self) -> dict:
        status = self.status if self.status in STATUSES else "NOT_EVALUATED"
        return {
            "gate_id": self.gate_id,
            "status": status,
            "validator": self.validator,
            "rule_version": self.rule_version,
            "evaluated_at": self.evaluated_at,
            "evidence_refs": self.evidence_refs,
            "computed_facts": self.computed_facts,
            "reason": self.reason,
        }


def utc_stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validation_rules_sha256() -> str:
    payload = {"required_gates": REQUIRED_GATES, "statuses": sorted(STATUSES), "version": "TIMELINE_R1_1A_VALIDATION_v0.1"}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def normalize_results(results: list[GateResult | dict], evaluated_at: str | None = None) -> list[dict]:
    by_gate = {}
    stamp = evaluated_at or utc_stamp()
    for item in results:
        result = item if isinstance(item, GateResult) else GateResult(**item)
        result.evaluated_at = result.evaluated_at or stamp
        by_gate[result.gate_id] = result.to_dict()
    for gate_id in REQUIRED_GATES:
        by_gate.setdefault(gate_id, GateResult(gate_id, "NOT_EVALUATED", "missing_validator", "TIMELINE_R1_1A_VALIDATION_v0.1", [], {}, "No validator result was returned.", stamp).to_dict())
    return [by_gate[gate_id] for gate_id in REQUIRED_GATES]


def summary(results: list[dict]) -> dict:
    out = {status: 0 for status in STATUSES}
    for result in results:
        out[result["status"]] += 1
    required_statuses = {result["status"] for result in results if result["gate_id"] in REQUIRED_GATES}
    if "FAIL" in required_statuses:
        acceptance = "RUNTIME_CLOSURE_FAIL"
    elif required_statuses & {"BLOCKED", "NOT_EVALUATED", "PARTIAL"}:
        acceptance = "RUNTIME_CLOSURE_PARTIAL"
    else:
        acceptance = "RUNTIME_CLOSURE_PASS"
    out["acceptance"] = acceptance
    return out


def write_registry(path: Path, results: list[GateResult | dict], metadata: dict | None = None) -> dict:
    normalized = normalize_results(results)
    registry = {
        "registry_id": "TIMELINE_R1_1A_GATE_RESULTS",
        "rule_version": "TIMELINE_R1_1A_VALIDATION_v0.1",
        "validation_rules_sha256": validation_rules_sha256(),
        "metadata": metadata or {},
        "summary": summary(normalized),
        "results": normalized,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return registry
