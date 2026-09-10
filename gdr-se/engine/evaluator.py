from __future__ import annotations

from pathlib import Path

from aggregation import CONFIG_PATH as AGGREGATION_CONFIG_PATH
from aggregation import aggregate, load_rules, public_status
from clock import isoformat_z, normalize_as_of, utc_now
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
RUNTIME_REVISION = "R1.1"


def config_hashes(root: Path = ROOT, aggregation_rules_path: Path | None = None) -> dict[str, str]:
    aggregation_path = aggregation_rules_path or root / "gdr-se" / "config" / "aggregation_rules.json"
    return {
        "gates_config_sha256": sha256_file(root / "gdr-se" / "config" / "gates.json"),
        "freshness_config_sha256": sha256_file(root / "gdr-se" / "config" / "category_freshness.json"),
        "aggregation_rules_sha256": sha256_file(aggregation_path),
        "research_profile_sha256": sha256_file(root / "gdr-se" / "config" / "research_profiles.json"),
    }


def evidence_envelope(context, artifact_metadata: list[dict], record_created_at: str) -> dict:
    by_role = {row["role"]: row for row in artifact_metadata}
    return {
        "envelope_id": f"GDR-SE-ENV-{context.subject}-R1.1",
        "research_id": context.research_id,
        "rtp_manifest_sha256": by_role.get("manifest", {}).get("sha256"),
        "canonical_research_sha256": by_role.get("canonical_research", {}).get("sha256"),
        "report_sha256": by_role.get("report", {}).get("sha256"),
        "source_inventory_sha256": by_role.get("source_inventory", {}).get("sha256"),
        "observation_registry_sha256": by_role.get("observation_registry", {}).get("sha256"),
        "claim_registry_sha256": by_role.get("claim_registry", {}).get("sha256"),
        "counter_evidence_sha256": by_role.get("counter_evidence", {}).get("sha256"),
        "record_created_at": record_created_at,
        "immutable": True,
        "artifacts": artifact_metadata,
    }


def input_bundle_hash(context, artifact_metadata: list[dict], hashes: dict[str, str], evaluation_as_of: str, aggregation_rule_version: str) -> str:
    return canonical_sha256({
        "gdr_se_version": VERSION,
        "runtime_revision": RUNTIME_REVISION,
        "profile": context.profile,
        "research_id": context.research_id,
        "evaluation_as_of": evaluation_as_of,
        "aggregation_rule_version": aggregation_rule_version,
        "artifact_hashes": {row["role"]: row["sha256"] for row in artifact_metadata},
        "config_hashes": hashes,
    })


def evaluate(context, root: Path = ROOT, as_of=None, aggregation_rules_path: Path | None = None) -> Evaluation:
    evaluation_dt = normalize_as_of(as_of)
    evaluation_as_of = isoformat_z(evaluation_dt)
    record_created_at = isoformat_z(utc_now())
    aggregation_path = aggregation_rules_path or AGGREGATION_CONFIG_PATH
    rules = load_rules(aggregation_path)
    hashes = config_hashes(root, aggregation_path)
    g1 = validate_g1_schema(context, root, evaluation_as_of)
    g2, artifact_rows = validate_g2_provenance(context, root, evaluation_as_of)
    gate_results = [
        g1,
        g2,
        validate_g3_freshness(context, evaluation_as_of, evaluation_dt.date()),
        validate_g4_source_dependency(context, root, evaluation_as_of),
        validate_g5_numerical(context, root, evaluation_as_of),
        validate_g6_ecl(context, evaluation_as_of),
        validate_g7_counter_evidence(context, root, evaluation_as_of),
        validate_g8_review(context, root, evaluation_as_of),
        validate_g9_sensitivity(context, evaluation_as_of),
        validate_g10_supersession(context, root, evaluation_as_of),
    ]
    authorization = aggregate(gate_results, rules)
    bundle = input_bundle_hash(context, artifact_rows, hashes, evaluation_as_of, rules["rule_version"])
    return Evaluation(
        evaluation_id=f"GDR-SE-EVAL-{bundle[:16]}-R1.1",
        context=context,
        gate_results=gate_results,
        authorization=authorization,
        public_status=public_status(authorization),
        evaluation_as_of=evaluation_as_of,
        record_created_at=record_created_at,
        aggregation_rule_version=rules["rule_version"],
        input_bundle_sha256=bundle,
        evidence_envelope=evidence_envelope(context, artifact_rows, record_created_at),
        config_hashes=hashes,
        artifact_metadata=artifact_rows,
    )
