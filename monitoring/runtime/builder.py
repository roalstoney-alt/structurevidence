from __future__ import annotations

import json
from pathlib import Path

from .hash import canonical_hash, file_hash
from .validators import validate_snapshot, visible_at


ROOT = Path(__file__).resolve().parents[2]
BUILDER_VERSION = "MONITORING_BUILDER_v1.0"
SCHEMA_VERSION = "MONITORING_SNAPSHOT_v1.0"
SNAPSHOT_AS_OF = "2026-09-11T00:00:00Z"


def _read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def input_paths(subject: str) -> list[tuple[str, str]]:
    if subject.lower() != "bnb":
        raise ValueError("monitoring v1.0 supports BNB only")
    return [
        ("research/digital-assets/batch-01-r1/BNB/CANONICAL_RESEARCH_R1.json", "canonical_research"),
        ("research/digital-assets/batch-01-r1/BNB/OBSERVATION_REGISTRY.json", "observation_registry"),
        ("research/digital-assets/batch-01-r1/BNB/CLAIM_REGISTRY.json", "claim_registry"),
        ("research/digital-assets/batch-01-r1/BNB/SOURCE_INVENTORY.json", "source_inventory"),
        ("research/digital-assets/batch-01-r1/BNB/COUNTER_EVIDENCE_SEARCH_LOG.json", "counter_evidence"),
        ("timeline/subjects/bnb_structural_timeline.json", "structural_timeline"),
        ("timeline/subjects/bnb_structural_day.json", "structural_day"),
        ("timeline/subjects/bnb_event_ledger.json", "event_ledger"),
        ("timeline/subjects/bnb_evidence_events.json", "evidence_events"),
        ("research/freshness/bnb/FRESHNESS_EVALUATION_v0.1a.json", "freshness"),
        ("research/digital-assets/batch-01-r1/BNB/gdr-se/GDR_SE_AUTHORIZATION_RECORD_R1_1.json", "gdr_authorization"),
        ("evidence-freeze/DIGITAL-ASSET-BATCH-01-R1/BNB/MANIFEST.json", "rtp_manifest"),
    ]


def gdr_monitor_actions(authorization: str) -> dict[str, str]:
    if authorization in {"ALLOW_PUBLICATION", "ALLOW_WITH_LIMITATIONS"}:
        limit = "ALLOW_WITH_LIMITATIONS" if authorization == "ALLOW_WITH_LIMITATIONS" else "ALLOW"
        return {
            "DISPLAY_OBSERVATION": "ALLOW",
            "DISPLAY_STATE": limit,
            "PUBLISH_INTERPRETATION": limit,
            "EXPORT_SNAPSHOT": limit,
            "COMMERCIAL_DELIVERY": "BLOCK",
        }
    if authorization == "REFRESH_REQUIRED":
        return {key: "REFRESH_REQUIRED" for key in ["DISPLAY_OBSERVATION", "DISPLAY_STATE", "PUBLISH_INTERPRETATION", "EXPORT_SNAPSHOT", "COMMERCIAL_DELIVERY"]}
    return {key: "BLOCK" for key in ["DISPLAY_OBSERVATION", "DISPLAY_STATE", "PUBLISH_INTERPRETATION", "EXPORT_SNAPSHOT", "COMMERCIAL_DELIVERY"]}


def _latest_structural_states(day: dict, cutoff: str) -> tuple[list[dict], list[dict]]:
    by_dimension: dict[str, list[dict]] = {}
    for bucket in day["buckets"]:
        known = bucket.get("level_last_observed_at") or bucket.get("delta_last_established_at")
        if known and visible_at(known, cutoff):
            by_dimension.setdefault(bucket["dimension_id"], []).append(bucket)
    levels = []
    deltas = []
    for dimension, buckets in sorted(by_dimension.items()):
        observed = [row for row in buckets if row.get("level_state") not in {"NO_OBSERVATION", None}]
        if not observed:
            continue
        latest = sorted(observed, key=lambda row: row.get("level_last_observed_at") or "")[-1]
        levels.append({
            "dimension_id": dimension,
            "state": latest["level_state"],
            "effective_at": latest.get("level_last_observed_at"),
            "source_refs": latest.get("source_refs", []),
            "observation_ids": latest.get("level_observation_ids", []),
        })
        established = [row for row in buckets if row.get("delta_state") not in {"NOT_ESTABLISHED", "NO_OBSERVATION", None}]
        if established:
            delta = sorted(established, key=lambda row: row.get("delta_last_established_at") or "")[-1]
            deltas.append({
                "dimension_id": dimension,
                "state": delta["delta_state"],
                "basis": delta.get("delta_basis"),
                "effective_at": delta.get("delta_last_established_at"),
                "comparability_state": "EXPLICIT_CHANGE_EVENT" if delta.get("delta_basis") == "EXPLICIT_CHANGE_EVENT" else "COMPARABLE",
                "source_refs": delta.get("source_refs", []),
            })
        else:
            deltas.append({
                "dimension_id": dimension,
                "state": "NOT_ESTABLISHED",
                "basis": "NO_VALID_COMPARABLE_PRIOR",
                "effective_at": None,
                "comparability_state": "NOT_ESTABLISHED",
                "source_refs": latest.get("source_refs", []),
            })
    return levels, deltas


