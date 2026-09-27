import { canonicalSerialize, objectHash } from "./phase5-core.js";

export const TEMPORAL_PROJECTION_VERSION = "SE_TEMPORAL_VISUALIZATION_v0.1";
export const TEMPORAL_WINDOWS = Object.freeze([30, 90]);
const UNKNOWN = "UNKNOWN";
const time = (value) => {
  const parsed = Date.parse(value || "");
  return Number.isFinite(parsed) ? parsed : null;
};
const unique = (values) => [...new Set(values.filter(Boolean))];
const slug = (value) => String(value).toUpperCase().replace(/[^A-Z0-9]+/g, "_").replace(/^_|_$/g, "");
const availableAt = (item, fallback) => item.known_at || item.recorded_at || item.observed_at || fallback;
const visibleAt = (item, boundary, fallback) => {
  const known = time(availableAt(item, fallback)), effective = time(item.effective_at);
  return known !== null && known <= boundary && (effective === null || effective <= boundary);
};

function componentRate(kind, events, windowDays, cutoff) {
  const lower = cutoff - windowDays * 86_400_000;
  const source = events.filter((item) => item.event_type === kind && time(item.timestamp) > lower && time(item.timestamp) <= cutoff);
  if (!source.length) return { component: `${kind}_RATE`, window_days: windowDays, event_count: UNKNOWN, rate_per_day: UNKNOWN, source_event_ids: [], interpretation: "No event cannot be distinguished from incomplete history." };
  return { component: `${kind}_RATE`, window_days: windowDays, event_count: source.length, rate_per_day: Number((source.length / windowDays).toFixed(6)), source_event_ids: source.map((item) => item.visual_event_id), interpretation: "Recorded event cadence, not adoption speed." };
}

