#!/usr/bin/env python3
"""Commit-aware preservation helpers for CML v1.1 regression harnesses."""
from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path
from typing import Callable, Iterable

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_BASE_SHA = "a1bb8e442316c48acb0af2aca0c8c269b00340af"
V11_1_SHA = "2baced87c4df494fbbe706b4e73029d767050779"
V11_2_ENTRY_SHA = V11_1_SHA
V11_2_ACCEPTED_SHA = "33931a5de0e931b1ad218d63d83a9183fd3778ec"
HISTORY_PATH = "technical-risk/CML_VERSION_HISTORY.jsonl"
V11_1_AUTHORIZED_FILES = {
    HISTORY_PATH,
    "technical-risk/cml-method-registry.json",
    "technical-risk/cml-v1.1/METHOD_TRANSITION.json",
    "technical-risk/cml-v1.1/history/HISTORICAL_BRANCH_FREEZE.json",
    "docs/architecture/CML_V1_1_ARCHITECTURE.md",
    "scripts/test_cml_v11_transition.py",
}
V11_2_FROZEN_PREFIXES = (
    "technical-risk/cml-v1.1/schema/",
    "technical-risk/cml-v1.1/vocabulary/",
    "technical-risk/cml-v1.1/templates/",
)


def git(*args: str, text: bool = True):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=text)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def is_ancestor(ancestor: str, descendant: str) -> bool:
    return subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=ROOT, capture_output=True, check=False,
    ).returncode == 0


def milestone_changed_files(start: str, end: str) -> set[str]:
    return set(git("diff", "--name-only", start, end, "--").splitlines())


def validate_v11_1_milestone() -> dict:
    require(is_ancestor(HISTORICAL_BASE_SHA, V11_1_SHA), "V11-1 is not descended from the historical base")
    changed = milestone_changed_files(HISTORICAL_BASE_SHA, V11_1_SHA)
    require(changed == V11_1_AUTHORIZED_FILES, f"V11-1 milestone scope drift: {sorted(changed ^ V11_1_AUTHORIZED_FILES)}")
    return {"changed_files": len(changed), "milestone": V11_1_SHA}


def _historical_scope(path: str) -> bool:
    return (
        path.startswith("technical-risk/")
        or fnmatch.fnmatch(path, "docs/architecture/CML_*")
        or fnmatch.fnmatch(path, "docs/execution/CML_*")
        or fnmatch.fnmatch(path, "scripts/*cml*")
    )


def tracked_paths_at(commit: str) -> list[str]:
    return git("ls-tree", "-r", "--name-only", commit).splitlines()


def historical_protected_paths() -> list[str]:
    return sorted(
        path for path in tracked_paths_at(HISTORICAL_BASE_SHA)
        if _historical_scope(path) and path != HISTORY_PATH
    )


def frozen_v11_2_paths() -> list[str]:
    accepted = set(tracked_paths_at(V11_2_ACCEPTED_SHA))
    entry = set(tracked_paths_at(V11_2_ENTRY_SHA))
    return sorted(
        path for path in accepted - entry
        if path.startswith(V11_2_FROZEN_PREFIXES)
    )


def commit_bytes(commit: str, path: str) -> bytes:
    return git("show", f"{commit}:{path}", text=False)


def worktree_bytes(path: str) -> bytes | None:
    target = ROOT / path
    return target.read_bytes() if target.is_file() else None


def compare_content(
    paths: Iterable[str], expected: Callable[[str], bytes | None], actual: Callable[[str], bytes | None]
) -> list[str]:
    return sorted(path for path in paths if expected(path) != actual(path))


def historical_mutations() -> list[str]:
    return compare_content(
        historical_protected_paths(),
        lambda path: commit_bytes(HISTORICAL_BASE_SHA, path),
        worktree_bytes,
    )


def frozen_v11_2_mutations() -> list[str]:
    return compare_content(
        frozen_v11_2_paths(),
        lambda path: commit_bytes(V11_2_ACCEPTED_SHA, path),
        worktree_bytes,
    )


def validate_version_history_lines(current: list[str]) -> dict:
    prior = git("show", f"{HISTORICAL_BASE_SHA}:{HISTORY_PATH}").splitlines()
    milestone = git("show", f"{V11_1_SHA}:{HISTORY_PATH}").splitlines()
    require(len(milestone) == len(prior) + 1, "V11-1 did not append exactly its transition entry")
    require(len(current) >= len(prior) + 1, "V11-1 transition entry missing")
    require(current[: len(prior)] == prior, "pre-V11 version history was rewritten")
    transition_index = len(prior)
    require(current[transition_index] == milestone[transition_index], "V11-1 transition entry was rewritten")
    entry = json.loads(current[transition_index])
    require(entry["change_type"] == "METHOD_TRANSITION" and entry["method_version"] == "CML_v1.1", "invalid V11-1 transition entry")
    require(not entry["scientific_findings_changed"] and not entry["historical_records_rewritten"], "transition entry changes historical findings")
    for line in current:
        json.loads(line)
    return {"base_lines": len(prior), "transition_index": transition_index, "current_lines": len(current)}


def validate_version_history() -> dict:
    return validate_version_history_lines((ROOT / HISTORY_PATH).read_text(encoding="utf-8").splitlines())


def validate_v11_2_milestone() -> dict:
    head = git("rev-parse", "HEAD").strip()
    origin = git("rev-parse", "origin/main").strip()
    require(is_ancestor(V11_2_ENTRY_SHA, V11_2_ACCEPTED_SHA), "V11-2 accepted commit is not descended from its entry")
    require(is_ancestor(V11_2_ACCEPTED_SHA, head), "current HEAD is not descended from accepted V11-2")
    require(head == origin, "HEAD does not match origin/main")
    paths = frozen_v11_2_paths()
    require(paths, "no V11-2 frozen core artifacts resolved")
    mutations = frozen_v11_2_mutations()
    require(not mutations, f"accepted V11-2 core artifacts changed: {mutations}")
    return {"entry": V11_2_ENTRY_SHA, "accepted": V11_2_ACCEPTED_SHA, "head": head, "frozen_core_files": len(paths)}
