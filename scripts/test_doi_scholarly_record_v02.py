#!/usr/bin/env python3
"""Validate the DOI backfill without permitting evidence or protocol drift."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE = "94ee5dc8670b8132979846c815b400f8cef17ab1"
VERSION_DOI = "10.5281/zenodo.23033588"
CONCEPT_DOI = "10.5281/zenodo.23033587"
VERSION_URL = f"https://doi.org/{VERSION_DOI}"
CONCEPT_URL = f"https://doi.org/{CONCEPT_DOI}"
ZENODO = "https://zenodo.org/records/23033588"


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def load(relative: str):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise AssertionError(f"duplicate JSON key in {relative}: {key}")
            value[key] = item
        return value

    return json.loads(read(relative), object_pairs_hook=unique_object)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate() -> None:
    method = load("method-contract.json")
    discovery = load(".well-known/structurevidence.json")
    require(read("method-contract.json") == read("docs/method-contract.json"), "method contract mirror drift")
    require(read(".well-known/structurevidence.json") == read("docs/.well-known/structurevidence.json"), "discovery mirror drift")
    require(read("agent/index.html") == read("docs/agent/index.html"), "agent page mirror drift")

    scholarly = method["scholarly_record"]
    require(scholarly["version_doi"] == VERSION_DOI and scholarly["version_doi_url"] == VERSION_URL, "version DOI mismatch")
    require(scholarly["concept_doi"] == CONCEPT_DOI and scholarly["concept_doi_url"] == CONCEPT_URL, "concept DOI mismatch")
    require(scholarly["canonical_scholarly_version"] == "VERSION_DOI", "version canonical marker mismatch")
    require(scholarly["canonical_scholarly_family"] == "CONCEPT_DOI", "family canonical marker mismatch")
    require(discovery["scholarly_record"]["zenodo_record"] == ZENODO, "discovery Zenodo mismatch")

    expected_purpose = "Prevent unsupported inference by separating evidence state, time boundary, and unresolved uncertainty."
    require(method["purpose"] == expected_purpose, "method purpose changed")
    require(method["question_protocol"]["version"] == "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1", "protocol version changed")
    require(method["question_protocol"]["automatic_research_authorization"] is False, "authorization boundary changed")

    package = "research/STRUCTEVIDENCE_METHOD_PAPER_AND_REPLICATION_KIT_v0.1"
    papers = [
        f"{package}/paper/STRUCTEVIDENCE_METHOD_PAPER_EN_v0.1.md",
        f"{package}/paper/STRUCTEVIDENCE_METHOD_PAPER_ZH_v0.1.md",
    ]
    for path in papers:
        body = read(path)
        require(VERSION_URL in body and CONCEPT_URL in body and BASELINE in body, f"missing scholarly metadata: {path}")

    kit_readme = read(f"{package}/README.md")
    require(VERSION_URL in kit_readme and CONCEPT_URL in kit_readme, "replication README DOI block missing")
    require("QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1" in kit_readme, "replication README protocol relation missing")

    for draft in ["publication/MEDIUM_DRAFT_EN.md", "publication/ZHIHU_DRAFT_ZH.md"]:
        body = read(f"{package}/{draft}")
        require(VERSION_URL in body and CONCEPT_URL in body, f"publication footer missing: {draft}")

    citation = read("CITATION.cff")
    require(f'doi: "{VERSION_DOI}"' in citation, "CITATION.cff primary DOI is not the version DOI")
    require(f'value: "{CONCEPT_DOI}"' in citation, "CITATION.cff concept DOI identifier missing")
    require(citation.count(f'doi: "{VERSION_DOI}"') == 2, "version DOI must remain primary and preferred")

    manifest_path = f"{package}/release/RELEASE_MANIFEST.json"
    manifest = load(manifest_path)
    require(manifest["version_doi"] == VERSION_DOI, "release manifest version DOI mismatch")
    require(manifest["concept_doi"] == CONCEPT_DOI, "release manifest concept DOI mismatch")
    require(manifest["implementation_baseline"] == BASELINE, "release manifest baseline mismatch")

    spec = read(f"{package}/spec/QUESTION_TO_EVIDENCE_PROTOCOL_SPEC_v0.1.md")
    require(VERSION_URL in spec and CONCEPT_URL in spec, "protocol spec scholarly reference missing")

    changed = subprocess.run(
        ["git", "diff", "--name-only", BASELINE, "--", "claims", "docs/claims", "cases", "technical-risk/cml-v1.1", "rdl"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    require(not changed, f"immutable evidence surface changed: {changed}")


if __name__ == "__main__":
    validate()
    print("DOI_SCHOLARLY_RECORD_V02_TESTS_PASS")
