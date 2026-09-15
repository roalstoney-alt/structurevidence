"""Map CML records into shared GDR-SE release facts without creating a new gate."""

from __future__ import annotations


PRIMARY_LIFECYCLE_TYPES = {
    "MANUFACTURER_PCN_MIRROR",
    "MANUFACTURER_DISCONTINUANCE_NOTICE",
    "MANUFACTURER_LIFECYCLE_INDEX",
    "MANUFACTURER_DATASHEET",
    "MANUFACTURER_PRODUCT_PAGE",
}


def facts_for(record: dict, source_register: dict) -> dict:
    cml = record["cml"]
    sources = source_register.get("sources", [])
    primary_lifecycle = any(source.get("source_type") in PRIMARY_LIFECYCLE_TYPES for source in sources)
    unresolved = len(cml.get("evidence", {}).get("unknowns", []))
    private_safe = cml.get("public_private_boundary") == "PUBLIC_EVIDENCE_ONLY_NO_CLIENT_BOM"
    untested = cml.get("verification", {}).get("qualification_state") in {
        "NOT_ASSESSED",
        "PAPER_SCREENING",
        "PAPER_COMPATIBLE_WITH_UNKNOWNS",
        "LAB_VERIFICATION_REQUIRED",
        "LAB_TESTING",
    }
    return {
        "domain": "TECHNICAL_RISK",
        "protocol": "CML",
        "primary_source_coverage": "PRESENT" if primary_lifecycle else "MISSING",
        "counter_evidence": "PRESENT" if cml.get("counter_evidence") else "MISSING",
        "critical_unknown_count": unresolved,
        "qualification_state": cml.get("verification", {}).get("qualification_state"),
        "untested_candidate_boundary": untested,
        "public_private_boundary": "PASS" if private_safe else "FAIL",
        "freshness_state": cml.get("freshness_state"),
        "correction_status": record["core"].get("correction_status"),
        "supersession_status": record["core"].get("supersession_status"),
    }


def release_effect(record: dict, source_register: dict) -> dict:
    facts = facts_for(record, source_register)
    hard_block = facts["primary_source_coverage"] == "MISSING" or facts["public_private_boundary"] == "FAIL" or facts["supersession_status"] == "SUPERSEDED"
    return {
        "adapter_version": "GDR_SE_CML_DOMAIN_ADAPTER_v0.1",
        "public_release": "BLOCK" if hard_block else "ALLOW_WITH_LIMITATIONS",
        "paid_delivery": "BLOCK",
        "reason": "CML v0.1 is public-method-pilot and request-only; qualification unknowns remain explicit.",
        "facts": facts,
    }
