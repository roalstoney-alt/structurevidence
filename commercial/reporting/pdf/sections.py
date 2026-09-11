from __future__ import annotations


REQUIRED_SECTIONS = [
    "Cover",
    "Executive Summary",
    "Research Scope",
    "Current Structural State",
    "Structural Level / Delta",
    "Freshness Status",
    "Evidence Dynamics",
    "Material Events",
    "ECL Evidence Consistency",
    "Counter-Evidence",
    "Numerical Reconciliation",
    "Source Dependency / Coverage",
    "GDR-SE Authorization",
    "What Could Change This Conclusion",
    "Limitations",
    "Verification Record",
    "Appendix / Source Index",
]


def section_lines(bundle: dict, draft: bool) -> list[tuple[str, list[str]]]:
    gdr = bundle["gdr_snapshot"]
    freshness = bundle["freshness_snapshot"]
    falsifiers = bundle.get("counterfactual", {}).get("falsifiers") or gdr.get("counterfactual", {}).get("falsifiers", [])
    sources = bundle.get("sources", [])
    return [
        ("Cover", [
            "StructEvidence",
            "Verified Research Report",
            f"Subject: {bundle['subject_id']}",
            f"Research ID: {bundle['research_id']}",
            f"Report ID: {bundle['report_id']}",
            f"Report Version: {bundle['report_version']}",
            f"Evaluation As-Of: {bundle['evaluation_as_of']}",
            f"Freshness Policy Version: {freshness['policy_version']}",
            f"GDR-SE Authorization ID: {gdr['authorization_id']}",
            f"Generated At: {bundle['generated_at']}",
            "Research only. No investment advice.",
            "DRAFT - NOT FOR DELIVERY" if draft else "FINAL_DELIVERABLE",
        ]),
        ("Executive Summary", [
            f"Current research finding: {bundle['research_snapshot'].get('finding')}",
            "What changed: this report is generated from structured current research, Timeline, RDL Freshness and GDR-SE artifacts.",
            f"Freshness status: {freshness['release_freshness']}.",
            "Supporting evidence is summarized in the evidence and source sections.",
        ]),
        ("Research Scope", [f"Product SKU: {bundle['product_sku']}", "This report is research only and does not provide investment advice, ratings, trading signals, or price targets."]),
        ("Current Structural State", [str(bundle["timeline_snapshot"].get("current_structural_state"))]),
        ("Structural Level / Delta", [*[f"Level: {row.get('dimension_id')} -> {row.get('freshness_state') or row.get('state')}" for row in freshness.get("level_freshness", [])[:8]], *[f"Delta: {row.get('dimension_id')} -> {row.get('freshness_state') or row.get('state')}" for row in freshness.get("delta_freshness", [])[:8]]]),
        ("Freshness Status", [f"Release Freshness: {freshness['release_freshness']}", f"Next Refresh Reason: {freshness.get('next_refresh_reason')}", *[f"Critical Evidence: {row.get('family_id')} -> {row.get('freshness_state')}" for row in freshness.get("critical_evidence_freshness", [])]]),
        ("Evidence Dynamics", [*[f"{row.get('family_id')}: {row.get('freshness_state')} / {row.get('criticality')} / last update {row.get('last_update_at')}" for row in freshness.get("critical_evidence_freshness", [])], "Freshness does not equal truth; it only describes currentness of the supporting evidence process."]),
        ("Material Events", [*[f"{row.get('event_id')}: {row.get('label') or row.get('event_type')} [{row.get('event_domain')}]" for row in bundle["timeline_snapshot"].get("events", [])], "No unsupported interpolation is used for sparse structural dynamics."]),
        ("ECL Evidence Consistency", [f"Evidence state: {bundle['ecl_snapshot'].get('evidence_state')}", str(bundle['ecl_snapshot'].get('finding'))]),
        ("Counter-Evidence", [str(item) for item in falsifiers] or ["No falsifier list was available in the bundle."]),
        ("Numerical Reconciliation", ["Numerical reconciliation is included where applicable in the canonical research bundle and GDR-SE gate table."]),
        ("Source Dependency / Coverage", ["Multiple URLs are not treated as independent sources. Hosting, authorship and observation independence are evaluated separately where material."]),
        ("GDR-SE Authorization", [f"Authorization: {gdr['authorization']}", f"Authorization ID: {gdr['authorization_id']}", f"Evaluation As-Of: {gdr['evaluation_as_of']}"]),
        ("What Could Change This Conclusion", [bundle.get("counterfactual", {}).get("what_could_change", "New primary evidence, correction, supersession, source retraction or material event could change this conclusion."), *[str(item) for item in falsifiers]]),
        ("Limitations", ["Research only", "No investment advice", "Freshness does not equal truth", "Evidence inconsistency does not imply fraud", "Currentness may change after new events"]),
        ("Verification Record", [f"Artifact ID: {bundle['artifact_id']}", "PDF SHA-256: RECORDED_AFTER_RENDER", f"Canonical research SHA-256: {bundle['verification'].get('canonical_research_sha256')}", f"Timeline input bundle SHA-256: {bundle['verification'].get('timeline_input_bundle_sha256')}", f"Freshness input bundle SHA-256: {bundle['verification'].get('freshness_input_bundle_sha256')}", f"Freshness policy version: {bundle['verification'].get('freshness_policy_version')}", f"GDR-SE authorization record ID: {bundle['verification'].get('gdr_authorization_id')}", f"Correction status: {bundle['verification'].get('correction_status')}", f"Supersession status: {bundle['verification'].get('supersession_status')}", f"Verify path: {bundle['verification'].get('verify_path')}"]),
        ("Appendix / Source Index", [f"[{i}] {src.get('source_id') or 'S'+str(i)} | {src.get('title') or src.get('source_title') or 'Untitled source'} | {src.get('source_class') or src.get('source_type') or 'UNCLASSIFIED'} | {src.get('capture_date') or src.get('retrieved_at') or 'N/A'} | {src.get('dependency_group') or 'N/A'} | {src.get('artifact_class') or 'N/A'}" for i, src in enumerate(sources, 1)]),
    ]
