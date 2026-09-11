from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


STATUSES = {"PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"}
GATES = [
    "RDLF01_POLICY_SCHEMA", "RDLF02_SUBJECT_CLASS_PROFILES", "RDLF03_LEVEL_FRESHNESS_RULES", "RDLF04_DELTA_FRESHNESS_RULES", "RDLF05_EVIDENCE_FAMILY_RULES", "RDLF06_NO_GLOBAL_THRESHOLD", "RDLF07_TIME_RULE_TYPES", "RDLF08_EVENT_INVALIDATION_RULES", "RDLF09_CORRECTION_OVERRIDE", "RDLF10_SUPERSESSION_OVERRIDE", "RDLF11_POLICY_PRECEDENCE", "RDLF12_CONFIG_DRIVEN_RUNTIME", "RDLF13_CADENCE_METRICS", "RDLF14_THRESHOLD_EVIDENCE_BASIS", "RDLF15_SENSITIVITY_ANALYSIS", "RDLF16_SPARSE_DATA_FAILSAFE", "RDLF17_POLICY_NOT_CONFIGURED_FAILSAFE", "RDLF18_LEVEL_DELTA_SEPARATION", "RDLF19_NO_LOOKAHEAD", "RDLF20_RUNTIME_CLOCK", "RDLF21_AS_OF_REPRODUCTION", "RDLF22_EVENT_VERIFICATION", "RDLF23_RELEASE_AGGREGATION", "RDLF24_PAID_CONTEXT_RULES", "RDLF25_GDR_G3_INTEGRATION", "RDLF26_TIMELINE_OVERLAY", "RDLF27_STRATEGY_PILOT", "RDLF28_BNB_PILOT", "RDLF29_SOL_PILOT", "RDLF30_TRX_PILOT", "RDLF31_XLM_PILOT", "RDLF32_EVIDENCE_FAMILY_PILOT", "RDLF33_UNCONFIGURED_REGISTRY", "RDLF34_POLICY_MANIFEST", "RDLF35_GATE_REGISTRY", "RDLF36_NO_DEFAULT_PASS", "RDLF37_RESEARCH_HASHES_UNCHANGED", "RDLF38_GDR_SEMANTICS_UNCHANGED", "RDLF39_TIMELINE_SEMANTICS_UNCHANGED", "RDLF40_ENGLISH_PUBLIC_SURFACE", "RDLF41_HREF_INTEGRITY", "RDLF42_ROOT_DOCS_SYNC", "RDLF43_TESTS", "RDLF44_GIT_PUSH", "RDLF45_REMOTE_MATCH",
]


@dataclass
class GateResult:
    gate_id: str
    status: str
    validator: str
    evidence_refs: list[str]
    computed_facts: dict = field(default_factory=dict)
    reason: str = ""
    rule_version: str = "RDL_FRESHNESS_VALIDATION_v0.1"
    evaluated_at: str = ""

    def to_dict(self) -> dict:
        return {"gate_id": self.gate_id, "status": self.status if self.status in STATUSES else "NOT_EVALUATED", "validator": self.validator, "rule_version": self.rule_version, "evaluated_at": self.evaluated_at, "evidence_refs": self.evidence_refs, "computed_facts": self.computed_facts, "reason": self.reason}


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validation_rules_sha256() -> str:
    return hashlib.sha256(json.dumps({"gates": GATES, "statuses": sorted(STATUSES)}, sort_keys=True).encode()).hexdigest()


def normalize(results: list[GateResult | dict]) -> list[dict]:
    now = stamp()
    by_gate = {}
    for item in results:
        row = item if isinstance(item, GateResult) else GateResult(**item)
        row.evaluated_at = row.evaluated_at or now
        by_gate[row.gate_id] = row.to_dict()
    for gate_id in GATES:
        by_gate.setdefault(gate_id, GateResult(gate_id, "NOT_EVALUATED", "missing_validator", [], {}, "No validator result returned.", evaluated_at=now).to_dict())
    return [by_gate[gate] for gate in GATES]


def summarize(rows: list[dict]) -> dict:
    counts = {status: 0 for status in STATUSES}
    for row in rows:
        counts[row["status"]] += 1
    if counts["FAIL"]:
        acceptance = "FAIL"
    elif counts["BLOCKED"] or counts["NOT_EVALUATED"] or counts["PARTIAL"]:
        acceptance = "METHOD_PILOT_PARTIAL"
    else:
        acceptance = "METHOD_PILOT_PASS"
    counts["acceptance"] = acceptance
    return counts


def write_registry(path: Path, results: list[GateResult | dict], metadata: dict) -> dict:
    rows = normalize(results)
    registry = {"registry_id": "RDL_FRESHNESS_GATE_RESULTS", "policy_version": "RDL_FRESHNESS_v0.1", "validation_rules_sha256": validation_rules_sha256(), "metadata": metadata, "summary": summarize(rows), "results": rows}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return registry