def _information_events(ledger: dict, cutoff: str) -> list[dict]:
    events = []
    for row in ledger["events"]:
        known_at = row.get("known_at") or row.get("timestamp")
        if not known_at or not visible_at(known_at, cutoff):
            continue
        refs = row.get("refs", [])
        hashes = [file_hash(ROOT / ref) for ref in refs if (ROOT / ref).is_file()]
        events.append({
            "event_id": row["event_id"],
            "subject_id": ledger["subject_id"],
            "event_type": row["event_type"],
            "event_domain": row["event_domain"],
            "effective_at": row.get("effective_at"),
            "known_at": known_at,
            "captured_at": known_at,
            "source_ids": [],
            "artifact_ids": refs,
            "artifact_sha256": hashes,
            "epistemic_status": "SUPPORTED",
            "epistemic_status_as_of": cutoff,
            "market_impact_status": "NOT_MEASURED",
            "impact_observation_window": None,
            "affected_dimensions": row.get("dimension_ids", [row.get("family_id")] if row.get("family_id") else []),
            "causal_status": "NOT_EVALUATED",
            "correction_status": "NONE",
            "supersedes_event_id": None,
            "notes": [row.get("label", ""), "Artifact integrity and content truth remain separate."]
        })
    return sorted(events, key=lambda event: (event["known_at"], event["event_id"]), reverse=True)


def build_view_model(subject: str = "bnb", snapshot_as_of: str = SNAPSHOT_AS_OF) -> dict:
    paths = input_paths(subject)
    inputs = [{"path": path, "role": role, "sha256": file_hash(ROOT / path)} for path, role in paths]
    source_bundle_hash = canonical_hash(inputs)
    canonical = _read(paths[0][0])
    claims = _read(paths[2][0])
    sources = _read(paths[3][0])
    structural = _read(paths[5][0])
    day = _read(paths[6][0])
    ledger = _read(paths[7][0])
    evidence_events = _read(paths[8][0])
    freshness = _read(paths[9][0])
    gdr = _read(paths[10][0])
    levels, deltas = _latest_structural_states(day, snapshot_as_of)
    events = _information_events(ledger, snapshot_as_of)
    snapshot = {
        "snapshot_id": "SE-MON-BNB-2026-09-11-v1",
        "subject_id": "BNB",
        "subject_label": "BNB",
        "subject_type": "DIGITAL_ASSET",
        "snapshot_as_of": snapshot_as_of,
        "known_at_cutoff": snapshot_as_of,
        "generated_at": snapshot_as_of,
        "source_bundle_hash": source_bundle_hash,
        "structural_level": {"overall_state": canonical["structural_state_final"], "dimensions": levels},
        "structural_delta": {"overall_state": "ESTABLISHED_IN_SELECTED_DIMENSIONS" if any(row["state"] != "NOT_ESTABLISHED" for row in deltas) else "DELTA_NOT_ESTABLISHED", "dimensions": deltas},
        "evidence_dynamics": {
            "overall_state": canonical["evidence_state_final"],
            "ecl_consistency": "CONSISTENT_WITH_LIMITATIONS" if canonical["material_inconsistency"] == "NO" else "INCONSISTENT",
            "source_coverage": canonical["source_coverage"],
            "claim_count": len(claims),
            "source_count": len(sources),
            "dependency_group_count": len({row["dependency_group"] for row in sources}),
            "events": [event for event in evidence_events["events"] if visible_at(event["known_at"], snapshot_as_of)],
        },
        "market_dynamics": {
            "state": "NOT_MEASURED",
            "reason": "No frozen market microstructure time series is available in the BNB input bundle.",
            "flow8": {key: "NOT_MEASURED" for key in ["magnitude", "velocity", "acceleration", "persistence", "depth", "breadth", "coupling", "entropy"]},
        },
        "liquidity_observations": [
            {"metric": metric, "state": "NOT_MEASURED", "observation_window": None, "source_refs": []}
            for metric in ["market_depth", "spread", "volume", "turnover", "liquidity_concentration", "venue_concentration", "volatility", "funding_leverage", "liquidation_activity", "cross_market_coupling"]
        ],
        "recent_events": events,
        "freshness_snapshot": {
            "policy_version": freshness["policy_version"],
            "release_state": freshness["release_result"]["release_freshness_state"],
            "next_refresh_reason": freshness["release_result"]["next_refresh_reason"],
            "input_bundle_hash": freshness["input_bundle_hash"],
        },
        "gdr_snapshot": {
            "authorization": gdr["authorization"],
            "authorization_id": gdr["authorization_id"],
            "evaluation_as_of": gdr["evaluation_as_of"],
            "limitations": gdr["limitations"],
            "actions": gdr_monitor_actions(gdr["authorization"]),
            "adapter_version": "GDR_MONITOR_ACTION_ADAPTER_v1.0",
        },
        "rtp_provenance_refs": inputs,
        "supported_resolutions": structural["supported_resolutions"],
        "prior_snapshot_id": None,
        "monitoring_boundary": "Observed structural and evidence state only. Market and liquidity dynamics are NOT_MEASURED in this snapshot.",
        "builder_version": BUILDER_VERSION,
        "schema_version": SCHEMA_VERSION,
        "snapshot_sha256": "",
    }
    hashable = dict(snapshot)
    hashable["snapshot_sha256"] = None
    snapshot["snapshot_sha256"] = canonical_hash(hashable)
    validate_snapshot(snapshot)
    return snapshot


