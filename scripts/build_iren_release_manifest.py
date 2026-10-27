#!/usr/bin/env python3
"""Create the deterministic IREN release manifest and SHA256SUMS."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "release" / "SE-IREN-TRACKER-PUBLIC-MVP-001"
ARTIFACTS = [
    "assets/iren-tracker.css",
    "docs/assets/iren-tracker.css",
    "docs/cases/index.html",
    "scripts/build_iren_public_tracker.py",
    "scripts/test_iren_public_tracker.py",
    "scripts/guard_history_immutability.py",
    "tests/test_history_immutability.py",
]
ARTIFACTS += [
    str(path.relative_to(ROOT))
    for path in sorted((ROOT / "cases" / "iren-ai-cloud-transition").glob("*"))
    if path.is_file()
]
ARTIFACTS += [
    str(path.relative_to(ROOT))
    for path in sorted((ROOT / "docs" / "cases" / "iren-ai-cloud-transition").glob("*"))
    if path.is_file()
]
ARTIFACTS += [
    str(path.relative_to(ROOT))
    for path in sorted(RELEASE.rglob("*"))
    if path.is_file()
    and path.name not in {"FREEZE_MANIFEST.json", "SHA256SUMS.txt"}
    and "-RESULT." not in path.name
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


manifest = {
    "schema_version": "SE-IREN-RELEASE-FREEZE-v0.1",
    "project": "SE-IREN-TRACKER-PUBLIC-MVP-001",
    "base_sha": "a3264420664a5c471fbc33829fc203429ca0f814",
    "feature_branch": "codex/se-iren-tracker-public-mvp-001",
    "evidence_cutoff": "2026-10-22",
    "last_source_check_utc": "2026-10-27T19:38:39Z",
    "reviewer_status": "PENDING_HUMAN_REVIEW",
    "publication_approved": False,
    "source_contract_sha256": "4cef5b37089eb0b85efe97304678ddeb32d6073b21d289c57dec8c2764432aed",
    "phase0_handoff_manifest_sha256": "36ba18248eb53ec0b02927d3991840f88f89940557382e3a209dea4c2932fa86",
    "artifacts": [{"path": path, "sha256": sha(ROOT / path)} for path in ARTIFACTS],
}
(RELEASE / "FREEZE_MANIFEST.json").write_text(
    json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

sum_paths = sorted(
    path for path in RELEASE.rglob("*")
    if path.is_file() and path.name != "SHA256SUMS.txt"
)
lines = [f"{sha(path)}  {path.relative_to(RELEASE)}" for path in sum_paths]
(RELEASE / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

print(f"FREEZE_MANIFEST_SHA256={sha(RELEASE / 'FREEZE_MANIFEST.json')}")
print(f"FILES_HASHED={len(sum_paths)}")
