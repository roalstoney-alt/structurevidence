#!/usr/bin/env python3
"""Build the deterministic, offline-readable Vortex pre-pilot snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "research-snapshot" / "v0.1"
ENTRY_SHA = "85f625b1f1eec890bd9980e51d5e4da1078d7313"
GENERATED_AT = "2026-09-29"
PROTOCOL_VERSION = "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1"
VERSION_DOI = "10.5281/zenodo.23033588"
CONCEPT_DOI = "10.5281/zenodo.23033587"


def encode(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def read(relative: str) -> bytes:
    return (ROOT / relative).read_bytes()


def load(relative: str):
    return json.loads(read(relative))


def example(question: str, match_class: str, claim_id: str | None, claims, normalized, boundary=None):
    claim = claims.get(claim_id) if claim_id else None
    return {
        "input": question,
        "expected_match_class": match_class,
        "claim_id": claim_id,
        "legacy_state": claim["state"] if claim else None,
        "normalized_state": normalized[claim_id]["normalized"] if claim else None,
        "boundary": boundary if boundary is not None else claim["does_not_support"],
    }


def build_payloads():
    index = load("claims/index.json")
    claim_rows = index["claims"]
    counts = Counter(row["case_id"] for row in claim_rows)
    if len(claim_rows) != 26 or counts != Counter({"CML-PDRE-001": 9, "SE-BESS-SODIUM-001": 9, "SE-ONC-NSQNSCLC-CN-001": 8}):
        raise ValueError(f"authoritative claim count drift: total={len(claim_rows)} counts={dict(counts)}")

    claims = {row["claim_id"]: load(f"claims/{row['claim_id']}.json") for row in claim_rows}
    normalization_document = load("protocol/state-normalization-v0.1.json")
    normalized = {row["claim_id"]: row for row in normalization_document["claims"]}
    if set(claims) != set(normalized):
        raise ValueError("normalization coverage does not equal authoritative claim inventory")

    examples = [
        example("Has a named 800VDC SST system been commercially deployed?", "EXACT", "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT", claims, normalized),
        example("Is 800VDC widely adopted?", "EXACT", "CML-PDRE-001.INDUSTRY_ADOPTION", claims, normalized),
        example("Has sodium-ion BESS been commissioned at a named customer site?", "EXACT", "SE-BESS-SODIUM-001.NAMED_COMMISSIONED_SITE", claims, normalized),
        example("What was HARMONi-A overall survival?", "EXACT", "SE-ONC-NSQNSCLC-CN-001.HARMONI_A_OS", claims, normalized),
        example("What is my chance of surviving lung cancer with this treatment?", "EXACT", "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY", claims, normalized, "Population evidence does not authorize a personal probability, diagnosis, prognosis, or treatment ranking."),
        example("Is optical quantum computing replacing GPU clusters in Indonesian hospitals?", "NONE", None, claims, normalized, "No governed public claim match; no evidence conclusion is generated."),
    ]

    payloads = {
        "README.md": f"""# StructureEvidence Minimal Research Snapshot v0.1

This offline-readable snapshot freezes the StructureEvidence method contract, 26 public claim objects, orthogonal state-normalization mapping, required protocol schemas, and six representative resolver expectations before the Vortex Discovery Pilot.

- Repository baseline: `{ENTRY_SHA}`
- Protocol: `{PROTOCOL_VERSION}`
- Version DOI: `{VERSION_DOI}`
- Concept DOI: `{CONCEPT_DOI}`
- Claim inventory: 26 total (`CML-PDRE-001`: 9, `SE-BESS-SODIUM-001`: 9, `SE-ONC-NSQNSCLC-CN-001`: 8)

Start with `MANIFEST.json`, then inspect `method-contract.json`, `claims/index.json`, `protocol/state-normalization-v0.1.json`, and `resolver-examples.json`. Verify integrity with `SHA256SUMS.txt` from this directory.

Legacy claim `state` values are preserved. Normalized axes are additive and do not change evidence conclusions. The inference policy is closed-boundary: only explicit support authorizes reuse; undeclared inference is `OUT_OF_BOUNDARY`.
""".encode("utf-8"),
        "method-contract.json": read("method-contract.json"),
        "claims/index.json": read("claims/index.json"),
        "protocol/state-normalization-v0.1.json": read("protocol/state-normalization-v0.1.json"),
        "protocol/state-normalization/schema-v0.1.json": read("protocol/state-normalization/schema-v0.1.json"),
        "resolver-examples.json": encode({"version": "v0.1", "examples": examples}),
        "implementation.json": encode({
            "repository": "https://github.com/roalstoney-alt/structurevidence",
            "repository_commit": ENTRY_SHA,
            "protocol_version": PROTOCOL_VERSION,
            "resolver_endpoint": "https://api.structurevidence.org/resolve",
            "method_contract": "https://structurevidence.org/method-contract.json",
            "inference_policy": "CLOSED_BOUNDARY",
            "undeclared_inference": "OUT_OF_BOUNDARY",
        }),
    }
    for claim_id in sorted(claims):
        payloads[f"claims/{claim_id}.json"] = read(f"claims/{claim_id}.json")
    for relative in [
        "protocol/question-intake/schema-v0.1.json",
        "protocol/claim-match/schema-v0.1.json",
        "protocol/freshness/schema-v0.1.json",
        "protocol/applicability/schema-v0.1.json",
        "protocol/verification-quote/schema-v0.1.json",
        "protocol/publication-eligibility/schema-v0.1.json",
    ]:
        payloads[relative] = read(relative)

    manifest = {
        "snapshot_version": "v0.1",
        "paper_version": "v0.1",
        "version_doi": VERSION_DOI,
        "concept_doi": CONCEPT_DOI,
        "repository_commit": ENTRY_SHA,
        "protocol_version": PROTOCOL_VERSION,
        "total_claims": len(claim_rows),
        "case_count": len(counts),
        "claims_per_case": dict(sorted(counts.items())),
        "case_claim_counts": dict(sorted(counts.items())),
        "generated_at": GENERATED_AT,
        "files": [
            {"path": path, "sha256": digest(content), "size_bytes": len(content)}
            for path, content in sorted(payloads.items())
        ],
    }
    payloads["MANIFEST.json"] = encode(manifest)
    sums = [f"{digest(content)}  {path}" for path, content in sorted(payloads.items())]
    payloads["SHA256SUMS.txt"] = ("\n".join(sums) + "\n").encode("utf-8")
    return payloads


def write_outputs(destination: Path, payloads) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for relative, content in payloads.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payloads = build_payloads()
    if not args.check:
        write_outputs(DESTINATION, payloads)
        print(f"MINIMAL_RESEARCH_SNAPSHOT=GENERATED files={len(payloads)}")
        return 0
    with tempfile.TemporaryDirectory(prefix="structurevidence-snapshot-") as temporary:
        expected = Path(temporary)
        write_outputs(expected, payloads)
        actual_files = {path.relative_to(DESTINATION) for path in DESTINATION.rglob("*") if path.is_file()}
        expected_files = {Path(path) for path in payloads}
        stale = sorted(str(path) for path in actual_files ^ expected_files)
        stale.extend(
            str(path)
            for path in sorted(expected_files & actual_files)
            if (DESTINATION / path).read_bytes() != (expected / path).read_bytes()
        )
        if stale:
            print("STALE_MINIMAL_RESEARCH_SNAPSHOT")
            print("\n".join(stale))
            return 1
    print(f"MINIMAL_RESEARCH_SNAPSHOT=CURRENT files={len(payloads)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
