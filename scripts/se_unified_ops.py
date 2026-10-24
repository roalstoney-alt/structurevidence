#!/usr/bin/env python3
"""StructEvidence single-schedule orchestrator and X publishing adapter.

The module deliberately separates configured, attempted, delivered and verified.
It has no scheduler of its own: an existing approved scheduler invokes this file.
"""
from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any, Iterable
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
SGT = ZoneInfo("Asia/Singapore")
UTC = dt.timezone.utc
ALLOWED_STATES = {"PASS", "PARTIAL", "BLOCKED", "MISSED", "NOT_DUE", "HOLD", "UNVERIFIED"}
REVIEW_RESULTS = {"NO_STATE_CHANGE", "REVIEW_INCOMPLETE", "HUMAN_GATE_REQUIRED"}
EVENT_CLASSIFICATIONS = {"NEW_EVENT", "NEWLY_DISCOVERED_OLD_EVIDENCE"}
DAILY_EVIDENCE_COUNTS = (
    "new_sources", "new_attributed_statements", "new_independent_evidence",
    "new_events", "newly_discovered_old_evidence", "state_changing_evidence",
)
EVENTS = {
    "SCHEDULED", "STARTED", "SEARCH_COMPLETED", "ARTIFACT_CREATED",
    "WRITE_ATTEMPTED", "DELIVERED", "VERIFIED",
}
X_URL_RE = re.compile(r"https?://[^\s]+", re.I)
SENSITIVE_PUBLIC_TERMS = {
    "internal contract amount", "private supplier accusation", "family movement",
    "clinical personal record", "pathogen handling instruction",
}


class OpsError(RuntimeError):
    code = "OPS_ERROR"


class LockHeld(OpsError):
    code = "RUN_LOCK_HELD"


class AppendOnlyConflict(OpsError):
    code = "APPEND_ONLY_CONFLICT"


class GateBlocked(OpsError):
    code = "PUBLIC_TRUST_GATE_FAILED"


def iso_now() -> str:
    return dt.datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def artifact_ref(path: Path, root: Path, state_root: Path) -> str:
    if path.is_relative_to(root):
        return str(path.relative_to(root))
    if path.is_relative_to(state_root):
        return "STATE_ROOT/" + str(path.relative_to(state_root))
    return path.name


