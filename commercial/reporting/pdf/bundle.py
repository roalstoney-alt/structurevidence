from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRODUCT_VERSION = "STRUCTEVIDENCE_PAID_PDF_v0.1"
PRODUCT_SKU = "VERIFIED_RESEARCH_REPORT_PDF"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def content_hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def subject_paths(subject: str) -> dict[str, Path]:
    key = subject.lower()
    if key == "strategy":
        return {
            "canonical": ROOT / "research" / "strategy-2026" / "CANONICAL_RESEARCH.json",
            "gdr": ROOT / "research" / "gdr-se" / "strategy-2026" / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json",
            "source_inventory": ROOT / "research" / "strategy-2026" / "SOURCE_INVENTORY.json",
            "numerical": ROOT / "research" / "strategy-2026" / "NUMERICAL_RECONCILIATION.json",
            "counter": ROOT / "research" / "strategy-2026" / "COUNTER_EVIDENCE_SEARCH_LOG.json",
        }
    symbol = key.upper()
    base = ROOT / "research" / "digital-assets" / "batch-01-r1" / symbol
    return {
        "canonical": base / "CANONICAL_RESEARCH_R1.json",
        "gdr": base / "gdr-se" / "GDR_SE_AUTHORIZATION_RECORD_R1_1.json",
        "source_inventory": base / "SOURCE_INVENTORY.json",
        "numerical": base / "NUMERICAL_RECONCILIATION.json",
        "counter": base / "COUNTER_EVIDENCE_SEARCH_LOG.json",
    }


def synthetic_happy_path_bundle(evaluation_as_of: str) -> dict:
    generated_at = "2026-09-11T00:00:00Z"
    bundle = {
        "report_id": "SE-PAID-PDF-HAPPY-PATH",
        "artifact_id": "ART-SE-PAID-PDF-HAPPY-PATH-v0.1",
        "research_id": "SE.TEST.PAID_PDF.2026.001",
        "subject_id": "Synthetic Paid PDF Fixture",
        "report_version": "STRUCTEVIDENCE_PAID_PDF_v0.1",
        "evaluation_as_of": evaluation_as_of,
        "generated_at": generated_at,
        "product_sku": PRODUCT_SKU,
        "pdf_product_version": PRODUCT_VERSION,
        "research_snapshot": {"finding": "Synthetic fixture for paid PDF fulfillment validation.", "canonical_research_sha256": "0" * 64, "report_sha256": "1" * 64, "rtp_manifest_sha256": "2" * 64, "observation_registry_sha256": "3" * 64, "claim_registry_sha256": "4" * 64, "counter_evidence_sha256": "5" * 64},
        "timeline_snapshot": {"current_structural_state": "SYNTHETIC_CURRENT_STATE", "level": [{"dimension_id": "SUPPLY_STRUCTURE", "state": "CURRENT"}, {"dimension_id": "VALIDATOR_DISTRIBUTION", "state": "CURRENT"}], "delta": [{"dimension_id": "SUPPLY_STRUCTURE", "state": "STABLE"}], "events": [{"event_id": "SYN-E1", "label": "Synthetic current observation", "event_domain": "SUBJECT_EVENT"}]},
        "freshness_snapshot": {"policy_version": "RDL_FRESHNESS_v0.1a", "release_freshness": "CURRENT", "level_freshness": [{"dimension_id": "SUPPLY_STRUCTURE", "freshness_state": "CURRENT"}], "delta_freshness": [{"dimension_id": "SUPPLY_STRUCTURE", "freshness_state": "CURRENT"}], "critical_evidence_freshness": [{"family_id": "PRIMARY_SOURCE_COVERAGE", "freshness_state": "CURRENT", "criticality": "CRITICAL"}], "next_refresh_reason": "EXPECTED_REPORTING_EVENT", "freshness_input_bundle_sha256": "6" * 64},
        "ecl_snapshot": {"evidence_state": "CONSISTENT", "finding": "Synthetic evidence is internally consistent for fixture purposes."},
        "gdr_snapshot": {"authorization": "ALLOW_PAID_DELIVERY", "authorization_id": "GDR-SE-AUTH-PAID-PDF-FIXTURE", "evaluation_as_of": evaluation_as_of, "gate_summary": {"PASS": 10}, "counterfactual": {"falsifiers": ["A new material event contradicts the synthetic current observation."], "discriminating_evidence": ["Primary source evidence captured after the material event."]}},
        "counterfactual": {"falsifiers": ["A verified correction changes the structural state.", "A source retraction invalidates the primary evidence."], "what_could_change": "New primary evidence, correction, or supersession could materially change this report."},
        "sources": [{"source_id": "S1", "title": "Synthetic Source Index", "source_class": "TEST_FIXTURE", "capture_date": "2026-09-11", "dependency_group": "G1", "artifact_class": "STRUCTURED_API_RESPONSE"}],
        "verification": {"canonical_research_sha256": "0" * 64, "timeline_input_bundle_sha256": "7" * 64, "freshness_input_bundle_sha256": "6" * 64, "freshness_policy_version": "RDL_FRESHNESS_v0.1a", "gdr_authorization_id": "GDR-SE-AUTH-PAID-PDF-FIXTURE", "correction_status": "NONE", "supersession_status": "CURRENT", "verify_path": "verify/reports/ART-SE-PAID-PDF-HAPPY-PATH-v0.1.json"},
    }
    bundle["report_content_bundle_sha256"] = content_hash(bundle)
    return bundle


