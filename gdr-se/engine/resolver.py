from __future__ import annotations

import json
from pathlib import Path

from integrity import read_json
from models import ResearchContext


ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = ROOT / "gdr-se" / "config" / "research_profiles.json"


def _static_id(path: Path) -> str | None:
    if not path.exists():
        return None
    data = read_json(path)
    return data.get("authorization_id")


def load_profiles(path: Path = PROFILES_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(subject: str, root: Path = ROOT) -> ResearchContext:
    profiles = load_profiles(root / "gdr-se" / "config" / "research_profiles.json")
    normalized = subject.lower()
    if normalized == "strategy":
        profile_name = "STRATEGY_LEGACY_METHOD_PILOT"
        profile = profiles["profiles"][profile_name]
        strategy_freeze = root / "evidence-freeze" / "S6.1a"
        if not strategy_freeze.exists():
            strategy_freeze = root.parent / "evidence-freeze" / "S6.1a"
        return ResearchContext(
            subject="strategy",
            profile=profile_name,
            display_label="Strategy 2026",
            research_id="ECL.COMPANY.STRATEGY_INC.2026.001",
            report_id="Strategy_2026_Public_Evidence_Research_Report_v0.1",
            report_version="Public v0.1",
            research_status="METHOD PILOT",
            method_version="ECL_METHOD_PILOT_v0.1",
            category=profile["freshness_category"],
            structural_state="HYBRID_ACCUMULATION_MONETIZATION",
            evidence_state="SEMANTIC_TENSION_BUT_RECONCILABLE",
            material_inconsistency="NO",
            source_coverage="PARTIAL",
            last_reviewed="2026-09-08",
            publication_status="METHOD PILOT",
            supersession_status="CURRENT",
            correction_status="NONE",
            canonical_path=root / "research" / "PUBLICATION_PACKAGE_MANIFEST_EN.json",
            report_path=root / "research" / "Strategy_2026_Public_Evidence_Research_Report_v0.1_EN.md",
            manifest_path=root / "research" / "PUBLICATION_PACKAGE_MANIFEST_EN.json",
            source_inventory_path=strategy_freeze / "SOURCE_DEPENDENCY_GRAPH_v2.json",
            observation_registry_path=strategy_freeze / "HYPOTHESIS_ASSESSMENTS_v2.json",
            claim_registry_path=strategy_freeze / "TRIANGULATION_MATRIX_v2.json",
            counter_evidence_path=strategy_freeze / "COUNTER_EVIDENCE_SEARCH_LOG_v3.json",
            numerical_reconciliation_path=None,
            independent_review_path=None,
            source_dependency_path=strategy_freeze / "SOURCE_DEPENDENCY_GRAPH_v2.json",
            hypothesis_registry_path=strategy_freeze / "HYPOTHESIS_ASSESSMENTS_v2.json",
            sha256sums_path=strategy_freeze / "SHA256SUMS.txt",
            supersession_paths=(),
            output_dir=root / "research" / "gdr-se" / "strategy-2026",
            static_authorization_id=_static_id(root / "research" / "gdr-se" / "strategy-2026" / "GDR_SE_AUTHORIZATION_RECORD.json"),
            profile_config=profile,
        )
    symbol = subject.upper()
    if symbol not in {"BNB", "SOL", "TRX", "XLM"}:
        raise ValueError(f"UNKNOWN_GDR_SE_SUBJECT:{subject}")
    profile_name = "DIGITAL_ASSET_R1"
    profile = profiles["profiles"][profile_name]
    base = root / "evidence-freeze" / "DIGITAL-ASSET-BATCH-01-R1" / symbol
    canonical = read_json(base / "CANONICAL_RESEARCH_R1.json")
    return ResearchContext(
        subject=symbol,
        profile=profile_name,
        display_label=symbol,
        research_id=canonical["research_id"],
        report_id=f"{symbol}_PUBLIC_EVIDENCE_RESEARCH_REPORT_R1",
        report_version="R1",
        research_status=canonical.get("research_status", canonical.get("publication_status", "R1 RESEARCH SUPPORT")),
        method_version=canonical["method_version"],
        category=profile["freshness_category"],
        structural_state=canonical["structural_state_final"],
        evidence_state=canonical["evidence_state_final"],
        material_inconsistency=canonical["material_inconsistency"],
        source_coverage=canonical["source_coverage"],
        last_reviewed=canonical["last_reviewed"],
        publication_status=canonical["publication_status"],
        supersession_status=canonical.get("supersession_status", "UNRESOLVED"),
        correction_status=canonical.get("correction_status", "NONE"),
        canonical_path=base / "CANONICAL_RESEARCH_R1.json",
        report_path=base / "PUBLIC_EVIDENCE_RESEARCH_REPORT_R1.md",
        manifest_path=base / "MANIFEST.json",
        source_inventory_path=base / "SOURCE_INVENTORY.json",
        observation_registry_path=base / "OBSERVATION_REGISTRY.json",
        claim_registry_path=base / "CLAIM_REGISTRY.json",
        counter_evidence_path=base / "COUNTER_EVIDENCE_SEARCH_LOG.json",
        numerical_reconciliation_path=base / "NUMERICAL_RECONCILIATION.json",
        independent_review_path=base / "AGREEMENT_DIVERGENCE_AUDIT.md",
        source_dependency_path=base / "SOURCE_DEPENDENCY_GRAPH.json",
        hypothesis_registry_path=base / "HYPOTHESIS_REGISTRY.json",
        sha256sums_path=base / "SHA256SUMS.txt",
        supersession_paths=(base / "SUPERSESSION_NOTICE.md",),
        output_dir=root / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se",
        static_authorization_id=_static_id(root / "research" / "digital-assets" / "batch-01-r1" / symbol / "gdr-se" / "GDR_SE_AUTHORIZATION_RECORD.json"),
        profile_config=profile,
    )