def atomic_json(path: Path, value: Any, *, replace: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not replace and path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        if canonical_json(existing) != canonical_json(value):
            raise AppendOnlyConflict(f"refusing to replace append-only artifact: {path}")
        return
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(temporary)


def append_jsonl_once(path: Path, value: dict[str, Any], key: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        handle.seek(0)
        for line in handle:
            if line.strip() and json.loads(line).get(key) == value.get(key):
                return False
        handle.seek(0, os.SEEK_END)
        handle.write(canonical_json(value) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
        return True


@dataclasses.dataclass
class Lease:
    path: Path
    run_id: str
    ttl_seconds: int = 7200

    def acquire(self, now: dt.datetime | None = None) -> None:
        now = now or dt.datetime.now(UTC)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            current = json.loads(self.path.read_text(encoding="utf-8"))
            expires = dt.datetime.fromisoformat(current["expires_at"].replace("Z", "+00:00"))
            if expires > now and current.get("run_id") != self.run_id:
                raise LockHeld(f"active run lease: {current.get('run_id')}")
        payload = {
            "run_id": self.run_id,
            "acquired_at": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "expires_at": (now + dt.timedelta(seconds=self.ttl_seconds)).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
        atomic_json(self.path, payload)

    def release(self) -> None:
        if not self.path.exists():
            return
        current = json.loads(self.path.read_text(encoding="utf-8"))
        if current.get("run_id") == self.run_id:
            self.path.unlink()


def stable_run_id(date_sgt: str, scheduled_at: str) -> str:
    key = f"StructEvidence|{date_sgt}|SE-UNIFIED-SCHEDULE-X-v1.0|{scheduled_at}"
    return f"SE-OPS-{date_sgt.replace('-', '')}-2200-{uuid.uuid5(uuid.NAMESPACE_URL, key)}"


def x_weighted_length(text: str) -> int:
    """Conservative X length check: every URL consumes the current t.co 23-char slot."""
    without_urls = X_URL_RE.sub("", text)
    return len(without_urls) + (23 * len(X_URL_RE.findall(text)))


def canonical_post_text(text: str) -> str:
    return " ".join(text.split()).strip()


def validate_candidate(candidate: dict[str, Any]) -> None:
    text = canonical_post_text(candidate.get("text", ""))
    if not text or x_weighted_length(text) > 280:
        raise GateBlocked("candidate is empty or exceeds X weighted length")
    if candidate.get("approval_gate") not in {"HUMAN_GATE_REQUIRED", "BLOCKED"}:
        raise GateBlocked("invalid approval gate")
    lower = canonical_json(candidate).lower()
    if any(term in lower for term in SENSITIVE_PUBLIC_TERMS):
        raise GateBlocked("sensitive/private material detected in public payload")
    if candidate.get("material_state_transition") and candidate.get("approval_gate") != "HUMAN_GATE_REQUIRED":
        raise GateBlocked("material state transitions require human review")
    urls = X_URL_RE.findall(text)
    if sorted(urls) != sorted(candidate.get("source_urls", [])):
        raise GateBlocked("candidate source URLs do not match final text URLs")


def validate_review(review: dict[str, Any]) -> None:
    required = {
        "case_id", "review_id", "reviewed_at", "result", "review_complete",
        "search_boundary", "sources_checked", "old_state", "new_state",
        "new_qualifying_evidence_count", "new_counter_evidence_count",
    }
    missing = sorted(required - set(review))
    if missing:
        raise GateBlocked(f"review missing required fields: {', '.join(missing)}")
    if review["result"] not in REVIEW_RESULTS:
        raise GateBlocked("invalid review result")
    reviewed_date = str(review["reviewed_at"])[:10]
    if reviewed_date >= "2026-10-15":
        missing_counts = [field for field in DAILY_EVIDENCE_COUNTS if field not in review]
        if missing_counts:
            raise GateBlocked(f"review missing separated daily evidence counts: {', '.join(missing_counts)}")
    for field in DAILY_EVIDENCE_COUNTS:
        if field in review and (not isinstance(review[field], int) or review[field] < 0):
            raise GateBlocked(f"{field} must be a nonnegative integer")
    if review["result"] == "NO_STATE_CHANGE":
        if review["review_complete"] is not True or not review["sources_checked"]:
            raise GateBlocked("NO_STATE_CHANGE requires a completed bounded review")
        if review["old_state"] != review["new_state"]:
            raise GateBlocked("NO_STATE_CHANGE cannot mutate accepted state")
        for field in ("new_qualifying_evidence_count", "new_counter_evidence_count"):
            if not isinstance(review[field], int) or review[field] < 0:
                raise GateBlocked("NO_STATE_CHANGE requires explicit nonnegative counts")
    if review["result"] == "HUMAN_GATE_REQUIRED" and review["old_state"] == review["new_state"]:
        # The accepted state remains frozen until a later human decision.
        return


def validate_irkutsk_budget(review: dict[str, Any]) -> None:
    budget = review.get("search_budget", {})
    if budget.get("targeted_search_groups", 0) > 4 or budget.get("webpage_open_attempts", 0) > 8:
        raise GateBlocked("Irkutsk consolidated search budget exceeded")
    sources = review.get("source_graph", [])
    ids = [row.get("source_id") for row in sources]
    if len(ids) != len(set(ids)) or any(not value for value in ids):
        raise GateBlocked("Irkutsk source graph requires unique source IDs")
    for row in sources:
        required = {"url", "retrieved_at", "originator", "publisher", "source_type", "claim_ids", "depends_on", "relation", "verification_status", "search_boundary"}
        if not required.issubset(row):
            raise GateBlocked("Irkutsk source graph record is incomplete")


def check_schedule_ownership(snapshot: dict[str, Any]) -> dict[str, Any]:
    timers = [row for row in snapshot.get("timers", []) if row.get("project") == "StructEvidence" and row.get("active")]
    owners = {row.get("logical_owner") or row.get("id") for row in timers}
    exact = len(timers) == 1 and len(owners) == 1
    timer = timers[0] if exact else None
    exact = bool(exact and timer.get("timezone") == "Asia/Singapore" and timer.get("local_time") == "22:00")
    return {
        "state": "PASS" if exact else ("FAIL" if timers else "UNVERIFIED"),
        "active_structevidence_timers": len(timers),
        "verified_owner": timer.get("logical_owner") if exact else None,
        "reason": None if exact else "expected exactly one active StructEvidence timer at 22:00 Asia/Singapore",
    }


def classify_github_write(http_status: int | None, commit_sha: str | None) -> dict[str, Any]:
    if http_status in {200, 201} and commit_sha:
        return {"state": "GITHUB_COMMITTED", "commit_sha": commit_sha, "error_code": None}
    return {"state": "PUBLIC_UPDATE_BLOCKED", "commit_sha": None, "error_code": f"HTTP_{http_status}" if http_status else "NO_WRITE_INTERFACE"}


def verify_public_deploy(expected_sha: str, deployed_sha: str | None, http_status: int | None, body: str, marker: str) -> dict[str, Any]:
    matched = bool(http_status == 200 and deployed_sha == expected_sha and marker and marker in body)
    return {
        "result": "PUBLIC_VERIFIED" if matched else "PUBLIC_VERIFICATION_FAILED",
        "expected_sha": expected_sha,
        "deployed_sha": deployed_sha,
        "http_status": http_status,
        "body_marker_verified": bool(marker and marker in body),
    }


def _date_from_timestamp(value: str) -> dt.date:
    return dt.date.fromisoformat(value[:10])


def validate_event_record(event: dict[str, Any]) -> None:
    if event.get("schema_version") == "se-information-event-v1":
        required = {
            "event_id", "case_id", "published_at", "event_at", "retrieved_at",
            "original_url", "public_url", "snapshot_file", "snapshot_sha256",
            "verification_status", "classifications", "old_stop", "candidate_stop",
            "state_changed",
        }
        missing = sorted(required - set(event))
        if missing:
            raise GateBlocked(f"information event record missing required fields: {', '.join(missing)}")
        classifications = set(event["classifications"])
        if len(classifications & EVENT_CLASSIFICATIONS) != 1:
            raise GateBlocked("information event must be exactly NEW_EVENT or NEWLY_DISCOVERED_OLD_EVIDENCE")
        if not classifications <= EVENT_CLASSIFICATIONS | {"NO_STATE_CHANGE", "HUMAN_GATE_REQUIRED"}:
            raise GateBlocked("invalid information event classification")
        if event["verification_status"] not in {"PRIMARY_SOURCE_READ", "VERIFIED_PRIMARY_SOURCE"}:
            raise GateBlocked("unverified source cannot enter an information event record")
        if not re.fullmatch(r"[0-9a-f]{64}", event["snapshot_sha256"]):
            raise GateBlocked("snapshot_sha256 must be a lowercase SHA-256")
        event_start = _date_from_timestamp(str(event["event_at"]).split("/", 1)[0])
        published = _date_from_timestamp(str(event["published_at"]))
        retrieved = _date_from_timestamp(str(event["retrieved_at"]))
        if published > retrieved or event_start > retrieved:
            raise GateBlocked("event or publication date cannot be later than retrieval date")
        if event["state_changed"]:
            if "HUMAN_GATE_REQUIRED" not in classifications:
                raise GateBlocked("state-changing evidence requires a human gate")
        elif event["old_stop"] != event["candidate_stop"] or "NO_STATE_CHANGE" not in classifications:
            raise GateBlocked("unchanged stop requires identical stops and NO_STATE_CHANGE")
        if not event["original_url"].startswith("https://") or not event["public_url"].startswith("https://structurevidence.org/"):
            raise GateBlocked("event URLs violate the publication boundary")
        return

    required = {
        "event_id", "case_id", "title", "published_at", "event_at", "retrieved_at",
        "originator", "publisher", "source_type", "original_url", "accessibility",
        "specific_claims", "supports", "does_not_support", "depends_on",
        "conflicts_counter_evidence", "verification_status", "search_boundary",
        "snapshot_path", "snapshot_sha256", "old_stop", "candidate_stop",
        "state_changed", "review_id", "classifications", "public_url", "x_candidate_text",
    }
    missing = sorted(required - set(event))
    if missing:
        raise GateBlocked(f"event record missing required fields: {', '.join(missing)}")
    classifications = set(event["classifications"])
    if len(classifications & EVENT_CLASSIFICATIONS) != 1:
        raise GateBlocked("event must be exactly NEW_EVENT or NEWLY_DISCOVERED_OLD_EVIDENCE")
    if not classifications <= EVENT_CLASSIFICATIONS | {"NO_STATE_CHANGE", "HUMAN_GATE_REQUIRED"}:
        raise GateBlocked("invalid event classification")
    if event["verification_status"] != "VERIFIED_PRIMARY_SOURCE":
        raise GateBlocked("unverified source cannot enter a verified website update")
    if not re.fullmatch(r"[0-9a-f]{64}", event["snapshot_sha256"]):
        raise GateBlocked("snapshot_sha256 must be a lowercase SHA-256")
    event_start = _date_from_timestamp(str(event["event_at"]).split("/", 1)[0])
    published = _date_from_timestamp(str(event["published_at"]))
    retrieved = _date_from_timestamp(str(event["retrieved_at"]))
    if published > retrieved or event_start > retrieved:
        raise GateBlocked("event or publication date cannot be later than retrieval date")
    if "NEWLY_DISCOVERED_OLD_EVIDENCE" in classifications and max(published, event_start) >= retrieved:
        raise GateBlocked("historical evidence cannot be labeled as a same-day new event")
    if event["state_changed"]:
        if "HUMAN_GATE_REQUIRED" not in classifications:
            raise GateBlocked("state-changing evidence requires a human gate")
    elif event["old_stop"] != event["candidate_stop"] or "NO_STATE_CHANGE" not in classifications:
        raise GateBlocked("unchanged stop requires identical stops and NO_STATE_CHANGE")
    if not event["original_url"].startswith("https://") or not event["public_url"].startswith("https://structurevidence.org/"):
        raise GateBlocked("event URLs violate the publication boundary")


def build_event_x_candidate(date_sgt: str, event: dict[str, Any], publication_receipt: dict[str, Any] | None) -> dict[str, Any]:
    validate_event_record(event)
    verified = bool(
        publication_receipt
        and publication_receipt.get("event_id") == event["event_id"]
        and publication_receipt.get("result") == "PUBLIC_VERIFIED"
        and publication_receipt.get("http_status") == 200
        and publication_receipt.get("body_marker_verified") is True
        and publication_receipt.get("public_url") == event["public_url"]
    )
    if not verified:
        return {
            "schema_version": "se-x-candidate-v2", "candidate_id": f"SE-X-{date_sgt}-EVENT-BLOCKED",
            "scheduled_date": date_sgt, "text": None, "source_urls": [],
            "evidence_cutoff": event["retrieved_at"], "content_hash": None,
            "approval_gate": "BLOCKED", "status": "WEBSITE_PUBLICATION_BLOCKED",
            "blocker": "WEBSITE_PUBLICATION_BLOCKED", "selected_event_id": event["event_id"],
            "factual_status": "+".join(event["classifications"]), "x_post_sent": 0,
        }
    text = canonical_post_text(event["x_candidate_text"])
    candidate = {
        "schema_version": "se-x-candidate-v2", "candidate_id": f"SE-X-{date_sgt}-EVENT-01",
        "scheduled_date": date_sgt, "text": text, "source_urls": X_URL_RE.findall(text),
        "evidence_cutoff": event["retrieved_at"], "content_hash": sha256_text(text),
        "approval_gate": "HUMAN_GATE_REQUIRED", "status": "AWAITING_HUMAN_REVIEW",
        "blocker": "X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW", "selected_event_id": event["event_id"],
        "selection_reason": "NEW_EVENT" if "NEW_EVENT" in event["classifications"] else "NEWLY_DISCOVERED_OLD_EVIDENCE",
        "website_url": event["public_url"], "original_url": event["original_url"],
        "snapshot_path": event["snapshot_path"], "snapshot_sha256": event["snapshot_sha256"],
        "factual_status": "+".join(event["classifications"]),
        "dedup_scope": {"local_candidate_window_days": 7, "x_provider_history": "NOT_READ_X_AUTO_PUBLISH_PAUSED"},
        "material_state_transition": event["state_changed"], "account_identity": "@structevidence",
        "post_id": None, "public_url": None, "published_at": None,
        "verification_checked_at": None, "new_findings_existed": True,
        "correction_required": False, "x_post_sent": 0,
    }
    validate_candidate(candidate)
    if candidate["source_urls"] != [event["public_url"]]:
        raise GateBlocked("event X candidate must point only to its verified StructEvidence page")
    return candidate


def select_x_candidate(
    date_sgt: str,
    config: dict[str, Any],
    events: list[dict[str, Any]],
    publication_receipts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    todays = [event for event in events if str(event.get("retrieved_at", ""))[:10] == date_sgt]
    todays.sort(key=lambda event: (0 if "NEW_EVENT" in event.get("classifications", []) else 1, event["event_id"]))
    if todays:
        event = todays[0]
        return build_event_x_candidate(date_sgt, event, publication_receipts.get(event["event_id"]))
    return default_candidate(date_sgt, config)


def default_candidate(date_sgt: str, config: dict[str, Any]) -> dict[str, Any]:
    template = config["x"].get("daily_manual_text_template")
    if template is None:
        template = config["x"].get("method_test_text")
    if template is None:
        raise GateBlocked("no reviewed method candidate template configured")
    text = canonical_post_text(template.format(date_sgt=date_sgt))
    candidate = {
        "schema_version": "se-x-candidate-v2", "candidate_id": f"SE-X-{date_sgt}-METHOD-01",
        "day_index": None, "scheduled_date": date_sgt, "text": text,
        "source_urls": X_URL_RE.findall(text), "evidence_cutoff": config["x"]["method_cutoff"],
        "content_hash": sha256_text(text), "approval_gate": "HUMAN_GATE_REQUIRED",
        "material_state_transition": False, "account_identity": "@structevidence",
        "dedup_check": "MANUAL_REVIEW_PENDING", "publish_attempt_id": None,
        "post_id": None, "public_url": None, "published_at": None,
        "verification_checked_at": None, "status": "AWAITING_HUMAN_REVIEW",
        "selection_reason": "REVIEWED_METHOD_FALLBACK", "factual_status": "METHOD_CONTENT",
        "blocker": "X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW",
        "dedup_scope": {"local_candidate_window_days": 7, "x_provider_history": "NOT_READ_X_AUTO_PUBLISH_PAUSED"},
        "new_findings_existed": False, "correction_required": False, "x_post_sent": 0,
    }
    validate_candidate(candidate)
    return candidate


def new_run(date_sgt: str, baseline_sha: str) -> dict[str, Any]:
    scheduled = f"{date_sgt}T22:00:00+08:00"
    weekday = dt.date.fromisoformat(date_sgt).weekday()
    return {
        "schema_version": "se-unified-run-v1", "run_id": stable_run_id(date_sgt, scheduled),
        "date_sgt": date_sgt, "scheduled_at": scheduled, "started_at": None, "ended_at": None,
        "report_delivered_at": None,
        "repo_baseline_sha": baseline_sha, "repo_final_sha": None,
        "pipeline": {key: "UNVERIFIED" for key in ("scheduler", "cases", "cml_ingestion", "x_publish", "audit_persistence", "external_delivery")},
        "reviews": [],
        "x": {"account": "@structevidence", "publication_authorized": False, "account_verified": False,
              "candidate_file": None, "post_id": None, "post_url": None, "posted_at": None,
              "result": "NOT_ATTEMPTED", "blocker": None},
        "internal_workflows": {
            "sunday_weekly_synthesis": {"due": weekday == 6, "state": "UNVERIFIED" if weekday == 6 else "NOT_DUE", "artifact": None},
            "monday_socsm": {"due": weekday == 0, "state": "UNVERIFIED" if weekday == 0 else "NOT_DUE", "artifact": None, "public_projection": "PRIVATE"},
        },
        "receipt_ids": [], "alerts": [], "events": [], "outcome": "UNVERIFIED",
    }


def event(run: dict[str, Any], name: str, stage: str, proof: str | None = None) -> None:
    if name not in EVENTS:
        raise ValueError(name)
    payload = {"event_id": sha256_text(f"{run['run_id']}|{name}|{stage}|{proof or ''}"), "event": name, "stage": stage, "at": iso_now()}
    if proof:
        payload["proof"] = proof
    if not any(row["event_id"] == payload["event_id"] for row in run["events"]):
        run["events"].append(payload)


def render_report(run: dict[str, Any], candidate: dict[str, Any], cross_project: dict[str, Any]) -> str:
    def row(name: str, due: str, enabled: str, actual: str, evidence: str, receipt: str, state: str, action: str) -> str:
        assert state in ALLOWED_STATES
        return f"| {name} | {due} | {enabled} | {actual} | {evidence} | {receipt} | {state} | {action} |"
    review_by_case = {r.get("case_id"): r for r in run.get("reviews", [])}
    lines = [
        f"# StructEvidence Daily Execution Report | {run['date_sgt']} | SGT", "",
        f"Run ended at: {run.get('ended_at') or 'NONE'}",
        f"Report delivered at: {run.get('report_delivered_at') or 'NONE'}",
        f"Delivery state: {run.get('pipeline', {}).get('external_delivery', 'UNVERIFIED')}", "",
        "| Project / subflow | Due | Enabled | Last actual run | Execution evidence (review/artifact) | Publish/delivery receipt | State | Failure / next action |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for cid, label in (("CML-PDRE-001", "SE 800V"), ("SE-BESS-SODIUM-001", "SE sodium BESS"), ("SE-IRK-LAB-001", "SE Irkutsk direct+indirect")):
        r = review_by_case.get(cid)
        state = ("PARTIAL" if r and r.get("result") == "REVIEW_INCOMPLETE" else
                 "HOLD" if r and r.get("result") == "HUMAN_GATE_REQUIRED" else
                 "PASS" if r else "UNVERIFIED")
        lines.append(row(label, "YES", "YES", r.get("reviewed_at", "NONE") if r else "NONE", r.get("review_id", "NONE") if r else "NONE", "pending", state, r.get("result", "bounded review not recorded") if r else "bounded review not recorded"))
    weekday = dt.date.fromisoformat(run["date_sgt"]).weekday()
    internal = run.get("internal_workflows", {})
    weekly = internal.get("sunday_weekly_synthesis", {"state": "UNVERIFIED", "artifact": None})
    socsm = internal.get("monday_socsm", {"state": "UNVERIFIED", "artifact": None})
    lines.append(row("SE weekly synthesis + folded NSCLC", "Sundays", "YES", "NONE", weekly.get("artifact") or "NONE", "pending", weekly["state"], "same-run Sunday addendum only"))
    lines.append(row("SE SOCSM", "Mondays", "YES", "NONE", socsm.get("artifact") or "NONE", "PRIVATE", socsm["state"], "same-run Monday check only; strict private/public wall"))
    x = run["x"]
    x_state = "PASS" if x.get("post_url") else ("BLOCKED" if x.get("blocker") else "UNVERIFIED")
    lines.append(row("SE X candidate", "YES", "REPORT-ONLY", "NONE", candidate["candidate_id"], x.get("blocker") or "NONE", x_state, "human review and manual publication"))
    for key, label, due in (("cml", "CML technical/FDE", "own daily plan"), ("lovetimeline", "LoveTimeline", "Mon/Tue/Fri")):
        item = cross_project.get(key, {})
        lines.append(row(label, due, str(item.get("enabled", "UNKNOWN")), item.get("last_actual_run", "NONE"), item.get("artifact", "NONE"), item.get("receipt", "draft only; OUTREACH HOLD"), item.get("state", "UNVERIFIED"), item.get("next_action", "read permission or real run evidence required")))
    due_count = 5 + (1 if weekday == 6 else 0) + (1 if weekday == 0 else 0) + (1 if weekday in {0, 1, 4} else 0)
    verified = sum(1 for value in run["pipeline"].values() if value == "PASS")
    blocked = sum(1 for value in run["pipeline"].values() if value == "BLOCKED")
    totals = {field: sum(review.get(field, 0) for review in run.get("reviews", [])) for field in DAILY_EVIDENCE_COUNTS}
    lines += [
        "", "## Daily evidence accounting", "",
        *[f"- {field}: {totals[field]}" for field in DAILY_EVIDENCE_COUNTS],
        "", "## X daily post", "", f"- Exact English text: {candidate.get('text') or 'NONE — WEBSITE_PUBLICATION_BLOCKED'}",
        f"- State: {candidate['status']}",
        f"- Approval gate: {candidate['approval_gate']}",
        f"- Content hash: {candidate.get('content_hash') or 'NONE'}",
        f"- Cited URLs: {', '.join(candidate['source_urls']) or 'NONE'}",
        f"- Source cutoff: {candidate['evidence_cutoff']}",
        f"- Factual status: {candidate.get('factual_status', 'UNSPECIFIED')}",
        f"- Deduplication scope: {canonical_json(candidate.get('dedup_scope', {}))}",
        f"- Automatic publication blocker: {x.get('blocker') or candidate.get('blocker') or 'X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW'}",
        "- X_POST_SENT: 0",
        f"- Post ID: {x.get('post_id') or 'NONE'}", f"- Verified URL: {x.get('post_url') or 'NONE'}",
        f"- Published at: {x.get('posted_at') or 'NONE'}",
        f"- New findings existed: {'YES' if candidate.get('new_findings_existed') else 'NO'}",
        f"- Prior post correction needed: {'YES' if candidate.get('correction_required') else 'NO'}",
        "", "## Reconciliation", "", "- 7-day missing runs: UNVERIFIED until an independent health surface supplies run history",
        f"- due_count: {due_count}", f"- execution_verified_count: {verified}",
        f"- delivery_verified_count: {1 if x.get('post_url') else 0}", f"- blocked_count: {blocked}",
        f"- human_gate_count: {sum(1 for r in run.get('reviews', []) if r.get('result') == 'HUMAN_GATE_REQUIRED')}",
        "- next checkpoint: next bounded run at the existing single 22:00 Asia/Singapore trigger",
        "- confirmed platform connectivity: X automatic publication paused; no write interface called",
    ]
    return "\n".join(lines) + "\n"


def run_orchestrator(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    root = Path(args.root).resolve()
    config = json.loads((root / "data/ops/se/config.json").read_text(encoding="utf-8"))
    date_sgt = args.date or dt.datetime.now(SGT).date().isoformat()
    baseline_sha = args.baseline_sha or config["baseline_main_sha"]
    run = new_run(date_sgt, baseline_sha)
    state_root = Path(os.environ.get("SE_OPS_STATE_DIR", root / "data/ops/se"))
    run_file = state_root / "runs" / f"{date_sgt}.json"
    candidate_file = state_root / "x-candidates" / f"{date_sgt}.json"
    ledger = state_root / "ledger.jsonl"
    alerts_file = state_root / "alerts" / f"{date_sgt}.json"
    lease = Lease(state_root / "runtime" / f"{date_sgt}.lock.json", run["run_id"])
    lease.acquire()
    try:
        if run_file.exists():
            previous = json.loads(run_file.read_text(encoding="utf-8"))
            if previous.get("run_id") == run["run_id"] and previous.get("outcome") in {"PASS", "PARTIAL", "BLOCKED"}:
                return previous, json.loads(candidate_file.read_text(encoding="utf-8"))
        run["started_at"] = iso_now()
        event(run, "SCHEDULED", "scheduler", run["scheduled_at"])
        event(run, "STARTED", "orchestrator")
        ownership = json.loads((root / "data/ops/se/SCHEDULE_OWNERSHIP.json").read_text(encoding="utf-8"))
        check = check_schedule_ownership(ownership)
        run["pipeline"]["scheduler"] = "PASS" if check["state"] == "PASS" else "BLOCKED"
        if check["state"] != "PASS":
            run["alerts"].append({"code": "SCHEDULE_CONFLICT", "dedupe_key": f"SCHEDULE_CONFLICT:{date_sgt}", "detail": check["reason"]})

        reviews_path = root / "data/ops/se/review-inputs" / f"{date_sgt}.json"
        if reviews_path.exists():
            review_bundle = json.loads(reviews_path.read_text(encoding="utf-8"))
            reviews = review_bundle["reviews"]
            for review in reviews:
                validate_review(review)
                if review["case_id"] == "SE-IRK-LAB-001":
                    validate_irkutsk_budget(review)
            run["reviews"] = reviews
            run["pipeline"]["cases"] = "PARTIAL" if any(r["result"] == "REVIEW_INCOMPLETE" for r in reviews) else "PASS"
            event(run, "SEARCH_COMPLETED", "cases", str(reviews_path.relative_to(root)))

            weekly = run["internal_workflows"]["sunday_weekly_synthesis"]
            if weekly["due"]:
                addendum = review_bundle.get("sunday_weekly_addendum")
                if addendum and addendum.get("nsclc_management_status") == "FOLDED" and addendum.get("artifact"):
                    weekly_state = addendum.get("state", "PASS")
                    if weekly_state not in {"PASS", "PARTIAL", "HOLD"}:
                        raise ValueError(f"unsupported Sunday weekly state: {weekly_state}")
                    weekly.update(state=weekly_state, artifact=addendum["artifact"])
                else:
                    weekly["state"] = "BLOCKED"
                    run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"SUNDAY_ADDENDUM:{date_sgt}", "detail": "Sunday weekly synthesis with folded NSCLC was due but no validated addendum was supplied."})

            socsm = run["internal_workflows"]["monday_socsm"]
            if socsm["due"]:
                socsm_input = review_bundle.get("monday_socsm")
                opaque_ref = socsm_input.get("opaque_linkage_id", "") if socsm_input else ""
                if socsm_input and socsm_input.get("state") in {"PASS", "PARTIAL", "HOLD"} and re.fullmatch(r"SOCSM-[A-Z0-9-]{8,64}", opaque_ref):
                    socsm.update(state=socsm_input["state"], artifact=opaque_ref)
                else:
                    socsm["state"] = "BLOCKED"
                    run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"SOCSM:{date_sgt}", "detail": "Monday SOCSM was due but no validated private-wall result was supplied."})
            if any(item["state"] == "BLOCKED" for item in run["internal_workflows"].values()):
                run["pipeline"]["cases"] = "PARTIAL"
        else:
            run["pipeline"]["cases"] = "BLOCKED"
            run["alerts"].append({"code": "SOURCE_BLOCKED_NEW", "dedupe_key": f"CASE_REVIEW_MISSING:{date_sgt}", "detail": "No validated daily review-input bundle exists."})

        cross_project: dict[str, Any] = {}
        cross_path_value = args.cross_project_status or os.environ.get("SE_CROSS_PROJECT_STATUS")
        if cross_path_value:
            cross_path = Path(cross_path_value).resolve()
            cross_project = json.loads(cross_path.read_text(encoding="utf-8"))
            for name, item in cross_project.items():
                if name not in {"cml", "lovetimeline"} or item.get("state") not in ALLOWED_STATES:
                    raise GateBlocked("invalid cross-project read-only status bundle")
            run["pipeline"]["cml_ingestion"] = "PASS" if "cml" in cross_project else "PARTIAL"
            event(run, "ARTIFACT_CREATED", "cross_project_read_only", cross_path.name)
        else:
            run["pipeline"]["cml_ingestion"] = "UNVERIFIED"
            run["alerts"].append({"code": "OBSERVABILITY_BLOCKED", "dedupe_key": f"CROSS_PROJECT:{date_sgt}", "detail": "No verified CML/LoveTimeline run evidence was supplied."})

        event_records = []
        for path in sorted(root.glob("cases/*/events/*/index.json")):
            record = json.loads(path.read_text(encoding="utf-8"))
            validate_event_record(record)
            event_records.append(record)
        publication_receipts = {}
        receipts_dir = root / "data/ops/se/website-publications"
        if receipts_dir.is_dir():
            for path in sorted(receipts_dir.glob("*.json")):
                receipt = json.loads(path.read_text(encoding="utf-8"))
                if receipt.get("event_id"):
                    publication_receipts[receipt["event_id"]] = receipt
        candidate = select_x_candidate(date_sgt, config, event_records, publication_receipts)
        atomic_json(candidate_file, candidate, replace=False)
        run["x"]["candidate_file"] = artifact_ref(candidate_file, root, state_root)
        event(run, "ARTIFACT_CREATED", "x_candidate", run["x"]["candidate_file"])

        run["pipeline"]["x_publish"] = "BLOCKED"
        blocker = candidate.get("blocker") or "X_AUTO_PUBLISH_PAUSED_HUMAN_REVIEW"
        run["x"].update(result=candidate["status"], blocker=blocker)
        alert_code = "WEBSITE_PUBLICATION_BLOCKED" if blocker == "WEBSITE_PUBLICATION_BLOCKED" else "X_HUMAN_REVIEW_REQUIRED"
        run["alerts"].append({"code": alert_code, "dedupe_key": f"X:{date_sgt}:{alert_code}", "detail": blocker})

        run["pipeline"]["audit_persistence"] = "PASS"
        run["pipeline"]["external_delivery"] = "BLOCKED"
        run["alerts"].append({"code": "MISSING_RUN_DETECTION_NOT_INDEPENDENT", "dedupe_key": f"MISSING_HEARTBEAT:{date_sgt}", "detail": "No independent health surface has been verified."})
        run["ended_at"] = iso_now()
        failures = [state for state in run["pipeline"].values() if state in {"BLOCKED", "UNVERIFIED", "MISSED"}]
        run["outcome"] = "PASS" if not failures else ("PARTIAL" if run["pipeline"]["audit_persistence"] == "PASS" else "BLOCKED")
        atomic_json(alerts_file, {"schema_version": "se-alerts-v1", "run_id": run["run_id"], "alerts": run["alerts"]}, replace=False)
        event(run, "ARTIFACT_CREATED", "alerts", artifact_ref(alerts_file, root, state_root))
        report = render_report(run, candidate, cross_project)
        report_path = state_root / "reports" / f"{date_sgt}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        if report_path.exists() and report_path.read_text(encoding="utf-8") != report:
            raise AppendOnlyConflict(f"daily report already exists with different content: {report_path}")
        report_path.write_text(report, encoding="utf-8")
        event(run, "ARTIFACT_CREATED", "daily_report", artifact_ref(report_path, root, state_root))
        atomic_json(run_file, run, replace=False)
        append_jsonl_once(ledger, {"event_id": sha256_text(canonical_json(run)), "run_id": run["run_id"], "recorded_at": iso_now(), "outcome": run["outcome"], "run_file": artifact_ref(run_file, root, state_root)}, "run_id")
        return run, candidate
    finally:
        lease.release()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--date")
    parser.add_argument("--baseline-sha")
    parser.add_argument("--cross-project-status")
    parser.add_argument("--mode", choices=("report-only", "dry-run"), default="report-only")
    args = parser.parse_args()
    run, _ = run_orchestrator(args)
    print(canonical_json({"run_id": run["run_id"], "outcome": run["outcome"], "x_result": run["x"]["result"]}))
    return 0 if run["outcome"] in {"PASS", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
