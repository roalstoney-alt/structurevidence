import { objectHash } from "./phase5-core.js";

export const STOP_POINT_VERSION = "SE_STOP_POINT_v0.2";
export const STOP_STATES = Object.freeze(["KNOWN", "ATTRIBUTABLE_ONLY", "UNKNOWN", "NOT_ESTABLISHED", "NOT_FOUND_WITHIN_SCOPE", "CONFLICTED"]);
export const STOP_REASONS = Object.freeze(["EVIDENCE_SUFFICIENT", "RESEARCH_ENVELOPE_EXHAUSTED", "SOURCE_CONTROLLED_INFORMATION", "DEADLINE_REACHED", "NO_ADDITIONAL_DISCOVERABLE_SOURCES", "CUSTOMER_CANCELLED", "HUMAN_STOP", "OTHER_EXPLICIT"]);
export const SOURCE_ACCESS_STATUSES = Object.freeze(["PUBLIC", "PAYWALLED", "REGISTRATION_REQUIRED", "ACCESS_RESTRICTED", "SOURCE_CONTROLLED", "CONFIDENTIAL", "KNOWN_TO_EXIST_NOT_ACCESSIBLE", "UNAVAILABLE_OR_REMOVED", "UNKNOWN_ACCESS"]);
export const DIRECT_INQUIRY_STATUSES = Object.freeze(["NOT_SENT", "SENT", "DELIVERY_CONFIRMED", "DELIVERY_UNCONFIRMED", "ACKNOWLEDGED", "NO_RESPONSE_BY_CUTOFF", "DECLINED_TO_COMMENT", "REDIRECTED", "PARTIALLY_CONFIRMED", "CONFIRMED", "CONTRADICTED", "RESPONSE_RECEIVED_PRIVATE"]);
export const VERIFICATION_DEPTHS = Object.freeze(["V0_LIBRARY_ONLY", "V1_PUBLIC_SEARCH", "V2_PRIMARY_SOURCE_SEARCH", "V3_RESTRICTED_OR_PAID_SOURCE_CHECK", "V4_DIRECT_WRITTEN_INQUIRY", "V5_INDEPENDENT_THIRD_PARTY_VERIFICATION"]);
export const VERIFICATION_MODES = Object.freeze(["PUBLIC_EVIDENCE_AVAILABLE", "PUBLIC_EVIDENCE_INSUFFICIENT", "CUSTOMER_EVIDENCE_REQUIRED", "SOURCE_CONTROLLED_INFORMATION", "INDEPENDENT_VERIFICATION_REQUIRED"]);
export const DOMAIN_RISK_CLASSES = Object.freeze(["R0_GENERAL", "R1_PROFESSIONAL", "R2_HIGH_STAKES", "R3_RESTRICTED"]);
export const PROVENANCE_CLASSES = Object.freeze(["PUBLIC_PRIMARY", "PUBLIC_SECONDARY", "CUSTOMER_PROVIDED_VERIFIED", "CUSTOMER_PROVIDED_UNVERIFIED", "VENDOR_CLAIM", "THIRD_PARTY_TEST", "INDEPENDENT_RECORD", "CONFIDENTIAL_SOURCE", "UNKNOWN_PROVENANCE"]);
export const CLAIM_MATCH_RESULTS = Object.freeze(["EXACT_MATCH", "ISOMORPHIC_MATCH", "PARTIAL_MATCH", "NO_MATCH"]);
export const UNKNOWN = "UNKNOWN";

const requiredScope = ["subject", "technical_boundary", "deployment_class", "jurisdiction", "attribution_scope", "time_boundary", "population_scope"];
const requiredStopOrder = ["CLAIM", "SCOPE", "AS_OF", "FRESHNESS_STATUS", "STATE", "SUPPORTS", "DOES_NOT_SUPPORT", "QUALIFYING_RECORDS", "REJECTED_OR_COUNTER", "SEARCH_PROVENANCE", "SOURCE_ACCESS_STATUS", "DIRECT_INQUIRY_STATUS", "VERIFICATION_DEPTH", "OPEN_GAP_IF_UNKNOWN", "NEXT_MINIMUM_VERIFICATION", "NOT_A", "CLAIM_ID", "VERSION"];
const present = (value) => value !== null && value !== undefined && value !== "";

