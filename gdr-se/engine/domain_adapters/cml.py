"""Map CML records into shared GDR-SE release facts without creating a new gate."""

from __future__ import annotations


PRIMARY_LIFECYCLE_TYPES = {
    "MANUFACTURER_PCN_MIRROR",
    "MANUFACTURER_DISCONTINUANCE_NOTICE",
    "MANUFACTURER_LIFECYCLE_INDEX",
    "MANUFACTURER_DATASHEET",
    "MANUFACTURER_PRODUCT_PAGE",
}
PRIVATE_KEYS = {
    "customer_bom", "annual_usage", "inventory", "customer_pricing", "supplier_quotation",
    "customer_drawings", "customer_firmware", "customer_qualification_limits", "nda_documents",
    "revenue_exposure", "private_lab_raw_data",
    "internal_failure_data",
}
UNCERTAIN_QUALIFICATION_STATES = {
    "NOT_ASSESSED", "PAPER_SCREENING", "PAPER_COMPATIBLE_WITH_UNKNOWNS",
    "LAB_VERIFICATION_REQUIRED", "LAB_TESTING",
}


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_keys(item) for item in value.values()), set())
    if isinstance(value, list):
        return set().union(*(_keys(item) for item in value), set())
    return set()


def facts_for(record: dict, source_register: dict) -> dict:
    cml = record["cml"]
    sources = source_register.get("sources", [])
    primary_lifecycle = any(source.get("source_type") in PRIMARY_LIFECYCLE_TYPES for source in sources)
    unresolved = len(cml.get("evidence", {}).get("unknowns", []))
    private_fields = sorted(_keys(record) & PRIVATE_KEYS)
    private_safe = cml.get("public_private_boundary") == "PUBLIC_EVIDENCE_ONLY_NO_CLIENT_BOM" and not private_fields
    qualification_state = cml.get("verification", {}).get("qualification_state")
    untested = qualification_state in UNCERTAIN_QUALIFICATION_STATES
    unverified_dropin = any(candidate.get("relationship_type") == "DROP_IN" for candidate in cml.get("alternative", {}).get("candidates", [])) and untested
    return {
        "domain": "TECHNICAL_RISK",
        "protocol": "CML",
        "primary_source_coverage": "PRESENT" if primary_lifecycle else "MISSING",
        "counter_evidence": "PRESENT" if cml.get("counter_evidence") else "MISSING",
        "critical_unknown_count": unresolved,
        "qualification_state": qualification_state,
        "untested_candidate_boundary": untested,
        "unverified_dropin": unverified_dropin,
        "public_private_boundary": "PASS" if private_safe else "FAIL",
        "private_fields_detected": private_fields,
        "freshness_state": cml.get("freshness_state"),
        "freshness_reason": cml.get("freshness_reason"),
        "correction_status": record["core"].get("correction_status"),
        "supersession_status": record["core"].get("supersession_status"),
        "product_context": cml.get("product_context"),
    }


def release_effect(record: dict, source_register: dict) -> dict:
    facts = facts_for(record, source_register)
    hard_reasons = []
    if facts["primary_source_coverage"] == "MISSING":
        hard_reasons.append("PRIMARY_SOURCE_MISSING")
    if facts["public_private_boundary"] == "FAIL":
        hard_reasons.append("PRIVATE_BOUNDARY_FAIL")
    if facts["supersession_status"] == "SUPERSEDED":
        hard_reasons.append("SUPERSEDED")
    if facts["freshness_state"] == "EVENT_INVALIDATED":
        hard_reasons.append("EVENT_INVALIDATED")
    if facts["correction_status"] in {"MATERIAL_CORRECTION_OPEN", "CORRECTION_UNDER_REVIEW_MATERIAL"}:
        hard_reasons.append("CORRECTION_UNDER_REVIEW_MATERIAL")
    if facts["counter_evidence"] == "MISSING":
        hard_reasons.append("COUNTER_EVIDENCE_MISSING")
    if facts["unverified_dropin"]:
        hard_reasons.append("UNVERIFIED_DROP_IN")
    if facts["freshness_state"] in {"POLICY_NOT_CONFIGURED", "INSUFFICIENT_DATA"} and facts["product_context"] != "PUBLIC_TECHNICAL_RECORD":
        hard_reasons.append("FRESHNESS_NOT_AUTHORIZED_FOR_PRODUCT_CONTEXT")
    public_release = "BLOCK" if hard_reasons else "ALLOW_WITH_LIMITATIONS"
    return {
        "adapter_version": "GDR_SE_CML_DOMAIN_ADAPTER_v0.1a",
        "public_release": public_release,
        "paid_delivery": "BLOCK",
        "reason": ",".join(hard_reasons) if hard_reasons else "PUBLIC_METHOD_PILOT_WITH_EXPLICIT_LIMITATIONS",
        "hard_block_reasons": hard_reasons,
        "facts": facts,
    }