def build_bundle(subject: str = "BNB", evaluation_as_of: str = "2026-09-11T00:00:00Z", fixture: str | None = None) -> dict:
    if fixture == "paid_report_happy_path":
        return synthetic_happy_path_bundle(evaluation_as_of)
    key = subject.lower()
    paths = subject_paths(subject)
    canonical = read_json(paths["canonical"])
    gdr = read_json(paths["gdr"])
    structural = read_json(ROOT / "timeline" / "subjects" / f"{key}_structural_timeline.json")
    events = read_json(ROOT / "timeline" / "subjects" / f"{key}_event_ledger.json")
    freshness = read_json(ROOT / "research" / "freshness" / key / "FRESHNESS_EVALUATION_v0.1a.json")
    sources = read_json(paths["source_inventory"]) if paths["source_inventory"].exists() else []
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    bundle = {
        "report_id": gdr.get("report_id", canonical.get("report_id", f"SE-{subject}-REPORT")),
        "artifact_id": f"ART-{subject.upper()}-PAID-PDF-v0.1",
        "research_id": gdr.get("research_id", canonical.get("research_id")),
        "subject_id": structural["subject_id"],
        "report_version": "STRUCTEVIDENCE_PAID_PDF_v0.1",
        "evaluation_as_of": evaluation_as_of,
        "generated_at": generated_at,
        "product_sku": PRODUCT_SKU,
        "pdf_product_version": PRODUCT_VERSION,
        "research_snapshot": {"finding": canonical.get("current_structural_state") or structural.get("current_structural_state"), "canonical_research_sha256": sha256_file(paths["canonical"]), "report_sha256": sha256_file(paths["canonical"]), "rtp_manifest_sha256": sha256_file(ROOT / "timeline" / "subjects" / f"{key}_timeline_derivation_manifest.json"), "observation_registry_sha256": sha256_file(paths["canonical"].with_name("OBSERVATION_REGISTRY.json")), "claim_registry_sha256": sha256_file(paths["canonical"].with_name("CLAIM_REGISTRY.json")), "counter_evidence_sha256": sha256_file(paths["counter"])},
        "timeline_snapshot": {"current_structural_state": structural.get("current_structural_state"), "level": structural.get("dimensions", [])[:6], "delta": freshness["dimension_delta_results"], "events": events.get("events", [])[:8]},
        "freshness_snapshot": {"policy_version": freshness["policy_version"], "release_freshness": freshness["release_result"]["release_freshness_state"], "level_freshness": freshness["dimension_level_results"], "delta_freshness": freshness["dimension_delta_results"], "critical_evidence_freshness": [row for row in freshness["evidence_family_results"] if row["criticality"] == "CRITICAL"], "next_refresh_reason": freshness["release_result"]["next_refresh_reason"], "freshness_input_bundle_sha256": freshness["input_bundle_hash"]},
        "ecl_snapshot": {"evidence_state": gdr.get("evidence_state_reference"), "finding": "See canonical research and GDR-SE gate table."},
        "gdr_snapshot": {"authorization": gdr["authorization"], "authorization_id": gdr["authorization_id"], "evaluation_as_of": gdr["evaluation_as_of"], "gate_summary": {row["status"]: sum(1 for g in gdr["gate_results"] if g["status"] == row["status"]) for row in gdr["gate_results"]}, "counterfactual": gdr.get("counterfactual", {})},
        "counterfactual": gdr.get("counterfactual", {}),
        "sources": sources[:20],
        "verification": {"canonical_research_sha256": sha256_file(paths["canonical"]), "timeline_input_bundle_sha256": sha256_file(ROOT / "timeline" / "subjects" / f"{key}_timeline_derivation_manifest.json"), "freshness_input_bundle_sha256": freshness["input_bundle_hash"], "freshness_policy_version": freshness["policy_version"], "gdr_authorization_id": gdr["authorization_id"], "correction_status": canonical.get("correction_status", "NONE"), "supersession_status": canonical.get("supersession_status", "CURRENT"), "verify_path": f"verify/reports/ART-{subject.upper()}-PAID-PDF-v0.1.json"},
    }
    bundle["report_content_bundle_sha256"] = content_hash(bundle)
    return bundle