export function mapCanonicalToPublicState(canonicalState, evidence = {}) {
  const mapping = {
    KNOWN: "KNOWN", UNKNOWN: "UNKNOWN", NOT_ESTABLISHED: "NOT_ESTABLISHED", CONFLICTED: "CONFLICTED",
    R5_FIELD_DEPLOYED: "KNOWN", R5_ARCHITECTURE_FIELD_DEPLOYMENT_EVIDENCE_ACCEPTED_SINGLE_INSTANCE: "ATTRIBUTABLE_ONLY",
    R5_FIELD_DEPLOYED_NOT_ESTABLISHED: "NOT_ESTABLISHED",
  };
  const recordedNotFound = evidence.search_complete === true && evidence.qualifying_results === 0 && Number.isFinite(evidence.actual_query_count) && evidence.actual_query_count > 0 && Number.isFinite(evidence.actual_source_count) && evidence.actual_source_count > 0 && ["RESEARCH_ENVELOPE_EXHAUSTED", "NO_ADDITIONAL_DISCOVERABLE_SOURCES"].includes(evidence.stop_reason);
  if (recordedNotFound) return "NOT_FOUND_WITHIN_SCOPE";
  return mapping[canonicalState] || "UNKNOWN";
}

export function claimScopeFingerprint(input) {
  const fingerprint = {
    subject: input.subject || "UNRESOLVED", predicate: input.predicate || "UNRESOLVED", object: input.object || "EVIDENCE_ESTABLISHMENT",
    technical_scope: input.technical_scope || input.scope || "UNRESOLVED", jurisdiction: input.jurisdiction || "UNRESOLVED",
    deployment_class: input.deployment_class || (input.predicate === "NAMED_COMMERCIAL_OR_FIELD_OPERATION" ? "COMMERCIAL_FIELD_OPERATION" : "UNRESOLVED"),
    attribution_scope: input.attribution_scope || (input.predicate === "NAMED_COMMERCIAL_OR_FIELD_OPERATION" ? "NAMED_OPERATOR" : "UNRESOLVED"),
    time_boundary: input.time_boundary || "UNRESOLVED", population_scope: input.population_scope || (input.predicate === "NAMED_COMMERCIAL_OR_FIELD_OPERATION" ? "ONE_OR_MORE_NAMED_INSTANCES" : "UNRESOLVED"),
  };
  return Object.freeze(fingerprint);
}

export function atomicClaimGate(rawClaim) {
  const value = String(rawClaim || "").trim();
  const conjunction = /(?:,|\band\b|\bplus\b|；|，|并且|以及)/i.test(value);
  const propositions = [/(commercial|field).*(deploy|operat)|商业.*运行|现场.*部署/i, /(cheaper|cost superiority|经济性|更便宜)/i, /(reliab|可靠性)/i].filter((pattern) => pattern.test(value)).length;
  const atomic = !(conjunction && propositions > 1);
  return { ATOMIC_CLAIM_REQUIRED: atomic ? "PASS" : "FAIL", atomic, proposition_count: Math.max(propositions, value ? 1 : 0), decomposition_required: !atomic };
}

export function matchScopeFingerprint(candidate, library) {
  const keys = Object.keys(library), exact = keys.every((key) => candidate[key] === library[key]);
  if (exact) return "EXACT_MATCH";
  const core = ["subject", "predicate", "technical_scope", "deployment_class", "attribution_scope", "population_scope"];
  const compatible = core.every((key) => candidate[key] === library[key] || candidate[key] === "UNRESOLVED");
  if (compatible && candidate.subject !== "UNRESOLVED" && candidate.predicate !== "UNRESOLVED") return "ISOMORPHIC_MATCH";
  if (candidate.subject === library.subject) return "PARTIAL_MATCH";
  return "NO_MATCH";
}

export async function createSearchProvenance(researchRecord, classification = {}, capital = {}) {
  const record = researchRecord.research_record || researchRecord;
  const value = {
    search_run_id: `SE-SEARCH-${record.research_id}`, claim_id: "SE-CLAIM-800V-001", rdl_run_id: record.research_id,
    started_at: record.started_at, ended_at: record.completed_at, cutoff: record.completed_at,
    research_envelope_id: record.authorization?.authorization_ref || UNKNOWN,
    queries_executed: record.query_refs?.length ?? classification.query_count ?? UNKNOWN,
    search_engines_used: UNKNOWN, databases_checked: UNKNOWN, domains_checked: UNKNOWN,
    source_types_checked: ["PRIMARY_OPERATOR_PUBLICATION", "VENDOR_TECHNICAL_MATERIAL", "DERIVED_REPORTING"],
    results_discovered: record.source_refs_checked?.length ?? classification.sources_checked ?? UNKNOWN,
    results_reviewed: record.source_refs_checked?.length ?? classification.sources_checked ?? UNKNOWN,
    results_rejected: record.source_refs_rejected?.length ?? classification.sources_rejected ?? UNKNOWN,
    qualifying_results: record.source_refs_used?.length ?? classification.sources_used ?? UNKNOWN,
    restricted_sources: UNKNOWN, paywalled_sources: UNKNOWN, unavailable_sources: UNKNOWN,
    query_limit: classification.query_limit ?? capital.authorized_query_budget ?? UNKNOWN,
    source_limit: UNKNOWN, deep_review_limit: classification.deep_source_review_limit ?? capital.authorized_deep_review_budget ?? UNKNOWN,
    external_data_cap: record.telemetry?.cost_limit?.status === "KNOWN" ? record.telemetry.cost_limit.value : UNKNOWN,
    actual_query_count: record.query_refs?.length ?? UNKNOWN, actual_source_count: record.source_refs_checked?.length ?? UNKNOWN,
    actual_deep_review_count: classification.deep_source_review_count ?? capital.deep_reviews_used ?? record.research_actions?.filter((item) => item.action_type === "SOURCE_REVIEW").length ?? UNKNOWN,
    actual_external_data_cost: record.telemetry?.data_cost?.status === "KNOWN" ? record.telemetry.data_cost.value : UNKNOWN,
    stop_reason: STOP_REASONS.includes(record.stop_reason) ? record.stop_reason : record.stop_reason === "QUALIFYING_RECORD_FOUND" ? "EVIDENCE_SUFFICIENT" : "OTHER_EXPLICIT",
  };
  value.search_hash = await objectHash(value);
  return Object.freeze(value);
}

