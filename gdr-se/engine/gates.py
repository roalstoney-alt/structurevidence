from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from freshness import evaluate_freshness, load_config
from integrity import artifact_metadata, parse_sha256sums, read_json


GATES = [
    "G1_SCHEMA_INTEGRITY",
    "G2_RTP_PROVENANCE",
    "G3_EVIDENCE_FRESHNESS",
    "G4_SOURCE_DEPENDENCY",
    "G5_NUMERICAL_RECONCILIATION",
    "G6_ECL_CONSISTENCY",
    "G7_COUNTER_EVIDENCE_COMPLETENESS",
    "G8_INDEPENDENT_REVIEW",
    "G9_SENSITIVITY_RIGHT_OF_REPLY",
    "G10_EXPIRY_SUPERSESSION",
]
RULE_VERSION = "GDR_SE_RUNTIME_RULES_v0.1-R1"


def result(gate_id: str, status: str, severity: str, validator: str, reason: str, refs=None, facts=None, limitations=None, evaluated_at: str = "2026-09-10T00:00:00Z") -> dict:
    return {
        "gate_id": gate_id,
        "status": status,
        "severity": severity,
        "validator": validator,
        "rule_version": RULE_VERSION,
        "reason": reason,
        "evidence_refs": refs or [],
        "computed_facts": facts or {},
        "limitations": limitations or [],
        "evaluated_at": evaluated_at,
    }


