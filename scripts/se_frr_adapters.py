#!/usr/bin/env python3
"""Bounded adapters from existing CML/RDL records into SE-FRR v0.1 objects."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from se_frr_protocol import PROTOCOL_VERSION, finalize_evidence

ROOT = Path(__file__).resolve().parents[1]
CML_SOURCE = "technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json"
RDL_SOURCE = "rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json"
SUBJECT_ID = "SE-SUBJ-000001"


def provenance(source_object: str, recorded_at: str) -> dict[str, Any]:
    return {
        "repository": "StructEvidence",
        "commit_sha": None,
        "source_object": source_object,
        "created_by": "SE-FRR bounded adapter",
        "method_version": PROTOCOL_VERSION,
        "recorded_at": recorded_at,
        "supersedes": None,
        "superseded_by": None,
    }


def adapt_cml_subject(record: dict[str, Any]) -> dict[str, Any]:
    core = record["core"]
    pdre = record["pdre_record"]
    identity = pdre["identity"]
    return {
        "schema_version": "SE_SUBJECT_v0.1",
        "subject_id": SUBJECT_ID,
        "canonical_name": identity["title"],
        "subject_type": core["subject_class"],
        "aliases": [identity["cml_id"], identity["pdre_id"]],
        "industry": "AI data-center power infrastructure",
        "geography": [],
        "description": pdre["new_path"]["description"],
        "created_at": core["created_at"],
        "created_by": "SE-FRR bounded adapter",
        "visibility": "INTERNAL",
        "status": "WATCH",
        "tags": [core["protocol"], core["domain"]],
        "provenance": provenance(CML_SOURCE, core["created_at"]),
    }


def adapt_rdl_evidence(record: dict[str, Any], evidence_id: str = "SE-EV-20260920-900001") -> dict[str, Any]:
    core = record["core"]
    research = record["research_record"]
    evidence = {
        "schema_version": "SE_EVIDENCE_v0.1",
        "evidence_id": evidence_id,
        "subject_id": SUBJECT_ID,
        "published_at": None,
        "observed_at": core["effective_at"],
        "recorded_at": core["known_at"],
        "effective_at": core["effective_at"],
        "source": {
            "name": core["record_id"],
            "url": None,
            "type": core["subject_class"],
            "publisher": "StructEvidence RDL",
            "snapshot_ref": RDL_SOURCE,
            "retrieved_at": core["known_at"],
        },
        "raw_reference": core["record_hash"],
        "normalized_claim": research["hypothesis_after"],
        "evidence_type": "RDL_RESEARCH_RECORD",
        "review": {
            "status": "ACCEPTED",
            "reason": "Existing human-reviewed RDL record; no CML state mutation is implied.",
            "reviewed_at": core["updated_at"],
            "reviewed_by": "SE-FRR bounded adapter",
        },
        "counter_to": [],
        "research_class": research["research_class"],
        "visibility": "INTERNAL",
        "content_hash": "0" * 64,
        "provenance": provenance(RDL_SOURCE, core["known_at"]),
    }
    return finalize_evidence(evidence)
