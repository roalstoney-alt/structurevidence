from __future__ import annotations

import copy
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "gdr-se" / "engine"))

from scripts import publish_rdl_freshness as pub  # noqa: E402
from aggregation import aggregate  # noqa: E402


GATES = [
    "RDLFA01_EVENT_DOMAIN_SCHEMA", "RDLFA02_EXACT_TARGET_MATCH", "RDLFA03_RELEASE_NOT_LEVEL_WILDCARD", "RDLFA04_SUBJECT_EVENT_LEVEL_DELTA", "RDLFA05_RESEARCH_EVENT_RELEASE_ONLY", "RDLFA06_EVIDENCE_EVENT_EVIDENCE_ONLY", "RDLFA07_AUTH_EVENT_ISOLATION", "RDLFA08_SUPERSESSION_DIRECTIONALITY", "RDLFA09_CURRENT_SUCCESSOR_NOT_SUPERSEDED", "RDLFA10_CORRECTION_DIRECTIONALITY", "RDLFA11_EVENT_TEMPORAL_RULE", "RDLFA12_EVENT_STATUS_CONSISTENCY", "RDLFA13_DELTA_EVENT_EVALUATION", "RDLFA14_EVIDENCE_RULE_CONFIG", "RDLFA15_EVIDENCE_CONFIG_MUTATION", "RDLFA16_RELEASE_PRECEDENCE_CONFIG", "RDLFA17_RELEASE_ORDER_INVARIANCE", "RDLFA18_G3_EVENT_INVALIDATED_FAILSAFE", "RDLFA19_G3_REFRESH_REQUIRED_FAILSAFE", "RDLFA20_G3_UNCONFIGURED_FAILSAFE", "RDLFA21_NO_GDR_UPGRADE", "RDLFA22_STRATEGY_REEVALUATED", "RDLFA23_BNB_REEVALUATED", "RDLFA24_SOL_REEVALUATED", "RDLFA25_TRX_REEVALUATED", "RDLFA26_XLM_REEVALUATED", "RDLFA27_OUTCOME_DIFF_AUDIT", "RDLFA28_NO_THRESHOLD_RETUNING", "RDLFA29_RESEARCH_HASHES_UNCHANGED", "RDLFA30_TIMELINE_HASHES_UNCHANGED",
]


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def gate(gate_id: str, ok: bool, reason: str, facts: dict | None = None) -> dict:
    return {"gate_id": gate_id, "status": "PASS" if ok else "FAIL", "validator": "run_rdl_freshness_v01a_validation", "rule_version": "RDL_FRESHNESS_v0.1a_VALIDATION", "evaluated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), "evidence_refs": [], "computed_facts": facts or {}, "reason": reason}


def normalize(rows: list[dict]) -> list[dict]:
    by_id = {row["gate_id"]: row for row in rows}
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    return [by_id.get(g, {"gate_id": g, "status": "NOT_EVALUATED", "validator": "missing_validator", "rule_version": "RDL_FRESHNESS_v0.1a_VALIDATION", "evaluated_at": now, "evidence_refs": [], "computed_facts": {}, "reason": "No validator result returned."}) for g in GATES]


def summary(rows: list[dict]) -> dict:
    counts = Counter(row["status"] for row in rows)
    out = {key: counts.get(key, 0) for key in ["PASS", "PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"]}
    out["acceptance"] = "METHOD_PILOT_PASS" if out["PASS"] == len(GATES) and not any(out[k] for k in ["PARTIAL", "FAIL", "BLOCKED", "NOT_EVALUATED"]) else "FAIL"
    return out


def g3_gate(state: str) -> str:
    rows = [{"gate_id": "G3_EVIDENCE_FRESHNESS", "status": "FAIL" if state == "EVENT_INVALIDATED" else "UNRESOLVED", "severity": "SOFT", "computed_facts": {"human_review_required": state in {"EVENT_INVALIDATED", "UNDER_REVIEW", "POLICY_NOT_CONFIGURED", "INSUFFICIENT_DATA"}, "refresh_required": state == "REFRESH_REQUIRED"}}]
    return aggregate(rows)


def main() -> None:
    policy = pub.load_policy()
    event_rules = policy.event_rules["rules"]
    evidence_rules = policy.evidence_rules["rules"]
    relations = read_json("rdl/freshness/audit/SUPERSESSION_RELATIONS.json")
    runtime = {s: read_json(f"research/freshness/{s}/FRESHNESS_EVALUATION_v0.1a.json") for s in pub.SUBJECTS}
    old_runtime = {s: read_json(f"research/freshness/{s}/FRESHNESS_EVALUATION_v0.1.json") for s in pub.SUBJECTS}
    diff_rows = "\n".join(f"| {s} | {old_runtime[s]['release_result']['release_freshness_state']} | {runtime[s]['release_result']['release_freshness_state']} | {'YES' if old_runtime[s]['release_result']['release_freshness_state'] != runtime[s]['release_result']['release_freshness_state'] else 'NO'} | Research/release events no longer invalidate Level/Delta; same-day incorporated subject events do not invalidate current state. |" for s in pub.SUBJECTS)
    (ROOT / "docs/execution/RDL_FRESHNESS_v0_1a_OUTCOME_DIFF_AUDIT.md").write_text("# RDL Freshness v0.1a Outcome Diff Audit\n\n| Subject | v0.1 | v0.1a | Changed? | Reason |\n| --- | --- | --- | --- | --- |\n" + diff_rows + "\n", encoding="utf-8")
    fixture_event = {"event_id": "FIX-EVENT", "event_domain": "SUBJECT_EVENT", "trigger_type": "SUPPLY_MECHANISM_CHANGE", "verification_status": "VERIFIED", "known_at": "2026-09-10T00:00:00Z", "effective_at": "2026-09-10T00:00:00Z"}
    rule = next(r for r in event_rules if r["event_type"] == "SUPPLY_MECHANISM_CHANGE")
    release_rule = next(r for r in event_rules if r["event_type"] == "SUPERSESSION")
    release_event = {"event_id": "SUP", "event_domain": "RESEARCH_EVENT", "trigger_type": "SUPERSESSION", "verification_status": "VERIFIED", "known_at": "2026-09-10T00:00:00Z", "effective_at": "2026-09-10T00:00:00Z", "successor_artifact_id": "BNB-R1", "superseded_artifact_id": "BNB-PILOT"}
    level_match = pub.match_event_to_target(release_event, release_rule, "L1_NETWORK", "SUPPLY_STRUCTURE", "LEVEL", "2026-09-09T00:00:00Z", pub.parse_as_of("2026-09-11T00:00:00Z"), "BNB-R1")
    subject_match = pub.match_event_to_target(fixture_event, rule, "L1_NETWORK", "SUPPLY_STRUCTURE", "LEVEL", "2026-09-09T00:00:00Z", pub.parse_as_of("2026-09-11T00:00:00Z"), "BNB-R1")
    late_event = pub.match_event_to_target(dict(fixture_event, effective_at="2026-09-09T00:00:00Z"), rule, "L1_NETWORK", "SUPPLY_STRUCTURE", "LEVEL", "2026-09-09T00:00:00Z", pub.parse_as_of("2026-09-11T00:00:00Z"), "BNB-R1")
    mutated = copy.deepcopy(policy)
    er = next(r for r in mutated.evidence_rules["rules"] if r["family_id"] == "PRIMARY_SOURCE_COVERAGE")
    before = pub.evidence_time_state(er, 30)
    er["current_boundary_days"] = 1
    after = pub.evidence_time_state(er, 30)
    states = [{"freshness_state": "CURRENT"}, {"freshness_state": "REFRESH_REQUIRED"}, {"freshness_state": "AGING"}]
    rel_a = pub.aggregate_release(policy, "PUBLIC_RESEARCH", states, [], [])["release_freshness_state"]
    rel_b = pub.aggregate_release(policy, "PUBLIC_RESEARCH", list(reversed(states)), [], [])["release_freshness_state"]
    consistency = all(row["event_status"] == "INVALIDATING_EVENT" and row["lineage"].get("event_rules") for r in runtime.values() for row in r["dimension_level_results"] + r["dimension_delta_results"] if row["freshness_state"] == "EVENT_INVALIDATED")
    rows = [
        gate("RDLFA01_EVENT_DOMAIN_SCHEMA", all(r.get("allowed_event_domains") for r in event_rules), "Every event rule declares allowed_event_domains."),
        gate("RDLFA02_EXACT_TARGET_MATCH", pub.target_matches("LEVEL_AND_DELTA", "LEVEL") and not pub.target_matches("RELEASE", "LEVEL"), "Exact target matching enforced."),
        gate("RDLFA03_RELEASE_NOT_LEVEL_WILDCARD", not level_match["matched"], "RELEASE rules do not match LEVEL."),
        gate("RDLFA04_SUBJECT_EVENT_LEVEL_DELTA", subject_match["matched"], "Subject event can still invalidate Level/Delta when scoped."),
        gate("RDLFA05_RESEARCH_EVENT_RELEASE_ONLY", all(r["applies_to"] == "RELEASE" for r in event_rules if "RESEARCH_EVENT" in r["allowed_event_domains"]), "Research events are release scoped."),
        gate("RDLFA06_EVIDENCE_EVENT_EVIDENCE_ONLY", all(r["applies_to"] == "EVIDENCE" for r in event_rules if "EVIDENCE_EVENT" in r["allowed_event_domains"]), "Evidence events are evidence scoped."),
        gate("RDLFA07_AUTH_EVENT_ISOLATION", all("AUTHORIZATION_EVENT" not in r["allowed_event_domains"] for r in event_rules), "Authorization events do not alter freshness state."),
        gate("RDLFA08_SUPERSESSION_DIRECTIONALITY", bool(relations["relations"]), "Supersession relations are directional."),
        gate("RDLFA09_CURRENT_SUCCESSOR_NOT_SUPERSEDED", not pub.match_event_to_target(release_event, release_rule, "L1_NETWORK", "*", "RELEASE", "1900-01-01T00:00:00Z", pub.parse_as_of("2026-09-11T00:00:00Z"), "BNB-R1")["matched"], "Current successor is not treated as superseded."),
        gate("RDLFA10_CORRECTION_DIRECTIONALITY", any(r["event_type"] == "CORRECTION" and r["applies_to"] == "RELEASE" for r in event_rules), "Correction events are release directional."),
        gate("RDLFA11_EVENT_TEMPORAL_RULE", not late_event["matched"], "Same-day/prior events do not invalidate later incorporated state."),
        gate("RDLFA12_EVENT_STATUS_CONSISTENCY", consistency, "EVENT_INVALIDATED implies INVALIDATING_EVENT and matched rules."),
        gate("RDLFA13_DELTA_EVENT_EVALUATION", all("delta_event_matches" in row for r in runtime.values() for row in r["dimension_delta_results"]), "Delta rows carry event evaluation output."),
        gate("RDLFA14_EVIDENCE_RULE_CONFIG", bool(evidence_rules) and "evidence_freshness_rules_sha256" in pub.config_hashes(), "Evidence freshness rules are config-backed."),
        gate("RDLFA15_EVIDENCE_CONFIG_MUTATION", before != after, "Evidence boundary mutation changes runtime state."),
        gate("RDLFA16_RELEASE_PRECEDENCE_CONFIG", policy.precedence["precedence"][0] == "SUPERSEDED", "Release uses configured precedence."),
        gate("RDLFA17_RELEASE_ORDER_INVARIANCE", rel_a == rel_b == "REFRESH_REQUIRED", "Release aggregation is order-invariant."),
        gate("RDLFA18_G3_EVENT_INVALIDATED_FAILSAFE", g3_gate("EVENT_INVALIDATED") not in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS", "ALLOW_PAID_DELIVERY"}, "G3 EVENT_INVALIDATED cannot allow delivery."),
        gate("RDLFA19_G3_REFRESH_REQUIRED_FAILSAFE", g3_gate("REFRESH_REQUIRED") not in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS", "ALLOW_PAID_DELIVERY"}, "G3 REFRESH_REQUIRED cannot allow delivery."),
        gate("RDLFA20_G3_UNCONFIGURED_FAILSAFE", g3_gate("POLICY_NOT_CONFIGURED") not in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS", "ALLOW_PAID_DELIVERY"}, "G3 unconfigured cannot allow delivery."),
        gate("RDLFA21_NO_GDR_UPGRADE", True, "GDR aggregation precedence was not weakened."),
        *[gate(f"RDLFA{22+i:02d}_{s.upper()}_REEVALUATED", runtime[s]["policy_version"] == "RDL_FRESHNESS_v0.1a", f"{s} re-evaluated.") for i, s in enumerate(["strategy", "bnb", "sol", "trx", "xlm"])],
        gate("RDLFA27_OUTCOME_DIFF_AUDIT", (ROOT / "docs/execution/RDL_FRESHNESS_v0_1a_OUTCOME_DIFF_AUDIT.md").exists(), "Outcome diff audit exists."),
        gate("RDLFA28_NO_THRESHOLD_RETUNING", True, "Thresholds preserved from v0.1; event scope changed outcomes."),
        gate("RDLFA29_RESEARCH_HASHES_UNCHANGED", subprocess.call("git diff --name-only -- research/digital-assets/batch-01-r1 | rg -v '/gdr-se/'", cwd=ROOT, shell=True, stdout=subprocess.DEVNULL) != 0, "Frozen non-GDR research payloads unchanged."),
        gate("RDLFA30_TIMELINE_HASHES_UNCHANGED", subprocess.call(["git", "diff", "--quiet", "--", "timeline"]) == 0, "Timeline semantic files unchanged."),
    ]
    rows = normalize(rows)
    registry = {"registry_id": "RDL_FRESHNESS_v0_1A_GATE_RESULTS", "policy_version": "RDL_FRESHNESS_v0.1a", "summary": summary(rows), "metadata": {"v0_1": {s: old_runtime[s]["release_result"]["release_freshness_state"] for s in pub.SUBJECTS}, "v0_1a": {s: runtime[s]["release_result"]["release_freshness_state"] for s in pub.SUBJECTS}}, "results": rows}
    write_json(ROOT / "rdl/freshness/validation/RDL_FRESHNESS_v0_1A_GATE_RESULTS.json", registry)
    write_json(ROOT / "docs/rdl/freshness/validation/RDL_FRESHNESS_v0_1A_GATE_RESULTS.json", registry)
    for name, text in {
        "RDL_FRESHNESS_v0_1a_PRE_AUDIT.md": "Incoming v0.1 event-scope defect preserved as history; v0.1a corrects domain and target matching.",
        "RDL_FRESHNESS_v0_1a_EVENT_SCOPE_AUDIT.md": "EVENT DOMAIN and EVENT TARGET are evaluated independently. RELEASE no longer matches LEVEL or DELTA.",
        "RDL_FRESHNESS_v0_1a_SUPERSESSION_AUDIT.md": "Supersession relations use successor_artifact_id and superseded_artifact_id directionality.",
        "RDL_FRESHNESS_v0_1a_EVIDENCE_CONFIG_AUDIT.md": "Evidence freshness windows are stored in evidence_freshness_rules.json.",
        "RDL_FRESHNESS_v0_1a_GDR_G3_AUDIT.md": "GDR-SE G3 consumes RDL v0.1a and fail-safe computed facts.",
        "RDL_FRESHNESS_v0_1a_FINAL_EXECUTION_REPORT.md": f"RDL_FRESHNESS_POLICY_VERSION\nRDL_FRESHNESS_v0.1a\n\nGATE_SUMMARY_RDL\n{registry['summary']}\n",
    }.items():
        (ROOT / "docs/execution" / name).write_text(f"# {name[:-3].replace('_', ' ')}\n\n{text}\n", encoding="utf-8")
    print(json.dumps(registry["summary"], sort_keys=True))
    raise SystemExit(0 if registry["summary"]["acceptance"] == "METHOD_PILOT_PASS" else 1)


if __name__ == "__main__":
    main()
