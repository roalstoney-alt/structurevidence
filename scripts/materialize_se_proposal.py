#!/usr/bin/env python3
"""Validate and materialize an approved SE State proposal without overwrites."""
from __future__ import annotations

import argparse
import copy
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema

from se_frr_protocol import (
    ProtocolError,
    append_state,
    finalize_change,
    finalize_evidence,
    finalize_state,
    load_objects,
    state_hash,
    validate_bundle,
    validate_schema,
    verify_state_chain,
)

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL_SCHEMA = ROOT / "schemas" / "se-frr" / "state-change-proposal.schema.json"


def git(root: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=root, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def require_clean_worktree(root: Path) -> None:
    if git(root, "status", "--porcelain=v1"):
        raise ProtocolError("clean worktree required")


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def prepare_materialization(proposal: dict[str, Any], canonical_root: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    schema = json.loads(PROPOSAL_SCHEMA.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker()).validate(proposal)
    if proposal["validation_status"] != "VALIDATED" or proposal["review_status"] != "APPROVED" or proposal["status"] != "APPROVED":
        raise ProtocolError("proposal must be validated and approved")

    objects = load_objects(canonical_root)
    subject_states = sorted((item for item in objects["states"] if item["subject_id"] == proposal["subject_id"]), key=lambda item: (item["recorded_at"], item["state_id"]))
    if not subject_states:
        raise ProtocolError("proposal subject has no canonical State")
    previous = subject_states[-1]
    if previous["state_id"] != proposal["previous_state_id"] or previous["state_hash"] != proposal["previous_state_hash"]:
        raise ProtocolError("proposal previous State is not the verified canonical tail")
    if previous["state_hash"] != state_hash(previous) or verify_state_chain(subject_states)["result"] != "PASS":
        raise ProtocolError("canonical State tail or chain is invalid")

    evidence = [finalize_evidence(item) for item in copy.deepcopy(proposal["proposed_evidence"])]
    if [item["evidence_id"] for item in evidence] != proposal["proposed_evidence_ids"]:
        raise ProtocolError("proposed Evidence IDs do not match embedded Evidence")
    for item in evidence:
        validate_schema("evidence", item)
        if item["subject_id"] != proposal["subject_id"]:
            raise ProtocolError("proposed Evidence subject mismatch")
        if parse_time(item["observed_at"]) > parse_time(item["recorded_at"]):
            raise ProtocolError("Evidence observed_at cannot follow recorded_at")

    proposed_state = copy.deepcopy(proposal["proposed_state"])
    if proposed_state["subject_id"] != proposal["subject_id"] or proposed_state["previous_state_id"] != previous["state_id"] or proposed_state["previous_state_hash"] != previous["state_hash"]:
        raise ProtocolError("proposed State predecessor mismatch")
    if parse_time(proposed_state["observed_at"]) > parse_time(proposed_state["recorded_at"]) or parse_time(proposed_state["recorded_at"]) <= parse_time(previous["recorded_at"]):
        raise ProtocolError("proposed State timestamps are not canonical")
    new_state = finalize_state(proposed_state, previous["chain_hash"])
    validate_schema("states", new_state)

    proposed_change = copy.deepcopy(proposal["proposed_change_event"])
    proposed_change.update({
        "subject_id": proposal["subject_id"], "previous_state_id": previous["state_id"],
        "previous_state_hash": previous["state_hash"], "new_state_id": new_state["state_id"],
        "new_state_hash": new_state["state_hash"],
    })
    change = finalize_change(proposed_change)
    validate_schema("changes", change)
    if new_state["change_event_id"] != change["change_id"]:
        raise ProtocolError("Change reverse linkage mismatch")

    future = copy.deepcopy(objects)
    future["evidence"].extend(evidence)
    future["states"].append(new_state)
    future["changes"].append(change)
    result = validate_bundle(future)
    if result["result"] != "PASS":
        raise ProtocolError(f"full validation failed: {result['errors']}")
    if verify_state_chain(future["states"])["result"] != "PASS":
        raise ProtocolError("new State chain verification failed")
    return previous, evidence, new_state, change


def materialize(proposal_path: Path, root: Path = ROOT, dry_run: bool = False, commit: bool = False) -> dict[str, Any]:
    require_clean_worktree(root)
    proposal = json.loads(proposal_path.read_text(encoding="utf-8"))
    canonical_root = root / "data" / "se-frr"
    candidate_paths = [canonical_root / "evidence" / f"{item.get('evidence_id')}.json" for item in proposal.get("proposed_evidence", [])]
    if proposal.get("proposed_state", {}).get("state_id"):
        candidate_paths.append(canonical_root / "states" / f"{proposal['proposed_state']['state_id']}.json")
    if proposal.get("proposed_change_event", {}).get("change_id"):
        candidate_paths.append(canonical_root / "changes" / f"{proposal['proposed_change_event']['change_id']}.json")
    preexisting = [str(path) for path in candidate_paths if path.exists()]
    if preexisting:
        raise ProtocolError(f"destination already exists: {', '.join(preexisting)}")
    previous, evidence, state, change = prepare_materialization(proposal, canonical_root)
    targets = [(canonical_root / "evidence" / f"{item['evidence_id']}.json", item) for item in evidence]
    targets += [(canonical_root / "states" / f"{state['state_id']}.json", state), (canonical_root / "changes" / f"{change['change_id']}.json", change)]
    existing = [str(path) for path, _ in targets if path.exists()]
    if existing:
        raise ProtocolError(f"destination already exists: {', '.join(existing)}")
    summary = {"proposal_id": proposal["proposal_id"], "previous_state_id": previous["state_id"], "evidence": len(evidence), "state_id": state["state_id"], "change_id": change["change_id"], "chain_verification": "PASS", "dry_run": dry_run, "commit_sha": None}
    if dry_run:
        return summary

    for path, value in targets:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.parent.name == "states":
            append_state(path.parent, value)
        else:
            with path.open("x", encoding="utf-8") as handle:
                json.dump(value, handle, indent=2, sort_keys=True, ensure_ascii=False)
                handle.write("\n")

    if commit:
        relative = [str(path.relative_to(root)) for path, _ in targets]
        git(root, "add", "--", *relative)
        git(root, "commit", "-m", f"feat(se-frr): materialize {proposal['proposal_id']}")
        summary["commit_sha"] = git(root, "rev-parse", "HEAD")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal", required=True, help="Proposal ID or JSON path")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--commit", action="store_true", help="Commit verified materialized objects after writing")
    args = parser.parse_args()
    candidate = Path(args.proposal)
    proposal_path = candidate if candidate.exists() else args.root / "data" / "se-frr" / "proposals" / f"{args.proposal}.json"
    try:
        result = materialize(proposal_path, args.root.resolve(), args.dry_run, args.commit)
    except (OSError, subprocess.CalledProcessError, jsonschema.ValidationError, ProtocolError, ValueError) as exc:
        print(f"RESULT FAIL")
        print(f"ERROR {exc}")
        return 1
    for key, value in result.items():
        print(f"{key.upper()} {value}")
    print("RESULT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
