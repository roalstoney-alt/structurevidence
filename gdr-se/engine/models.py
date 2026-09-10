from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResearchContext:
    subject: str
    profile: str
    display_label: str
    research_id: str
    report_id: str
    report_version: str
    research_status: str
    method_version: str
    category: str
    structural_state: str
    evidence_state: str
    material_inconsistency: str
    source_coverage: str
    last_reviewed: str
    publication_status: str
    supersession_status: str
    correction_status: str
    canonical_path: Path
    report_path: Path
    manifest_path: Path
    source_inventory_path: Path | None
    observation_registry_path: Path | None
    claim_registry_path: Path | None
    counter_evidence_path: Path | None
    numerical_reconciliation_path: Path | None
    independent_review_path: Path | None
    source_dependency_path: Path | None
    hypothesis_registry_path: Path | None
    sha256sums_path: Path | None
    supersession_paths: tuple[Path, ...]
    output_dir: Path
    static_authorization_id: str | None
    profile_config: dict[str, Any]


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    context: ResearchContext
    gate_results: list[dict[str, Any]]
    authorization: str
    public_status: str
    evaluation_as_of: str
    record_created_at: str
    aggregation_rule_version: str
    input_bundle_sha256: str
    evidence_envelope: dict[str, Any]
    config_hashes: dict[str, str]
    artifact_metadata: list[dict[str, Any]]
