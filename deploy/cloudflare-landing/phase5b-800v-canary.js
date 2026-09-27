// Derived projection only. The canonical source remains CML-PDRE-001/pdre-record.json.
export const PHASE5B_800V_INVENTORY = Object.freeze({
  schema_version: "SE_DECISION_INVENTORY_v0.1",
  event_id: "SE-EVENT-800001",
  canonical_record_id: "SE.CML.PDRE.CML-PDRE-001.PDRE-001A.v0.1",
  canonical_record_hash: "c9fa8c3a6d3f6601412b28ad38f7e94337ff5e69e7ba07ca9a5f75523a54e096",
  title: "54V in-rack distribution to 800VDC sidecar / power rack",
  readiness: { code: "R3", name: "SAMPLE_BENCH_TESTED", interpretation: "TECHNICALLY_CREDIBLE", evidence_refs: ["EV-003", "EV-004"], supports_company_structural_assessment: false, limitations: ["Authorized by CML-PDRE-001-EVP-001.", "R4 through R7 are not established."] },
  as_of: "2026-09-17T00:00:00Z",
  primary_gap: "OPERATING_HISTORY",
  interpretation: "RECORDED_EVIDENCE_STATE_NOT_ADVICE_OR_GUARANTEE",
  dimensions: Object.freeze([
    { dimension_id: "FIELD_DEPLOYMENT", current_state: "NOT_ESTABLISHED", as_of: "2026-09-17T00:00:00Z", why: "No approved field-operation evidence; forward timing is counter-evidence.", qualifying_records_count: 0, linked_records_count: 3, counter_records_count: 2, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: ["EV-005", "EV-006", "EV-007"] },
    { dimension_id: "OPERATING_HISTORY", current_state: "UNKNOWN", as_of: "2026-09-17T00:00:00Z", why: "No duration, failure-rate, maintenance, or operating-history evidence is approved.", qualifying_records_count: 0, linked_records_count: 0, counter_records_count: 0, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: [] },
    { dimension_id: "REPLICATION", current_state: "NOT_ESTABLISHED", as_of: "2026-09-17T00:00:00Z", why: "Coordination and a specification do not establish multi-user or multi-OEM replication.", qualifying_records_count: 0, linked_records_count: 1, counter_records_count: 0, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: ["EV-005"] },
    { dimension_id: "INDEPENDENT_VALIDATION", current_state: "UNKNOWN", as_of: "2026-09-17T00:00:00Z", why: "Performance, copper, rack-space, and efficiency claims are not independently validated.", qualifying_records_count: 0, linked_records_count: 0, counter_records_count: 0, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: [] },
    { dimension_id: "ECONOMICS", current_state: "UNKNOWN", as_of: "2026-09-17T00:00:00Z", why: "CAPEX, ROI, payback, reliability, and service economics are not calculable.", qualifying_records_count: 0, linked_records_count: 5, counter_records_count: 0, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: ["EV-003", "EV-005", "EV-002", "EV-006", "EV-007"] },
    { dimension_id: "CONTEXT_FIT", current_state: "UNKNOWN", as_of: "2026-09-17T00:00:00Z", why: "No private decision context, jurisdiction, system boundary, or requirements were supplied.", qualifying_records_count: 0, linked_records_count: 0, counter_records_count: 0, unknown_count: 1, verification_available: true, last_change_at: "2026-09-17T00:00:00Z", evidence_refs: [] },
  ]),
});