export async function projectTemporalVisualization(record, { asOf = null, windowDays = 90, researchRecords = [] } = {}) {
  if (!TEMPORAL_WINDOWS.includes(windowDays)) throw Object.assign(new Error("Window must be 30 or 90 days."), { status: 400, code: "INVALID_WINDOW" });
  if (!record?.core?.record_hash || !record?.pdre_record) throw new Error("CANONICAL_PDRE_RECORD_REQUIRED");
  const latestKnownAt = [record.core.known_at, ...researchRecords.map((item) => item?.core?.known_at).filter(Boolean)].sort().at(-1);
  const cutoffIso = asOf || latestKnownAt;
  const cutoff = time(cutoffIso);
  if (cutoff === null) throw Object.assign(new Error("as_of must be RFC 3339."), { status: 400, code: "INVALID_AS_OF" });
  const pdre = record.pdre_record;
  const recordVisible = time(record.core.known_at) <= cutoff;
  const evidenceById = new Map((pdre.known_evidence || []).map((item) => [item.evidence_id, item]));
  const counterIds = new Set((pdre.counter_evidence || []).flatMap((item) => item.evidence_refs || []));
  const qualifyingIds = new Set(pdre.migration_readiness?.evidence_refs || []);
  const sourceTimeline = recordVisible ? (pdre.timeline || []).filter((item) => visibleAt(item, cutoff, record.core.known_at)) : [];
  const evidenceEvents = [];
  for (const [index, item] of sourceTimeline.entries()) {
    for (const evidenceId of item.evidence_refs || []) {
      const evidence = evidenceById.get(evidenceId);
      const eventType = counterIds.has(evidenceId) ? "COUNTER_EVIDENCE" : qualifyingIds.has(evidenceId) ? "QUALIFYING_EVIDENCE" : "EVIDENCE";
      evidenceEvents.push({
        visual_event_id: `TV-${String(index + 1).padStart(3, "0")}-${evidenceId}`,
        timestamp: availableAt(item, record.core.known_at), effective_at: item.effective_at || null,
        event_type: eventType, subject_id: record.core.subject_id, branch_id: null,
        state_before: null, state_after: null, evidence_ids: [evidenceId], counter_evidence_ids: counterIds.has(evidenceId) ? [evidenceId] : [],
        unknown_ids: [], outcome_ids: [], source_refs: unique([record.core.record_id, item.event_id, evidenceId]),
        classification: evidence?.evidence_type || UNKNOWN, source: evidence?.source_ref || UNKNOWN,
        summary: item.event, supports: qualifyingIds.has(evidenceId) ? pdre.migration_readiness.code : UNKNOWN,
        does_not_support: evidence?.limitations || [],
      });
    }
  }
  const unknownHistory = (pdre.unknown_history || []).filter((item) => visibleAt(item, cutoff, record.core.known_at));
  const unknownEvents = unknownHistory.map((item, index) => ({
    visual_event_id: `TV-UNK-${String(index + 1).padStart(3, "0")}`, timestamp: availableAt(item, record.core.known_at), effective_at: item.effective_at || null,
    event_type: item.status === "RESOLVED" ? "UNKNOWN_RESOLVED" : "UNKNOWN_OPENED", subject_id: record.core.subject_id,
    branch_id: null, state_before: null, state_after: null, evidence_ids: item.evidence_refs || [], counter_evidence_ids: [],
    unknown_ids: item.unknown_id ? [item.unknown_id] : [], outcome_ids: [], source_refs: unique([record.core.record_id, item.unknown_id, ...(item.evidence_refs || [])]),
  }));
  const openUnknowns = (recordVisible ? pdre.unknowns || [] : []).map((label, index) => ({
    unknown_key: slug(label), label, status: "OPEN", canonical_unknown_id: null,
    source_refs: [record.core.record_id], first_recorded_at: record.core.known_at, ordinal_in_record: index,
  }));
  const stateHistory = (pdre.state_history || []).filter((item) => visibleAt(item, cutoff, record.core.known_at));
  const changeEvents = stateHistory.filter((item) => item.state_before && item.state_after).map((item, index) => ({
    visual_event_id: `TV-CHG-${String(index + 1).padStart(3, "0")}`, timestamp: availableAt(item, record.core.known_at), effective_at: item.effective_at || null,
    event_type: "STATE_TRANSITION", subject_id: record.core.subject_id, branch_id: item.branch_id || null,
    state_before: item.state_before, state_after: item.state_after, evidence_ids: item.evidence_ids || [], counter_evidence_ids: item.counter_evidence_ids || [],
    unknown_ids: item.unknown_ids || [], outcome_ids: item.outcome_ids || [], source_refs: unique([item.change_event_id, ...(item.evidence_ids || [])]),
    change_event_id: item.change_event_id, reason: item.reason || UNKNOWN, supports: item.supports || UNKNOWN, does_not_support: item.does_not_support || [],
  }));
  const branches = (pdre.branches || []).filter((item) => visibleAt(item, cutoff, record.core.known_at)).map((item) => ({ ...item, source_refs: unique([item.branch_id, ...(item.evidence_ids || [])]) }));
  const outcomes = (pdre.outcomes || []).filter((item) => visibleAt(item, cutoff, record.core.known_at));
  const visibleResearch = researchRecords.filter((item) => item?.core?.record_hash && time(item.core.known_at) <= cutoff);
  const researchDecisionEvents = visibleResearch.filter((item) => item.research_record?.decision_changed === true).map((item, index) => ({
    visual_event_id: `TV-RDL-${String(index + 1).padStart(3, "0")}`, timestamp: item.core.known_at, effective_at: item.core.effective_at || null,
    event_type: "RESEARCH_DECISION_CHANGE", subject_id: record.core.subject_id, branch_id: null,
    state_before: item.research_record.decision_before, state_after: item.research_record.decision_after,
    evidence_ids: item.research_record.new_evidence_refs || [], counter_evidence_ids: item.research_record.counter_evidence_refs || [],
    unknown_ids: [], outcome_ids: [], source_refs: unique([item.core.record_id, ...(item.research_record.new_evidence_refs || [])]),
    change_event_id: null, reason: item.research_record.decision_change_reason,
    supports: item.research_record.decision_after, does_not_support: [item.research_record.readiness_after, ...(item.research_record.unknowns_remaining || [])],
    canonical_state_mutated: false,
  }));
  const researchEvidenceEvents = visibleResearch.flatMap((item, recordIndex) => (item.research_record?.new_evidence_refs || []).map((evidenceId, evidenceIndex) => ({
    visual_event_id: `TV-RDL-EV-${String(recordIndex + 1).padStart(2, "0")}-${String(evidenceIndex + 1).padStart(2, "0")}`,
    timestamp: item.core.known_at, effective_at: item.core.effective_at || null, event_type: "QUALIFYING_EVIDENCE",
    subject_id: record.core.subject_id, branch_id: null, state_before: null, state_after: null,
    evidence_ids: [evidenceId], counter_evidence_ids: [], unknown_ids: [], outcome_ids: [],
    source_refs: [item.core.record_id, evidenceId], classification: "FIELD_DEPLOYMENT_EVIDENCE",
    source: item.core.record_id, summary: item.research_record.hypothesis_after,
    supports: item.research_record.decision_after,
    does_not_support: [item.research_record.readiness_after, ...(item.research_record.unknowns_remaining || [])],
    qualification_scope: "RESEARCH_DECISION_ONLY",
  })));
  const researchUnknownEvents = visibleResearch.flatMap((item, recordIndex) => (item.research_record?.unknowns_resolved || []).map((label, unknownIndex) => ({
    visual_event_id: `TV-RDL-UNK-${String(recordIndex + 1).padStart(2, "0")}-${String(unknownIndex + 1).padStart(2, "0")}`,
    timestamp: item.core.known_at, effective_at: item.core.effective_at || null, event_type: "UNKNOWN_RESOLVED",
    subject_id: record.core.subject_id, branch_id: null, state_before: null, state_after: null,
    evidence_ids: item.research_record.new_evidence_refs || [], counter_evidence_ids: [], unknown_ids: [], outcome_ids: [],
    source_refs: [item.core.record_id, ...(item.research_record.new_evidence_refs || [])], summary: label,
  })));
  const researchOpenUnknowns = visibleResearch.flatMap((item, recordIndex) => (item.research_record?.unknowns_remaining || []).map((label, unknownIndex) => ({
    unknown_key: slug(label), label, status: "OPEN", canonical_unknown_id: null,
    source_refs: [item.core.record_id], first_recorded_at: item.core.known_at, ordinal_in_record: `${recordIndex}:${unknownIndex}`,
  })));
  const currentOpenUnknowns = [...openUnknowns, ...researchOpenUnknowns].filter((item, index, values) => values.findIndex((value) => value.unknown_key === item.unknown_key) === index);
  const allEvents = [...evidenceEvents, ...researchEvidenceEvents, ...unknownEvents, ...researchUnknownEvents, ...changeEvents, ...researchDecisionEvents].sort((a, b) => a.timestamp.localeCompare(b.timestamp) || a.visual_event_id.localeCompare(b.visual_event_id));
  const knownTimes = allEvents.map((item) => time(item.timestamp)).filter((item) => item !== null);
  const effectiveTimes = allEvents.map((item) => time(item.effective_at)).filter((item) => item !== null);
  const startMs = Math.min(cutoff, ...effectiveTimes, ...knownTimes);
  const rates = ["QUALIFYING_EVIDENCE", "COUNTER_EVIDENCE", "UNKNOWN_RESOLVED", "STATE_TRANSITION"].map((kind) => componentRate(kind, allEvents, windowDays, cutoff));
  const sourceSnapshotHash = await objectHash([record.core.record_hash, ...visibleResearch.map((item) => item.core.record_hash)]);
  const projection = {
    projection_version: TEMPORAL_PROJECTION_VERSION, subject_id: record.core.subject_id,
    generated_at: [record.core.updated_at, ...visibleResearch.map((item) => item.core.updated_at)].sort().at(-1), as_of: cutoffIso, source_snapshot_hash: sourceSnapshotHash,
    time_range: { start: new Date(startMs).toISOString(), end: cutoffIso, playback_clock: "KNOWLEDGE_TIME", effective_time_inspectable: true, compressed: true },
    states: recordVisible ? [{ state_id: record.core.record_id, state_code: pdre.migration_readiness.code, state_name: pdre.migration_readiness.name,
      timestamp: record.core.known_at, evidence_ids: pdre.migration_readiness.evidence_refs || [], source_refs: [record.core.record_id],
      supports: pdre.migration_readiness.interpretation, does_not_support: pdre.migration_readiness.limitations || [] }] : [],
    change_events: changeEvents, research_decision_events: researchDecisionEvents, branches, evidence_events: [...evidenceEvents.filter((item) => item.event_type !== "COUNTER_EVIDENCE"), ...researchEvidenceEvents],
    counter_evidence_events: evidenceEvents.filter((item) => item.event_type === "COUNTER_EVIDENCE"),
    unknown_events: [...unknownEvents, ...researchUnknownEvents], open_unknowns: currentOpenUnknowns, outcome_events: outcomes,
    velocity_series: rates, provenance_map: Object.fromEntries(allEvents.map((item) => [item.visual_event_id, item.source_refs])),
    paths: recordVisible ? [
      { path_id: "LEGACY_POWER_PATH", label: pdre.old_path.description, source_refs: pdre.old_path.evidence_refs || [] },
      { path_id: "800VDC_ALTERNATIVE_PATH", label: pdre.new_path.description, source_refs: pdre.new_path.evidence_refs || [] },
    ] : [],
    transition_availability: changeEvents.length ? "RECORDED" : "NO_CANONICAL_CHANGE_EVENT",
    r4_to_r5: changeEvents.find((item) => item.state_before === "R4" && item.state_after === "R5") || null,
    current_frame: { state: recordVisible ? pdre.migration_readiness.code : UNKNOWN, last_meaningful_change: changeEvents.at(-1)?.change_event_id || null,
      supported_dimensions: [pdre.migration_readiness.interpretation], open_gaps: currentOpenUnknowns.map((item) => item.unknown_key),
      counter_evidence_count: recordVisible ? (pdre.counter_evidence || []).length : UNKNOWN, active_branches: branches.length, as_of: cutoffIso,
      proof_ref: sourceSnapshotHash },
  };
  projection.projection_hash = await objectHash(projection);
  return projection;
}

export function temporalProjectionCanonicalForm(projection) {
  const { projection_hash, ...withoutHash } = projection;
  return canonicalSerialize(withoutHash);
}
