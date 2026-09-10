from __future__ import annotations

from pathlib import Path

from aggregation import aggregate, public_status
from integrity import canonical_sha256, sha256_file
from models import Evaluation
from gates import (
    validate_g1_schema,
    validate_g2_provenance,
    validate_g3_freshness,
    validate_g4_source_dependency,
    validate_g5_numerical,
    validate_g6_ecl,
    validate_g7_counter_evidence,
    validate_g8_review,
    validate_g9_sensitivity,
    validate_g10_supersession,
)


ROOT = Path(__file__).resolve().parents[2]
VERSION = "GDR_SE_v0.1"
CREATED_AT = "2026-09-10T00:00:00Z"


def config_hashes(root: Path = ROOT) -> dict[str, str]:
    return {
        "gates_config_sha256": sha256_file(root / "gdr-se" / "config" / "gates.json"),
        "freshness_config_sha256": sha256_file(root / "gdr-se" / "config" / "category_freshness.json"),
        "aggregation_rules_sha256": sha256_file(root / "gdr-se" / "config" / "aggregation_rules.json"),
        "research_profile_sha256": sha256_file(root / "gdr-se" / "config" / "research_profiles.json"),
    }


def evidence_envelope(context, artifact_metadata: list[dict]) -> dict:
    by_role = {row["role"]: row for row in artifact_metadata}
    return {
        "envelope_id": f"GDR-SE-ENV-{context.subject}-R1",
        "research_id": context.research_id,
        "rtp_manifest_sha256": by_role.get("manifest", {}).get("sha256"),
        "canonical_research_sha256": by_role.get("canonical_research", {}).get("sha256"),
        "report_sha256": by_role.get("report", {}).get("sha256"),
        "source_inventory_sha256": by_role.get("source_inventory", {}).get("sha256"),
        "observation_registry_sha256": by_role.get("observation_registry", {}).get("sha256"),
        "claim_registry_sha256": by_role.get("claim_registry", {}).get("sha256"),
        "counter_evidence_sha256": by_role.get("counter_evidence", {}).get("sha256"),
        "created_at": CREATED_AT,
        "immutable": True,
        "artifacts": artifact_metadata,
    }


def input_bundle_hash(context, artifact_metadata: list[dict], hashes: dict[str, str]) -> str:
    return canonical_sha256({
        "gdr_se_version": VERSION,
        "profile": context.profile,
        "research_id": context.research_id,
        "artifact_hashes": {row["role"]: row["sha256"] for row in artifact_metadata},
        "config_hashes": hashes,
    })


def evaluate(context, root: Path = ROOT) -> Evaluation:
    g1 = validate_g1_schema(context, root, CREATED_AT)
    g2, artifact_rows = validate_g2_provenance(context, root, CREATED_AT)
    gate_results = [
        g1,
        g2,
        validate_g3_freshness(context, CREATED_AT),
        validate_g4_source_dependency(context, root, CREATED_AT),
        validate_g5_numerical(context, root, CREATED_AT),
        validate_g6_ecl(context, CREATED_AT),
        validate_g7_counter_evidence(context, root, CREATED_AT),
        validate_g8_review(context, root, CREATED_AT),
        validate_g9_sensitivity(context, CREATED_AT),
        validate_g10_supersession(context, root, CREATED_AT),
    ]
    authorization = aggregate(gate_results)
    hashes = config_hashes(root)
    bundle = input_bundle_hash(context, artifact_rows, hashes)
    return Evaluation(
        evaluation_id=f"GDR-SE-EVAL-{bundle[:16]}-R1",
        context=context,
        gate_results=gate_results,
        authorization=authorization,
        public_status=public_status(authorization),
        input_bundle_sha256=bundle,
        evidence_envelope=evidence_envelope(context, artifact_rows),
        config_hashes=hashes,
        artifact_metadata=artifact_rows,
    )
