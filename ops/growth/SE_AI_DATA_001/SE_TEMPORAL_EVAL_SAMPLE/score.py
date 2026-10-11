#!/usr/bin/env python3
"""Deterministic scorer for the SE-AI-DATA-001 sample."""

from __future__ import annotations

import json
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return rows


def score_submission(submission_path: Path) -> dict:
    gold_rows = load_jsonl(HERE / "gold.jsonl")
    submission_rows = load_jsonl(submission_path)
    gold = {row["task_id"]: row for row in gold_rows}
    submitted = {row.get("task_id"): row for row in submission_rows}
    unknown_task_ids = sorted(set(submitted) - set(gold))
    results = []

    for task_id, expected in gold.items():
        actual = submitted.get(task_id, {})
        components = {
            "state": 40 if actual.get("state") == expected["state"] else 0,
            "knowledge_cutoff": 15
            if actual.get("knowledge_cutoff") == expected["knowledge_cutoff"]
            else 0,
            "evidence_ids": 20
            if set(actual.get("evidence_ids", [])) == set(expected["evidence_ids"])
            else 0,
            "boundary": 0,
            "stop_decision": 10
            if actual.get("stop_decision") == expected["stop_decision"]
            else 0,
        }
        boundary = str(actual.get("boundary", "")).casefold()
        if all(term.casefold() in boundary for term in expected["boundary_required_terms"]):
            components["boundary"] = 15
        results.append(
            {
                "task_id": task_id,
                "score": sum(components.values()),
                "components": components,
            }
        )

    mean_score = sum(row["score"] for row in results) / len(results)
    coverage = sum(1 for task_id in gold if task_id in submitted) / len(gold)
    return {
        "sample_version": "v0.1",
        "task_count": len(gold),
        "coverage": coverage,
        "mean_score": mean_score,
        "unknown_task_ids": unknown_task_ids,
        "results": results,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} SUBMISSION.jsonl", file=sys.stderr)
        return 2
    try:
        result = score_submission(Path(sys.argv[1]))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["coverage"] == 1 and not result["unknown_task_ids"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
