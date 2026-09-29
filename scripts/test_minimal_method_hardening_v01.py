#!/usr/bin/env python3
"""Validate minimal pre-Vortex hardening and snapshot integrity."""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]
ENTRY_SHA = "85f625b1f1eec890bd9980e51d5e4da1078d7313"
SNAPSHOT = ROOT / "research-snapshot" / "v0.1"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    index = load(ROOT / "claims/index.json")
    counts = Counter(row["case_id"] for row in index["claims"])
    require(len(index["claims"]) == 26, "authoritative total must be 26")
    require(counts == Counter({"CML-PDRE-001": 9, "SE-BESS-SODIUM-001": 9, "SE-ONC-NSQNSCLC-CN-001": 8}), "authoritative 9/9/8 split changed")

    normalization = load(ROOT / "protocol/state-normalization-v0.1.json")
    schema = load(ROOT / "protocol/state-normalization/schema-v0.1.json")
    jsonschema.validate(normalization, schema)
    mappings = {row["claim_id"]: row for row in normalization["claims"]}
    require(set(mappings) == {row["claim_id"] for row in index["claims"]}, "normalization coverage mismatch")
    require(mappings["CML-PDRE-001.NAMED_FIELD_DEPLOYMENT"]["normalized"]["verification_depth"] == "FIELD_DEPLOYED_SINGLE_INSTANCE", "single-instance mapping mismatch")
    require(mappings["SE-ONC-NSQNSCLC-CN-001.HARMONI_A_OS"]["normalized"]["applicability_scope"] == "POPULATION_SPECIFIC", "trial-population mapping mismatch")
    production = mappings["SE-BESS-SODIUM-001.PRODUCTION_READINESS"]
    require(production["normalized"]["epistemic_state"] == "UNKNOWN", "verification-required epistemic state must be unknown")
    require(production["normalized"]["workflow_state"] == "VERIFICATION_REQUIRED", "verification workflow separation missing")
    require(production["mapping_status"] == "REVIEW_REQUIRED", "unresolved epistemic mapping must stay review-required")

    method = load(ROOT / "method-contract.json")
    require((ROOT / "method-contract.json").read_bytes() == (ROOT / "docs/method-contract.json").read_bytes(), "method root/docs parity failed")
    policy = method["inference_policy"]
    require(policy["mode"] == "CLOSED_BOUNDARY", "closed-boundary policy missing")
    require(policy["rule_id"] == "UNDECLARED_INFERENCE_NOT_AUTHORIZED", "inference rule ID mismatch")
    require(policy["undeclared_inference"] == "OUT_OF_BOUNDARY", "undeclared inference policy mismatch")

    manifest = load(SNAPSHOT / "MANIFEST.json")
    require(manifest["total_claims"] == len(index["claims"]), "snapshot count differs from authoritative source")
    require(manifest["claims_per_case"] == dict(sorted(counts.items())), "generated claims-per-case mismatch")
    require(manifest["case_count"] == 3 and manifest["case_claim_counts"] == dict(sorted(counts.items())), "snapshot case counts mismatch")
    require(manifest["repository_commit"] == ENTRY_SHA, "snapshot repository baseline mismatch")
    for entry in manifest["files"]:
        path = SNAPSHOT / entry["path"]
        require(path.is_file(), f"snapshot file missing: {entry['path']}")
        require(path.stat().st_size == entry["size_bytes"], f"snapshot size mismatch: {entry['path']}")
        require(sha256(path) == entry["sha256"], f"snapshot manifest hash mismatch: {entry['path']}")
    for line in (SNAPSHOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        require(sha256(SNAPSHOT / relative) == expected, f"SHA256SUMS mismatch: {relative}")
    for row in index["claims"]:
        relative = Path("claims") / f"{row['claim_id']}.json"
        require((SNAPSHOT / relative).read_bytes() == (ROOT / relative).read_bytes(), f"snapshot claim differs: {row['claim_id']}")

    immutable = subprocess.run(
        ["git", "diff", "--name-only", ENTRY_SHA, "--", "claims", "docs/claims", "cases", "technical-risk/cml-v1.1", "rdl"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(not immutable, f"public claim or primitive changed: {immutable}")


if __name__ == "__main__":
    validate()
    print("MINIMAL_METHOD_HARDENING_V01_TESTS_PASS")