export function publicSearchProvenance(log) {
  return Object.freeze({ verification_level: "V2_PRIMARY_SOURCE_SEARCH", started_at: log.started_at, ended_at: log.ended_at, cutoff: log.cutoff, research_envelope: log.research_envelope_id, query_count: log.actual_query_count, source_count: log.actual_source_count, source_categories: log.source_types_checked, deep_review_count: log.actual_deep_review_count, qualifying_count: log.qualifying_results, rejected_count: log.results_rejected, access_limited_count: log.restricted_sources, stop_reason: log.stop_reason, search_hash: log.search_hash });
}

export function classifySourceAccess(status) {
  if (!SOURCE_ACCESS_STATUSES.includes(status)) throw new Error("INVALID_SOURCE_ACCESS_STATUS");
  return status;
}

export async function createDirectInquiryDraft({ claim_id, rdl_run_id, target_organization, target_role_or_department, question, response_deadline }) {
  const value = { inquiry_id: `SE-INQUIRY-${crypto.randomUUID()}`, claim_id, rdl_run_id, target_organization, target_role_or_department, question_sent: null, message_draft: question, sent_at: null, channel: "WRITTEN", delivery_status: "NOT_SENT", delivery_evidence_ref: null, response_deadline, response_status: "NOT_SENT", response_received_at: null, response_summary: null, publication_permission: "NOT_REQUESTED", confidentiality_status: "UNASSESSED", auto_send: false };
  value.inquiry_hash = await objectHash(value); value.response_hash = null;
  return value;
}

export async function recordDirectInquirySend(draft, { sent_at, channel, delivery_status, delivery_evidence_ref, human_approved }) {
  if (!human_approved || !sent_at || !delivery_evidence_ref || !["DELIVERY_CONFIRMED", "DELIVERY_UNCONFIRMED"].includes(delivery_status)) throw new Error("DELIVERY_EVIDENCE_AND_HUMAN_APPROVAL_REQUIRED");
  const value = { ...draft, question_sent: draft.message_draft, sent_at, channel, delivery_status, delivery_evidence_ref, response_status: delivery_status };
  value.inquiry_hash = await objectHash({ ...value, inquiry_hash: undefined });
  return value;
}

export async function recordDirectInquiryResponse(inquiry, response) {
  if (!DIRECT_INQUIRY_STATUSES.includes(response.response_status)) throw new Error("INVALID_DIRECT_INQUIRY_STATUS");
  const value = { ...inquiry, ...response };
  value.response_hash = await objectHash({ inquiry_id: value.inquiry_id, response_status: value.response_status, response_received_at: value.response_received_at, response_summary: value.response_summary });
  value.claim_state_effect = ["NO_RESPONSE_BY_CUTOFF", "DECLINED_TO_COMMENT"].includes(value.response_status) ? "NEUTRAL" : "REQUIRES_HUMAN_DETERMINATION";
  return value;
}

export function createNotFoundWithinScope(scope, provenance) {
  const queryCount = provenance?.actual_query_count ?? provenance?.query_count;
  const sourceCount = provenance?.actual_source_count ?? provenance?.source_count;
  const qualifyingCount = provenance?.qualifying_results ?? provenance?.qualifying_count;
  const completeStop = ["RESEARCH_ENVELOPE_EXHAUSTED", "NO_ADDITIONAL_DISCOVERABLE_SOURCES"].includes(provenance?.stop_reason);
  if (!Number.isFinite(queryCount) || queryCount <= 0 || !Number.isFinite(sourceCount) || sourceCount <= 0 || qualifyingCount !== 0 || !completeStop) throw new Error("NOT_FOUND_WITHIN_SCOPE_REQUIRES_COMPLETED_RECORDED_SEARCH");
  return { state: "NOT_FOUND_WITHIN_SCOPE", supports: ["No qualifying evidence was identified within the documented scope."], does_not_support: ["This does not establish that qualifying evidence does not exist outside the searched scope or in inaccessible/private sources."], scope, search_provenance: provenance };
}