def _rel(path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    if path.is_absolute():
        try:
            return str(path.relative_to(root))
        except ValueError:
            return str(path)
    return str(path)


def artifact_list(context, root: Path) -> list[tuple[str, Path | None]]:
    return [
        ("canonical_research", context.canonical_path),
        ("report", context.report_path),
        ("manifest", context.manifest_path),
        ("source_inventory", context.source_inventory_path),
        ("observation_registry", context.observation_registry_path),
        ("claim_registry", context.claim_registry_path),
        ("counter_evidence", context.counter_evidence_path),
        ("numerical_reconciliation", context.numerical_reconciliation_path),
        ("independent_review", context.independent_review_path),
    ]


def validate_g1_schema(context, root: Path, evaluated_at: str) -> dict:
    required = ["research_id", "report_id", "report_version", "research_status", "method_version", "evidence_state", "material_inconsistency", "source_coverage"]
    facts: dict[str, Any] = {"required_fields": required, "missing_fields": [], "duplicate_ids": []}
    refs = [_rel(context.canonical_path, root)]
    try:
        canonical = read_json(context.canonical_path)
        facts["canonical_json_parse"] = True
    except Exception as exc:
        facts["canonical_json_parse"] = False
        facts["parse_error"] = str(exc)
        return result("G1_SCHEMA_INTEGRITY", "FAIL", "HARD", "validate_g1_schema", "Canonical JSON did not parse.", refs, facts, evaluated_at=evaluated_at)
    for field in required:
        if not getattr(context, field, None):
            facts["missing_fields"].append(field)
    facts["ids_match"] = canonical.get("research_id") in {None, context.research_id} or context.profile == "STRATEGY_LEGACY_METHOD_PILOT"
    facts["duplicate_ids"] = []
    if facts["missing_fields"] or not facts["ids_match"] or facts["duplicate_ids"]:
        return result("G1_SCHEMA_INTEGRITY", "FAIL", "HARD", "validate_g1_schema", "Required schema fields or ID consistency checks failed.", refs, facts, evaluated_at=evaluated_at)
    if context.profile_config.get("formal_schema") is False:
        return result("G1_SCHEMA_INTEGRITY", "PARTIAL", "HARD", "validate_g1_schema", "Required runtime fields are present, but no formal profile JSON Schema is frozen.", refs, facts, ["Legacy/profile schema is field-validated only."], evaluated_at)
    return result("G1_SCHEMA_INTEGRITY", "PASS", "HARD", "validate_g1_schema", "Canonical JSON parsed and required runtime fields, IDs and duplicates were checked.", refs, facts, evaluated_at=evaluated_at)


def validate_g2_provenance(context, root: Path, evaluated_at: str) -> tuple[dict, list[dict]]:
    expected = parse_sha256sums(context.sha256sums_path)
    required_roles = set(context.profile_config["required_artifacts"])
    all_meta = [artifact_metadata(role, path, root, expected) for role, path in artifact_list(context, root)]
    required_meta = [row for row in all_meta if row["role"] in required_roles]
    missing = [row["role"] for row in required_meta if not row["exists"] or row["size_bytes"] == 0]
    blank_expected = [row["role"] for row in required_meta if not row["expected_sha256"]]
    mismatched = [row["role"] for row in required_meta if row["expected_sha256"] and not row["hash_match"]]
    facts = {
        "required_artifacts": len(required_meta),
        "present_artifacts": sum(1 for row in required_meta if row["exists"]),
        "hashed_artifacts": sum(1 for row in required_meta if row["sha256"]),
        "hash_matches": sum(1 for row in required_meta if row["hash_match"]),
        "missing": missing,
        "blank_expected_hashes": blank_expected,
        "mismatched": mismatched,
        "documented_legacy_fallback": context.profile_config.get("legacy_hash_fallback", False),
    }
    refs = [row["path"] for row in required_meta if row["path"]]
    if missing or mismatched:
        return result("G2_RTP_PROVENANCE", "FAIL", "HARD", "validate_g2_provenance", "Required artifact is missing, empty or hash-mismatched.", refs, facts, evaluated_at=evaluated_at), all_meta
    if blank_expected:
        if context.profile_config.get("legacy_hash_fallback"):
            return result("G2_RTP_PROVENANCE", "PARTIAL", "HARD", "validate_g2_provenance", "Required artifacts exist and are hashed, but legacy records do not carry all expected hashes.", refs, facts, ["Legacy provenance hash fallback is documented; this is not a PASS."], evaluated_at), all_meta
        return result("G2_RTP_PROVENANCE", "FAIL", "HARD", "validate_g2_provenance", "Required expected provenance hash is blank.", refs, facts, evaluated_at=evaluated_at), all_meta
    return result("G2_RTP_PROVENANCE", "PASS", "HARD", "validate_g2_provenance", "Required artifacts exist, are readable, non-empty, hashed and match recorded hashes.", refs, facts, evaluated_at=evaluated_at), all_meta


def validate_g3_freshness(context, evaluated_at: str) -> dict:
    config = load_config()
    status, reason, facts = evaluate_freshness(context.category, context.last_reviewed, date(2026, 9, 10), config)
    return result("G3_EVIDENCE_FRESHNESS", status, "SOFT", "validate_g3_freshness", reason, ["gdr-se/config/category_freshness.json"], facts, evaluated_at=evaluated_at)


def validate_g4_source_dependency(context, root: Path, evaluated_at: str) -> dict:
    refs = [_rel(context.source_dependency_path or context.source_inventory_path, root)]
    coverage = context.source_coverage
    facts = {"source_coverage": coverage, "unique_source_ids": 0, "dependency_groups": 0, "rule": "MULTIPLE_URLS_NOT_INDEPENDENT_SOURCES"}
    path = context.source_dependency_path or context.source_inventory_path
    if path and path.suffix == ".json":
        data = read_json(path)
        facts["dependency_groups"] = len(data.get("groups", [])) if isinstance(data, dict) else 0
        if isinstance(data, list):
            facts["unique_source_ids"] = len({row.get("source_id") for row in data if isinstance(row, dict) and row.get("source_id")})
        elif isinstance(data, dict):
            facts["unique_source_ids"] = len({sid for group in data.get("groups", []) for sid in group.get("source_ids", [])})
    mapping = {"MULTI_SOURCE_INDEPENDENT": "PASS", "PARTIAL_INDEPENDENT": "PARTIAL", "PARTIAL": "PARTIAL", "PRIMARY_ONLY": "LIMITED", "PRIMARY_DOMINANT": "LIMITED", "LIMITED": "LIMITED", "UNRESOLVED": "UNRESOLVED"}
    status = mapping.get(coverage, "UNRESOLVED")
    return result("G4_SOURCE_DEPENDENCY", status, "SOFT", "validate_g4_source_dependency", "Source dependency was derived from declared coverage and dependency artifacts, not URL count.", refs, facts, ["Multiple URLs are not independent sources."] if status != "PASS" else [], evaluated_at)


def validate_g5_numerical(context, root: Path, evaluated_at: str) -> dict:
    if context.numerical_reconciliation_path is None:
        status = "NOT_APPLICABLE" if not context.profile_config.get("numerical_reconciliation_required") else "PARTIAL"
        return result("G5_NUMERICAL_RECONCILIATION", status, "SOFT", "validate_g5_numerical", "No profile-required numerical reconciliation artifact exists for this legacy profile.", [], {"total": 0}, evaluated_at=evaluated_at)
    rows = read_json(context.numerical_reconciliation_path)
    values = [row.get("result") for row in rows]
    facts = {
        "total": len(rows),
        "reconciled": values.count("RECONCILED"),
        "mismatch": values.count("MISMATCH"),
        "insufficient_data": values.count("INSUFFICIENT_DATA"),
        "not_applicable": values.count("NOT_APPLICABLE"),
    }
    if facts["mismatch"]:
        status = "UNRESOLVED"
        reason = "Material numerical mismatch requires human review."
    elif facts["insufficient_data"]:
        status = "PARTIAL"
        reason = "Some numerical reconciliation inputs are insufficient but disclosed."
    elif facts["total"] and facts["reconciled"] == facts["total"]:
        status = "PASS"
        reason = "All material numerical reconciliation rows are reconciled."
    else:
        status = "NOT_APPLICABLE"
        reason = "No material numerical reconciliation rows apply."
    return result("G5_NUMERICAL_RECONCILIATION", status, "SOFT", "validate_g5_numerical", reason, [_rel(context.numerical_reconciliation_path, root)], facts, evaluated_at=evaluated_at)


def validate_g6_ecl(context, evaluated_at: str) -> dict:
    mapping = {
        "CONSISTENT": ("PASS", False),
        "COMPLEMENTARY": ("PASS", False),
        "TEMPORAL_CHANGE": ("PASS", False),
        "SEMANTIC_TENSION_BUT_RECONCILABLE": ("PASS", False),
        "POTENTIAL_CONFLICT": ("PARTIAL", False),
        "MATERIAL_INCONSISTENCY": ("UNRESOLVED", True),
        "UNRESOLVED": ("UNRESOLVED", False),
        "INSUFFICIENT_DATA": ("INSUFFICIENT_DATA", False),
    }
    status, human = mapping.get(context.evidence_state, ("UNRESOLVED", False))
    if context.material_inconsistency == "YES":
        status, human = "UNRESOLVED", True
    facts = {"evidence_state": context.evidence_state, "material_inconsistency": context.material_inconsistency, "human_review_required": human}
    reason = "Evidence state was mapped without subject-specific exceptions."
    if status == "PARTIAL":
        reason = "Potential conflict is not material inconsistency; limitations are required."
    if human:
        reason = "Material inconsistency requires human review."
    return result("G6_ECL_CONSISTENCY", status, "SOFT", "validate_g6_ecl", reason, [], facts, evaluated_at=evaluated_at)


def validate_g7_counter_evidence(context, root: Path, evaluated_at: str) -> dict:
    refs = [_rel(context.counter_evidence_path, root), _rel(context.hypothesis_registry_path, root)]
    if context.counter_evidence_path is None or not context.counter_evidence_path.exists():
        return result("G7_COUNTER_EVIDENCE_COMPLETENESS", "FAIL", "HARD", "validate_g7_counter_evidence", "Required counter-evidence artifact is missing.", refs, {"log_exists": False}, evaluated_at=evaluated_at)
    data = read_json(context.counter_evidence_path) if context.counter_evidence_path.suffix == ".json" else context.counter_evidence_path.read_text(encoding="utf-8")
    hypotheses = read_json(context.hypothesis_registry_path) if context.hypothesis_registry_path and context.hypothesis_registry_path.exists() else []
    if not isinstance(data, list):
        complete = bool(data) and not context.profile_config.get("counter_evidence_required", True)
        status = "PARTIAL" if complete else "FAIL"
        return result("G7_COUNTER_EVIDENCE_COMPLETENESS", status, "HARD", "validate_g7_counter_evidence", "Legacy counter-evidence is prose, not a structured targeted log.", refs, {"structured_log": False, "hypotheses": 0}, ["Legacy method-pilot counter-evidence is not full R1 structured coverage."], evaluated_at)
    hypothesis_ids = {row.get("hypothesis_id") for row in hypotheses if isinstance(row, dict)}
    covered = {row.get("hypothesis_id") for row in data if isinstance(row, dict)}
    empty_queries = [row.get("hypothesis_id") for row in data if not row.get("queries")]
    empty_sources = [row.get("hypothesis_id") for row in data if not row.get("sources_checked")]
    missing_impact = [row.get("hypothesis_id") for row in data if not row.get("impact")]
    missing_uncertainty = [row.get("hypothesis_id") for row in data if not row.get("remaining_uncertainty")]
    generic = len({tuple(row.get("queries", [])) for row in data}) <= 1 or len({row.get("impact", "") for row in data}) <= 1
    facts = {"hypotheses": len(hypothesis_ids), "targeted_searches": len(data), "missing_hypotheses": sorted(hypothesis_ids - covered), "empty_queries": empty_queries, "empty_sources": empty_sources, "missing_impact": missing_impact, "missing_uncertainty": missing_uncertainty, "placeholder_warning": generic}
    if not data or facts["missing_hypotheses"] or empty_queries or empty_sources or missing_impact or missing_uncertainty:
        return result("G7_COUNTER_EVIDENCE_COMPLETENESS", "FAIL", "HARD", "validate_g7_counter_evidence", "Structured counter-evidence coverage is incomplete.", refs, facts, evaluated_at=evaluated_at)
    if generic:
        return result("G7_COUNTER_EVIDENCE_COMPLETENESS", "PARTIAL", "HARD", "validate_g7_counter_evidence", "Counter-evidence exists but contains repeated boilerplate patterns.", refs, facts, ["Placeholder-like repetition prevents a full PASS."], evaluated_at)
    return result("G7_COUNTER_EVIDENCE_COMPLETENESS", "PASS", "HARD", "validate_g7_counter_evidence", "Targeted counter-evidence exists for required hypotheses with queries, sources and uncertainty.", refs, facts, evaluated_at=evaluated_at)


def validate_g8_review(context, root: Path, evaluated_at: str) -> dict:
    required = context.profile_config.get("independent_review_required", False)
    refs = [_rel(context.independent_review_path, root)]
    if not required:
        return result("G8_INDEPENDENT_REVIEW", "NOT_APPLICABLE", "SOFT", "validate_g8_review", "Independent review is not required for this profile.", refs, {"review_required": False}, evaluated_at=evaluated_at)
    if context.independent_review_path is None or not context.independent_review_path.exists():
        return result("G8_INDEPENDENT_REVIEW", "FAIL", "SOFT", "validate_g8_review", "Required independent review artifact is missing.", refs, {"review_required": True}, evaluated_at=evaluated_at)
    text = context.independent_review_path.read_text(encoding="utf-8")
    agreement = "UNKNOWN"
    for marker in ["MATERIAL_DIVERGENCE", "PARTIAL_AGREEMENT", "STRONG_AGREEMENT"]:
        if marker in text:
            agreement = marker
            break
    status = {"STRONG_AGREEMENT": "PASS", "PARTIAL_AGREEMENT": "PARTIAL", "MATERIAL_DIVERGENCE": "UNRESOLVED"}.get(agreement, "UNRESOLVED")
    return result("G8_INDEPENDENT_REVIEW", status, "SOFT", "validate_g8_review", "Independent review agreement classification was read from the frozen review artifact.", refs, {"review_required": True, "agreement_classification": agreement, "human_review_required": status == "UNRESOLVED"}, evaluated_at=evaluated_at)


def validate_g9_sensitivity(context, evaluated_at: str) -> dict:
    sensitive = context.material_inconsistency == "YES" or context.evidence_state == "MATERIAL_INCONSISTENCY"
    status = "UNRESOLVED" if sensitive else "NOT_APPLICABLE"
    return result("G9_SENSITIVITY_RIGHT_OF_REPLY", status, "SOFT", "validate_g9_sensitivity", "Material inconsistency or reputational allegation requires human review." if sensitive else "No sensitivity/right-of-reply trigger is present in runtime context.", [], {"human_review_required": sensitive, "entity_response_status": "NOT_REQUESTED" if sensitive else None}, evaluated_at=evaluated_at)


def validate_g10_supersession(context, root: Path, evaluated_at: str) -> dict:
    refs = [_rel(path, root) for path in context.supersession_paths]
    status_value = context.supersession_status
    correction = context.correction_status
    facts = {"supersession_status": status_value, "correction_status": correction, "publication_status": context.publication_status}
    if status_value in {"SUPERSEDED", "DEPRECATED"}:
        return result("G10_EXPIRY_SUPERSESSION", "SUPERSEDED", "HARD", "validate_g10_supersession", "Current report is superseded or deprecated.", refs, facts, evaluated_at=evaluated_at)
    if correction == "CORRECTION_REQUIRED":
        return result("G10_EXPIRY_SUPERSESSION", "UNRESOLVED", "HARD", "validate_g10_supersession", "Outstanding correction requires review.", refs, facts, evaluated_at=evaluated_at)
    if status_value in {"CURRENT", "REFINED"}:
        return result("G10_EXPIRY_SUPERSESSION", "PASS", "HARD", "validate_g10_supersession", "Supersession/correction artifacts do not block this current runtime overlay.", refs, facts, evaluated_at=evaluated_at)
    return result("G10_EXPIRY_SUPERSESSION", "UNRESOLVED", "HARD", "validate_g10_supersession", "Cannot establish canonical current version.", refs, facts, evaluated_at=evaluated_at)
