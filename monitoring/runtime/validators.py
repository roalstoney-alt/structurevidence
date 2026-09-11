from __future__ import annotations

from datetime import datetime


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def visible_at(known_at: str, cutoff: str) -> bool:
    return parse_utc(known_at) <= parse_utc(cutoff)


def validate_dual_axis(event: dict) -> None:
    if "epistemic_status" not in event or "market_impact_status" not in event:
        raise ValueError("information event must keep epistemic and market-impact status separate")
    if event["causal_status"] == "CAUSAL_SUPPORT_ESTABLISHED" and not event.get("causal_evidence_refs"):
        raise ValueError("causal support requires explicit evidence refs")


def validate_snapshot(snapshot: dict) -> None:
    required = {
        "snapshot_id", "subject_id", "snapshot_as_of", "known_at_cutoff", "generated_at",
        "source_bundle_hash", "structural_level", "structural_delta", "evidence_dynamics",
        "market_dynamics", "liquidity_observations", "recent_events", "freshness_snapshot",
        "gdr_snapshot", "rtp_provenance_refs", "prior_snapshot_id", "snapshot_sha256",
        "builder_version", "schema_version",
    }
    missing = sorted(required - snapshot.keys())
    if missing:
        raise ValueError(f"missing snapshot fields: {missing}")
    for event in snapshot["recent_events"]:
        validate_dual_axis(event)


def validate_append_only_events(events: list[dict]) -> None:
    seen: dict[str, dict] = {}
    for event in sorted(events, key=lambda row: (parse_utc(row["known_at"]), row["event_id"])):
        event_id = event["event_id"]
        if event_id in seen:
            raise ValueError(f"duplicate event_id: {event_id}")
        target_id = event.get("supersedes_event_id")
        if target_id:
            if target_id not in seen:
                raise ValueError("supersession must point to an earlier preserved event")
            if parse_utc(event["known_at"]) <= parse_utc(seen[target_id]["known_at"]):
                raise ValueError("supersession must move forward in known time")
        seen[event_id] = event


def establish_delta(prior_state: str | None, current_state: str, *, comparable: bool,
                    explicit_change_event: bool = False) -> str:
    if explicit_change_event and prior_state is not None:
        return "ESTABLISHED"
    if prior_state is None or not comparable:
        return "NOT_ESTABLISHED"
    return "UNCHANGED" if prior_state == current_state else "ESTABLISHED"
