#!/usr/bin/env python3
"""Append-only controlled observation runner for SE-CEPE-001."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "ops/research/SE_CEPE_001"
SAMPLE = ROOT / "ops/growth/SE_AI_DATA_001/SE_TEMPORAL_EVAL_SAMPLE"
ALLOWED_STATUSES = {
    "NO_MATERIAL_CHANGE",
    "NEW_EVIDENCE_OBSERVED",
    "EVIDENCE_CONFLICT",
    "SOURCE_UNAVAILABLE",
    "INTERPRETATION_REVIEW_REQUIRED",
    "NOT_RUN",
    "CHECK_FAILED",
}
MAX_BYTES = 2_000_000


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_hash(record: dict) -> str:
    payload = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_bytes(payload.encode("utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")


def validate_baseline(base: Path = DEFAULT_BASE) -> dict:
    registry = json.loads((base / "TASK_REGISTRY.json").read_text(encoding="utf-8"))
    tasks = read_jsonl(SAMPLE / "tasks.jsonl")
    gold = read_jsonl(SAMPLE / "gold.jsonl")
    manifest = json.loads((SAMPLE / "source_manifest.json").read_text(encoding="utf-8"))
    expected_ids = {f"SE-TECP-{number:03d}" for number in range(1, 9)}
    task_ids = {row["task_id"] for row in tasks}
    gold_ids = {row["task_id"] for row in gold}
    registry_ids = {row["task_id"] for row in registry["tasks"]}
    if task_ids != expected_ids or gold_ids != expected_ids or registry_ids != expected_ids:
        raise ValueError("baseline must contain exactly the eight frozen task IDs")
    for key, path in (
        ("task_source_sha256", SAMPLE / "tasks.jsonl"),
        ("gold_source_sha256", SAMPLE / "gold.jsonl"),
        ("manifest_source_sha256", SAMPLE / "source_manifest.json"),
    ):
        if sha256_file(path) != registry[key]:
            raise ValueError(f"frozen file hash drift: {path}")
    by_claim = {row["claim_id"]: row for row in gold}
    registry_by_task = {row["task_id"]: row for row in registry["tasks"]}
    for record in manifest["records"]:
        claim_path = ROOT / record["path"]
        if sha256_file(claim_path) != record["sha256"]:
            raise ValueError(f"frozen claim hash drift: {record['path']}")
        canonical = json.loads(claim_path.read_text(encoding="utf-8"))
        expected = by_claim[record["claim_id"]]
        if canonical["state"] != expected["state"] or canonical["as_of"] != expected["knowledge_cutoff"]:
            raise ValueError(f"Gold/canonical mismatch: {record['claim_id']}")
        registered = registry_by_task[expected["task_id"]]
        if registered["frozen_claim_ref"] != record["path"] or registered["frozen_claim_sha256"] != record["sha256"]:
            raise ValueError(f"registry/manifest mismatch: {record['claim_id']}")
    return {"registry": registry, "tasks": tasks, "gold": gold, "manifest": manifest}


def fetch_public_source(url: str, timeout: int) -> dict:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "StructEvidence-SE-CEPE-001/0.1 (+https://structurevidence.org/)"
        },
    )
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            body = response.read(MAX_BYTES + 1)
            truncated = len(body) > MAX_BYTES
            body = body[:MAX_BYTES]
            return {
                "retrieval_status": "AVAILABLE",
                "http_status": getattr(response, "status", 200),
                "final_url": response.geturl(),
                "source_content_sha256": sha256_bytes(body),
                "bytes_hashed": len(body),
                "content_truncated": truncated,
                "error": None,
            }
    except urllib.error.HTTPError as exc:
        return {
            "retrieval_status": "SOURCE_UNAVAILABLE",
            "http_status": exc.code,
            "final_url": url,
            "source_content_sha256": None,
            "bytes_hashed": 0,
            "content_truncated": False,
            "error": f"HTTPError:{exc.code}",
        }
    except Exception as exc:  # operational evidence; preserve without traceback/secrets
        return {
            "retrieval_status": "CHECK_FAILED",
            "http_status": None,
            "final_url": url,
            "source_content_sha256": None,
            "bytes_hashed": 0,
            "content_truncated": False,
            "error": type(exc).__name__,
        }


def fixture_result(url: str, fixture: str, task_id: str) -> dict:
    if fixture == "failure":
        return {
            "retrieval_status": "CHECK_FAILED",
            "http_status": None,
            "final_url": url,
            "source_content_sha256": None,
            "bytes_hashed": 0,
            "content_truncated": False,
            "error": "SyntheticNetworkFailure",
        }
    suffix = "changed" if fixture == "change" and task_id == "SE-TECP-001" else "stable"
    return {
        "retrieval_status": "AVAILABLE",
        "http_status": 200,
        "final_url": url,
        "source_content_sha256": sha256_bytes(f"{url}|{suffix}".encode()),
        "bytes_hashed": len(url) + len(suffix) + 1,
        "content_truncated": False,
        "error": None,
    }


def observation_status(result: dict, fixture: str | None, task_id: str) -> str:
    if result["retrieval_status"] == "CHECK_FAILED":
        return "CHECK_FAILED"
    if result["retrieval_status"] == "SOURCE_UNAVAILABLE":
        return "SOURCE_UNAVAILABLE"
    if fixture == "change" and task_id == "SE-TECP-001":
        return "NEW_EVIDENCE_OBSERVED"
    return "NO_MATERIAL_CHANGE"


def build_observation(run_id: str, checked_at: str, task: dict, result: dict, fixture: str | None) -> dict:
    status = observation_status(result, fixture, task["task_id"])
    observed_change = (
        "SYNTHETIC_FIXTURE_CONTENT_CHANGE"
        if status == "NEW_EVIDENCE_OBSERVED"
        else "NONE_WITHIN_SOURCE_AVAILABILITY_AND_RETRIEVAL_SCOPE"
        if status == "NO_MATERIAL_CHANGE"
        else status
    )
    record = {
        "run_id": run_id,
        "task_id": task["task_id"],
        "checked_at": checked_at,
        "observation_scope": "PRIMARY_SOURCE_AVAILABILITY_AND_RETRIEVAL_HASH_ONLY",
        "queries": [],
        "source_urls": result.get("attempted_urls", [result["final_url"]]),
        "source_attempts": result.get("attempts", []),
        "retrieval_status": result["retrieval_status"],
        "http_status": result["http_status"],
        "source_published_at": task["public_disclosure_at"],
        "source_content_sha256": result["source_content_sha256"],
        "content_truncated": result["content_truncated"],
        "canonical_event_identity": canonical_hash(
            {
                "task_id": task["task_id"],
                "source_url": result["final_url"],
                "source_content_sha256": result["source_content_sha256"],
            }
        ),
        "event_at": task["event_at"],
        "public_disclosure_at": task["public_disclosure_at"],
        "knowledge_cutoff_at": task["knowledge_cutoff_at"],
        "observation_status": status,
        "observed_change": observed_change,
        "evidence_citations": [result["final_url"]] if result["source_content_sha256"] else [],
        "counterevidence_citations": [],
        "analyst_inference": None,
        "decision_impact": "NOT_APPLICABLE_SOURCE_CHECK_ONLY",
        "error": result["error"],
    }
    record["record_hash"] = canonical_hash(record)
    return record


def write_cost_row(base: Path, summary: dict) -> None:
    path = base / "RUN_COST_LEDGER.csv"
    fields = [
        "run_id", "started_at", "finished_at", "mode", "tasks_scheduled",
        "checks_completed", "checks_failed", "runtime_seconds", "human_review_minutes",
        "agent_tool_cost", "content_drafts", "publication_approvals", "regression_status",
    ]
    exists = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({key: summary[key] for key in fields})


def write_change_report(base: Path, summary: dict, observations: list[dict]) -> None:
    material = [row for row in observations if row["observation_status"] in {"NEW_EVIDENCE_OBSERVED", "EVIDENCE_CONFLICT", "INTERPRETATION_REVIEW_REQUIRED"}]
    failures = [row for row in observations if row["observation_status"] in {"SOURCE_UNAVAILABLE", "CHECK_FAILED", "NOT_RUN"}]
    if failures:
        what_changed = "OPERATIONAL_EXCEPTION_NOT_A_NULL_RESULT"
        decision_changed = "UNKNOWN — one or more bounded source checks were unavailable or failed."
    elif material:
        what_changed = "REVIEW_REQUIRED"
        decision_changed = "UNKNOWN — the synthetic or observed delta requires human semantic review."
    else:
        what_changed = "NONE_WITHIN_SEARCH_SCOPE"
        decision_changed = "NO — no semantic evidence assessment was performed."
    lines = [
        f"# Evidence Change Report — {summary['run_id']}",
        "",
        f"CHECKED_AT = `{summary['finished_at']}`",
        "",
        f"WHAT_CHANGED = `{what_changed}`",
        "",
        "WHY_IT_MATTERS = `Source availability and retrieval hashes establish an operational baseline; semantic claim review was outside this controlled source-check scope.`",
        "",
        f"DECISION_CHANGED = `{decision_changed}`",
        "",
        "PRODUCT_IMPROVEMENT = `NONE`",
        "",
        "NEXT_OBSERVABLE = `The task-specific events in TASK_REGISTRY.json.`",
        "",
        f"MATERIAL_EVENT_COUNT = `{len(material)}`",
        "",
        f"OPERATIONAL_EXCEPTION_COUNT = `{len(failures)}`",
        "",
        "A retrieval failure is not a no-change observation. Historical Gold remains unchanged.",
    ]
    path = base / "EVIDENCE_CHANGE_REPORTS" / f"{summary['run_id']}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def execute(base: Path, run_id: str, checked_at: str, mode: str, timeout: int, fixture: str | None = None) -> dict:
    started = time.monotonic()
    baseline = validate_baseline(base)
    runs_path = base / "SOURCE_CHECK_RUNS.jsonl"
    existing_runs = read_jsonl(runs_path)
    if any(row["run_id"] == run_id for row in existing_runs):
        return {"run_id": run_id, "status": "ALREADY_RECORDED", "idempotent": True}
    registry_tasks = baseline["registry"]["tasks"]
    retrieval_cache: dict[str, dict] = {}
    observations = []
    for task in registry_tasks:
        if fixture is None:
            attempts = []
            result = None
            for url in task["source_urls"]:
                if url not in retrieval_cache:
                    retrieval_cache[url] = fetch_public_source(url, timeout)
                candidate = retrieval_cache[url]
                attempts.append({
                    "url": url,
                    "retrieval_status": candidate["retrieval_status"],
                    "http_status": candidate["http_status"],
                    "error": candidate["error"],
                })
                result = candidate
                if candidate["retrieval_status"] == "AVAILABLE":
                    break
            assert result is not None
            result = dict(result)
            result["attempted_urls"] = [attempt["url"] for attempt in attempts]
            result["attempts"] = attempts
        else:
            url = task["source_urls"][0]
            result = fixture_result(url, fixture, task["task_id"])
            result["attempted_urls"] = [url]
            result["attempts"] = [{
                "url": url,
                "retrieval_status": result["retrieval_status"],
                "http_status": result["http_status"],
                "error": result["error"],
            }]
        observations.append(build_observation(run_id, checked_at, task, result, fixture))
    completed = sum(row["observation_status"] not in {"SOURCE_UNAVAILABLE", "CHECK_FAILED", "NOT_RUN"} for row in observations)
    failed = len(observations) - completed
    material = sum(row["observation_status"] in {"NEW_EVIDENCE_OBSERVED", "EVIDENCE_CONFLICT", "INTERPRETATION_REVIEW_REQUIRED"} for row in observations)
    finished_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    summary = {
        "run_id": run_id,
        "started_at": checked_at,
        "finished_at": finished_at,
        "mode": mode,
        "tasks_scheduled": 8,
        "checks_completed": completed,
        "checks_failed": failed,
        "material_events": material,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "human_review_minutes": "UNKNOWN",
        "agent_tool_cost": "UNKNOWN",
        "content_drafts": 0,
        "publication_approvals": 0,
        "regression_status": "NOT_RUN",
        "status": "COMPLETE" if failed == 0 else "COMPLETE_WITH_OPERATIONAL_EXCEPTIONS",
    }
    summary["record_hash"] = canonical_hash(summary)
    append_jsonl(base / "TASK_OBSERVATION_LEDGER.jsonl", observations)
    append_jsonl(runs_path, [summary])
    write_cost_row(base, summary)
    write_change_report(base, summary, observations)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--run-id")
    parser.add_argument("--checked-at")
    parser.add_argument("--mode", choices=("controlled", "scheduled"), default="controlled")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--fixture", choices=("no-change", "change", "failure"))
    args = parser.parse_args()
    checked_at = args.checked_at or datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    run_id = args.run_id or f"SE-CEPE-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    try:
        result = execute(args.output_dir, run_id, checked_at, args.mode, args.timeout, args.fixture)
    except Exception as exc:
        print(json.dumps({"run_id": run_id, "status": "BLOCKED", "error": str(exc)}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