def build_monitoring_artifacts(subject: str = "bnb", snapshot_as_of: str = SNAPSHOT_AS_OF) -> dict[str, Path]:
    snapshot = build_view_model(subject, snapshot_as_of)
    out = ROOT / "monitoring" / "subjects" / subject.lower()
    snapshot_path = out / "MONITORING_SNAPSHOT.json"
    events_path = out / "INFORMATION_EVENT_LEDGER.json"
    transitions_path = out / "STATE_TRANSITION_INDEX.json"
    provenance_path = out / "PROVENANCE_INDEX.json"
    public_index_path = ROOT / "monitoring" / "PUBLIC_MONITORING_INDEX.json"
    _write(snapshot_path, snapshot)
    _write(events_path, {"ledger_id": "SE-MON-BNB-EVENTS-v1", "subject_id": "BNB", "events": snapshot["recent_events"]})
    transitions = []
    for row in snapshot["structural_delta"]["dimensions"]:
        transitions.append({
            "transition_id": f"SE-MON-BNB-{row['dimension_id']}-v1",
            "subject_id": "BNB",
            "dimension_id": row["dimension_id"],
            "prior_state": None,
            "current_state": row["state"],
            "effective_at": row["effective_at"],
            "known_at": snapshot_as_of,
            "basis": row["basis"],
            "comparability_state": row["comparability_state"],
            "source_refs": row["source_refs"],
        })
    _write(transitions_path, {"index_id": "SE-MON-BNB-TRANSITIONS-v1", "subject_id": "BNB", "supported_resolutions": snapshot["supported_resolutions"], "transitions": transitions})
    _write(provenance_path, {"index_id": "SE-MON-BNB-PROVENANCE-v1", "subject_id": "BNB", "integrity_boundary": "Hash match proves artifact identity, not content truth.", "artifacts": snapshot["rtp_provenance_refs"]})
    _write(public_index_path, {
        "index_id": "SE-PUBLIC-MONITORING-INDEX-v1",
        "integrity_boundary": "Hash verification establishes artifact identity, not content truth.",
        "records": [{
            "snapshot_id": snapshot["snapshot_id"],
            "subject_id": snapshot["subject_id"],
            "snapshot_as_of": snapshot["snapshot_as_of"],
            "snapshot_sha256": snapshot["snapshot_sha256"],
            "source_bundle_hash": snapshot["source_bundle_hash"],
            "artifact_path": str(snapshot_path.relative_to(ROOT)),
            "workspace_path": "monitor.html?subject=bnb",
        }],
    })
    outputs = [snapshot_path, events_path, transitions_path, provenance_path, public_index_path]
    manifest = {
        "manifest_id": "SE-MON-BNB-BUILD-v1",
        "builder_version": BUILDER_VERSION,
        "subject_id": "BNB",
        "snapshot_id": snapshot["snapshot_id"],
        "generated_at": snapshot_as_of,
        "inputs": snapshot["rtp_provenance_refs"],
        "outputs": [{"path": str(path.relative_to(ROOT)), "sha256": file_hash(path)} for path in outputs],
        "source_bundle_hash": snapshot["source_bundle_hash"],
    }
    manifest_path = out / "MONITORING_BUILD_MANIFEST.json"
    _write(manifest_path, manifest)
    return {"snapshot": snapshot_path, "events": events_path, "transitions": transitions_path, "provenance": provenance_path, "public_index": public_index_path, "manifest": manifest_path}