export function createConflictedDetermination({ supporting, counter, conflict, next }) {
  if (!supporting?.length || !counter?.length || !conflict || !next) throw new Error("INCOMPLETE_CONFLICTED_DETERMINATION");
  return { state: "CONFLICTED", supports: supporting, does_not_support: counter, unresolved_conflict: conflict, next_minimum_verification: next };
}

export function evidenceLineageSummary(records) {
  const origins = new Set(records.map((item) => item.origin_id || item.id));
  const confirmations = new Set(records.filter((item) => item.independence_class === "INDEPENDENT_CONFIRMATION").map((item) => item.origin_id || item.id));
  return { DOCUMENT_COUNT: records.length, INDEPENDENT_ORIGIN_COUNT: origins.size, INDEPENDENT_CONFIRMATION_COUNT: confirmations.size };
}

export function lateEvidenceRecord({ published_at, effective_at, observed_at, recorded_at }) {
  if (Date.parse(observed_at) < Date.parse(published_at) || Date.parse(recorded_at) < Date.parse(observed_at)) throw new Error("INVALID_KNOWLEDGE_TIME");
  return { published_at, effective_at, observed_at, recorded_at, historical_state_rewritten: false };
}

export function assessFreshness(asOf, policy, now = new Date().toISOString()) {
  if (!policy) return "UNASSESSED";
  const ageDays = (Date.parse(now) - Date.parse(asOf)) / 86400000;
  if (ageDays <= policy.current_days) return "CURRENT";
  if (ageDays <= policy.stale_days) return "AGING";
  return "STALE";
}

export function validateResearchCycle(cycle) {
  if (!cycle.cutoff) return { accepted: false, reason: "CUTOFF_REQUIRED" };
  for (const key of ["query_limit", "source_limit", "deep_review_limit", "external_data_cap"]) if (!Number.isFinite(cycle[key]) || cycle[key] < 0) return { accepted: false, reason: `INVALID_${key.toUpperCase()}` };
  if (!cycle.deadline) return { accepted: false, reason: "DEADLINE_REQUIRED" };
  const hours = (Date.parse(cycle.deadline) - Date.now()) / 3600000;
  const deadline_feasibility = hours < 0 ? "DEADLINE_NOT_FEASIBLE" : hours < 24 ? "LIMITED_SCOPE_ONLY" : "DEADLINE_READY";
  return { accepted: deadline_feasibility !== "DEADLINE_NOT_FEASIBLE", deadline_feasibility, hard_cap: true, payment_buys_process: true, payment_buys_preferred_outcome: false };
}

export function enforceResearchEnvelope(cycle, actual) {
  const reached = actual.query_count >= cycle.query_limit || actual.source_count >= cycle.source_limit || actual.deep_review_count >= cycle.deep_review_limit || actual.external_data_cost > cycle.external_data_cap;
  return { continue_research: !reached, hard_cap_reached: reached, stop_reason: reached ? "RESEARCH_ENVELOPE_EXHAUSTED" : null, scope_expanded: false, next_cycle_requires_new_quote: reached };
}

export function createPrivateStopPoint(stopPoint, provenance = {}) {
  return { visibility: "PRIVATE_STOP_POINT", stop_point: stopPoint, provenance, public_library_eligible: false };
}

export function publicPromotionGate(checks) {
  const required = ["provenance_validation", "privacy_validation", "license_validation", "human_acceptance"];
  return { promoted: required.every((key) => checks[key] === true) && checks.customer_authorization !== false, required };
}

export function createStopPointV2(input) {
  if (!STOP_STATES.includes(input.STATE)) throw new Error("INVALID_PUBLIC_STOP_STATE");
  if (!input.SCOPE || requiredScope.some((key) => !present(input.SCOPE[key]))) throw new Error("SCOPE_REQUIRED");
  if (!input.SUPPORTS?.length || !input.DOES_NOT_SUPPORT?.length) throw new Error("BOUNDARY_INCOMPLETE");
  if (!VERIFICATION_DEPTHS.includes(input.VERIFICATION_DEPTH)) throw new Error("INVALID_VERIFICATION_DEPTH");
  const stop = {};
  for (const key of requiredStopOrder) stop[key] = input[key];
  stop.determination = Object.freeze({ state: stop.STATE, supports: stop.SUPPORTS, does_not_support: stop.DOES_NOT_SUPPORT });
  stop.boundary_complete = true;
  return Object.freeze(stop);
}

export { requiredStopOrder as STOP_POINT_FIELD_ORDER };
