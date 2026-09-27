// Read-only bundle adapter for canonical JSONL sources that Cloudflare Workers
// cannot load from the filesystem at runtime. Tests require exact parity with
// the source JSONL; this module never mutates or supersedes canonical records.
export const BUNDLED_TEMPORAL_TIMELINE = Object.freeze([
  { event_id: "CML-PDRE-001-TL-0002", event: "SOURCE_REPORTED_ENGINEERING_DEMONSTRATION", effective_at: "2025-05-20", known_at: "2026-09-17", evidence_refs: ["EV-001"], limitations: ["Source-reported exhibition; not field deployment."] },
  { event_id: "CML-PDRE-001-TL-0003", event: "SOURCE_REPORTED_ALTERNATIVE_PATH", effective_at: "2026-03-02", known_at: "2026-09-17", evidence_refs: ["EV-002"], limitations: ["White-paper claims remain source-attributed."] },
  { event_id: "CML-PDRE-001-TL-0004", event: "SOURCE_REPORTED_PRODUCT_DEMONSTRATION", effective_at: "2026-03-16", known_at: "2026-09-17", evidence_refs: ["EV-003"], limitations: ["Claimed efficiency is not independently verified."] },
  { event_id: "CML-PDRE-001-TL-0005", event: "SOURCE_REPORTED_SAMPLE_BENCH_TEST", effective_at: "2026-05", known_at: "2026-09-17", evidence_refs: ["EV-004"], limitations: ["Source date has month precision; no day is inferred."] },
  { event_id: "CML-PDRE-001-TL-0006", event: "SOURCE_REPORTED_STANDARDIZATION", effective_at: "2026-08-11", known_at: "2026-09-17", evidence_refs: ["EV-005"], limitations: ["Standardization and ecosystem coordination do not establish field deployment."] },
  { event_id: "CML-PDRE-001-TL-0007", event: "SOURCE_REPORTED_FORWARD_PRODUCT_TIMING", effective_at: "2026-08-11", known_at: "2026-09-17", evidence_refs: ["EV-006"], limitations: ["Forward-looking timing bounds current migration state."] },
  { event_id: "CML-PDRE-001-TL-0008", event: "SOURCE_REPORTED_FORWARD_DEPLOYMENT_TIMING", effective_at: "2026", known_at: "2026-09-17", evidence_refs: ["EV-007"], limitations: ["Source date has year precision; no month or day is inferred. Performance and rack-space claims are not independently verified."] },
]);

export const BUNDLED_TEMPORAL_STATE_HISTORY = Object.freeze([
  { change_event_id: "CML-PDRE-001-SH-0002", state_before: "NOT_ASSIGNED", state_after: "R3", known_at: "2026-09-17", effective_at: "2026-09-17T13:55:14Z", evidence_ids: ["EV-003", "EV-004"], reason: "UNKNOWN", supports: "TECHNICALLY_CREDIBLE", does_not_support: ["Authorized by CML-PDRE-001-EVP-001 for PDRE-001A only.", "Does not establish R4 or higher.", "PDRE-001B remains NOT_ASSIGNED."] },
]);

export function hydrateBundledTemporalRecord(record) {
  const hydrated = structuredClone(record);
  hydrated.pdre_record.timeline = structuredClone(BUNDLED_TEMPORAL_TIMELINE);
  hydrated.pdre_record.state_history = structuredClone(BUNDLED_TEMPORAL_STATE_HISTORY);
  return hydrated;
}
