import { objectHash, SnapshotChainProvider, UNKNOWN_COST } from "./phase5-core.js";

export const PHASE5B_EVENT_ID = "SE-EVENT-800001";
export const DECISION_DIMENSIONS = Object.freeze([
  "FIELD_DEPLOYMENT", "OPERATING_HISTORY", "REPLICATION",
  "INDEPENDENT_VALIDATION", "ECONOMICS", "CONTEXT_FIT",
]);
export const RESEARCH_ENVELOPES = Object.freeze({
  G1: { queries_max: 4, sources_max: 10, deep_reviews_max: 1, paid_data: false, specialist_review: false },
  G2: { queries_max: 8, sources_max: 25, deep_reviews_max: 3, paid_data: "BOUNDED", specialist_review: false },
  G3: { queries_max: 15, sources_max: 50, deep_reviews_max: 5, paid_data: "BOUNDED", specialist_review: true },
});
export const DECISION_STATES = Object.freeze([
  "REQUEST_SUBMITTED", "PREFLIGHT_COMPLETE", "QUOTE_ISSUED", "QUOTE_ACCEPTED",
  "PAYMENT_PENDING", "PAYMENT_CONFIRMED", "RDL_BOUND", "RESEARCH_IN_PROGRESS",
  "DETERMINATION_READY", "DELIVERED", "OUTCOME_PENDING", "OUTCOME_RECORDED", "CLOSED",
  "DECLINED", "EXPIRED", "CANCELLED",
]);
const TERMINAL_STATES = new Set(["CLOSED", "DECLINED", "EXPIRED", "CANCELLED"]);
const TRANSITIONS = Object.freeze({
  REQUEST_SUBMITTED: ["PREFLIGHT_COMPLETE", "DECLINED", "CANCELLED"],
  PREFLIGHT_COMPLETE: ["QUOTE_ISSUED", "DECLINED", "CANCELLED"],
  QUOTE_ISSUED: ["QUOTE_ACCEPTED", "EXPIRED", "DECLINED", "CANCELLED"],
  QUOTE_ACCEPTED: ["PAYMENT_PENDING", "CANCELLED"], PAYMENT_PENDING: ["PAYMENT_CONFIRMED", "CANCELLED"],
  PAYMENT_CONFIRMED: ["RDL_BOUND", "CANCELLED"], RDL_BOUND: ["RESEARCH_IN_PROGRESS", "CANCELLED"],
  RESEARCH_IN_PROGRESS: ["DETERMINATION_READY", "CANCELLED"], DETERMINATION_READY: ["DELIVERED"],
  DELIVERED: ["OUTCOME_PENDING", "CLOSED"], OUTCOME_PENDING: ["OUTCOME_RECORDED", "CLOSED"],
  OUTCOME_RECORDED: ["CLOSED"],
});
const ASCII = /^[\x21-\x7E]+$/;
const money = (value) => typeof value === "number" && Number.isFinite(value) && value >= 0 ? value : UNKNOWN_COST;
const countRefs = (items) => new Set(items.flatMap((item) => item.evidence_refs || [])).size;
const hasUnknown = (record, expression) => record.pdre_record.unknowns.some((item) => expression.test(item));
const stage = (record, name) => record.pdre_record.pdre.pdre_evidence_chain.find((item) => item.stage === name);
const counterCount = (record, dimension) => dimension === "FIELD_DEPLOYMENT" ? record.pdre_record.counter_evidence.length : 0;

export function project800vDecisionInventory(record) {
  if (!record?.core?.record_hash || record?.pdre_record?.identity?.cml_id !== "CML-PDRE-001") throw new Error("CANONICAL_800V_RECORD_REQUIRED");
  const knownAt = record.core.known_at;
  const field = stage(record, "FIELD_DEPLOYMENT"), replication = stage(record, "MULTI_USER_MULTI_OEM_REPLICATION");
  const dimensions = [
    ["FIELD_DEPLOYMENT", field.status, "No approved field-operation evidence; forward timing is counter-evidence.", field.evidence_refs, true],
    ["OPERATING_HISTORY", hasUnknown(record, /Operating history/i) ? "UNKNOWN" : "ESTABLISHED", "No duration, failure-rate, maintenance, or operating-history evidence is approved.", [], true],
    ["REPLICATION", replication.status, "Coordination and a specification do not establish multi-user or multi-OEM replication.", replication.evidence_refs, true],
    ["INDEPENDENT_VALIDATION", hasUnknown(record, /Independent validation/i) ? "UNKNOWN" : "ESTABLISHED", "Performance, copper, rack-space, and efficiency claims are not independently validated.", [], true],
    ["ECONOMICS", "UNKNOWN", "CAPEX, ROI, payback, reliability, and service economics are not calculable.", Object.values(record.pdre_record.economics).flatMap((item) => item.evidence_refs || []), true],
    ["CONTEXT_FIT", "UNKNOWN", "No private decision context, jurisdiction, system boundary, or requirements were supplied.", [], true],
  ].map(([dimension_id, current_state, why, evidence_refs, verification_available]) => ({
    dimension_id, current_state, as_of: knownAt, why,
    qualifying_records_count: current_state === "ESTABLISHED" ? countRefs([{ evidence_refs }]) : 0,
    linked_records_count: countRefs([{ evidence_refs }]), counter_records_count: counterCount(record, dimension_id),
    unknown_count: current_state === "ESTABLISHED" ? 0 : 1, verification_available,
    last_change_at: knownAt, evidence_refs: [...new Set(evidence_refs)],
  }));
  return {
    schema_version: "SE_DECISION_INVENTORY_v0.1", event_id: PHASE5B_EVENT_ID,
    canonical_record_id: record.core.record_id, canonical_record_hash: record.core.record_hash,
    title: record.pdre_record.identity.title, readiness: record.pdre_record.migration_readiness,
    as_of: knownAt, dimensions,
    primary_gap: "OPERATING_HISTORY", interpretation: "RECORDED_EVIDENCE_STATE_NOT_ADVICE_OR_GUARANTEE",
  };
}

export function project800vPublicEvent(record, inventory) {
  const r = record.pdre_record;
  return {
    event_id: PHASE5B_EVENT_ID, projection_type: "DecisionInventoryProjection", projection_version: "SE_800V_EVENT_v0.1",
    subject: { canonical_name: r.identity.title, domain: "infrastructure", object_type: "PATH_DEPENDENCY_RELEASE_CANDIDATE" },
    current_state: { state_code: r.migration_readiness.code, state_name: r.migration_readiness.name, interpretation: r.migration_readiness.interpretation, supports_company_structural_assessment: false },
    as_of: record.core.known_at, inventory, canonical_record_ref: record.core.record_id,
    canonical_record_hash: record.core.record_hash, canonical_storage_created: false,
    counter_evidence: r.counter_evidence, open_unknowns: r.unknowns, timeline: r.timeline,
    calls_to_action: [{ type: "VERIFY_GAP", label: "Verify an evidence gap" }, { type: "CONTEXT_FIT", label: "Scope context fit" }],
  };
}

export async function projectDecisionEventFromInventory(inventory) {
  const event = {
    projection_type: "DecisionInventoryProjection", projection_version: "SE_800V_EVENT_v0.1", event_id: inventory.event_id,
    as_of: inventory.as_of,
    subject: { canonical_name: inventory.title, domain: "infrastructure", object_type: "PATH_DEPENDENCY_RELEASE_CANDIDATE" },
    current_state: { state_code: inventory.readiness.code, state_name: inventory.readiness.name, observed_at: inventory.as_of, interpretation: inventory.readiness.interpretation },
    change_history: [], supporting_evidence: [],
    counter_evidence: inventory.dimensions.filter((item) => item.counter_records_count > 0).map((item) => ({ dimension_id: item.dimension_id, count: item.counter_records_count, evidence_refs: item.evidence_refs })),
    open_unknowns: inventory.dimensions.filter((item) => item.unknown_count > 0).map((item) => item.dimension_id),
    branches: [], outcomes: [], rdl_history: [], decision_inventory: inventory.dimensions,
    canonical_record_ref: inventory.canonical_record_id, canonical_record_hash: inventory.canonical_record_hash,
    canonical_storage_created: false,
  };
  event.proof = await new SnapshotChainProvider().createProof(event, inventory.canonical_record_hash);
  return event;
}

export function preflightGapVerification(input, inventory) {
  const allowed = new Set(["claim", "decision_context", "decision_deadline", "jurisdiction", "system_boundary", "dimension_id"]);
  if (!input || typeof input !== "object" || Array.isArray(input) || Object.keys(input).some((key) => !allowed.has(key))) throw new Error("INVALID_PREFLIGHT_INPUT");
  if (![input.claim, input.decision_context, input.decision_deadline].every((value) => typeof value === "string" && value.trim())) throw new Error("CLAIM_CONTEXT_AND_DEADLINE_REQUIRED");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(input.decision_deadline)) throw new Error("INVALID_DECISION_DEADLINE");
  const dimension = inventory.dimensions.find((item) => item.dimension_id === (input.dimension_id || inventory.primary_gap));
  if (!dimension) throw new Error("UNKNOWN_DECISION_DIMENSION");
  return {
    schema_version: "SE_GAP_PREFLIGHT_v0.1", event_id: inventory.event_id, dimension_id: dimension.dimension_id,
    feasibility: dimension.verification_available ? "FEASIBLE_WITHIN_PUBLIC_EVIDENCE_BOUNDARY" : "CONDITIONAL",
    current_state: dimension.current_state, decision_deadline: input.decision_deadline,
    acceptance_criteria: [`Evidence must directly address ${dimension.dimension_id}.`, "Event time and knowledge time must be recorded.", "Counter-evidence and unresolved unknowns must remain visible."],
    recommended_envelope: dimension.dimension_id === "OPERATING_HISTORY" ? "G2" : "G1",
    discovery_queries_used: 0, deep_research_performed: false, quote_ready: true,
    cutoff_policy: "DELIVERY_CUTOFF_BOUND_AT_PAYMENT_CONFIRMATION", proof_level: "P1_SNAPSHOT_CHAIN",
    no_favorable_result_guarantee: true,
  };
}

export class QuoteEngine {
  constructor({ targetMargin = UNKNOWN_COST } = {}) { this.targetMargin = targetMargin; }
  createQuote({ request_id, envelope_id, costs = {}, currency = "USD", valid_until }) {
    if (!RESEARCH_ENVELOPES[envelope_id]) throw new Error("INVALID_RESEARCH_ENVELOPE");
    const components = ["search", "external_data", "model", "human", "proof", "runtime", "risk"].map((name) => ({ name, expected: money(costs[name]?.expected), p90: money(costs[name]?.p90) }));
    const known = components.every((item) => item.expected !== UNKNOWN_COST && item.p90 !== UNKNOWN_COST);
    const marginKnown = typeof this.targetMargin === "number" && this.targetMargin >= 0 && this.targetMargin < 1;
    const expected_cost = known ? components.reduce((sum, item) => sum + item.expected, 0) : UNKNOWN_COST;
    const p90_cost = known ? components.reduce((sum, item) => sum + item.p90, 0) : UNKNOWN_COST;
    return {
      schema_version: "SE_GAP_QUOTE_v0.1", quote_id: `SE-QUOTE-${crypto.randomUUID()}`, request_id, envelope_id, created_at: new Date().toISOString(),
      envelope: RESEARCH_ENVELOPES[envelope_id], components, currency, expected_cost, p90_cost,
      target_margin: marginKnown ? this.targetMargin : UNKNOWN_COST,
      minimum_price: known && marginKnown ? Number((p90_cost / (1 - this.targetMargin)).toFixed(2)) : UNKNOWN_COST,
      price_status: known && marginKnown ? "PRICED" : "UNKNOWN_INPUTS", valid_until,
      research_authorized: false, payment_status: "NOT_CONFIRMED",
    };
  }
}

export class DecisionExecutionStore {
  constructor() { this.requests = new Map(); this.events = []; this.deliveries = new Map(); }
  create(input, at = new Date().toISOString()) {
    const id = `SE-DREQ-${crypto.randomUUID()}`;
    const item = { request_id: id, state: "REQUEST_SUBMITTED", visibility: "CUSTOMER_PRIVATE", created_at: at, updated_at: at, input, quote: null, payment: null, rdl_binding: null };
    this.requests.set(id, item); this.events.push({ request_id: id, from: null, to: item.state, at, actor: "REQUESTER", reason: "REQUEST_CREATED" }); return item;
  }
  get(id) { return this.requests.get(id) || null; }
  update(item) { this.requests.set(item.request_id, item); return item; }
  getDelivery(id) { return this.deliveries.get(id) || null; }
  transition(id, to, { actor, reason, at = new Date().toISOString(), details = null } = {}) {
    const item = this.get(id); if (!item) throw new Error("REQUEST_NOT_FOUND");
    if (TERMINAL_STATES.has(item.state) || !(TRANSITIONS[item.state] || []).includes(to)) throw new Error("INVALID_STATE_TRANSITION");
    if (!actor || !reason) throw new Error("ACTOR_AND_REASON_REQUIRED");
    if (["RDL_BOUND", "RESEARCH_IN_PROGRESS"].includes(to) && item.state !== "PAYMENT_CONFIRMED" && item.payment?.status !== "CONFIRMED") throw new Error("PAYMENT_REQUIRED_BEFORE_RESEARCH");
    const from = item.state; item.state = to; item.updated_at = at; this.events.push({ request_id: id, from, to, at, actor, reason, details }); return item;
  }
  confirmPayment(id, { reference, actor, at = new Date().toISOString(), override = false } = {}) {
    const item = this.get(id); if (!item || item.state !== "PAYMENT_PENDING") throw new Error("PAYMENT_NOT_PENDING");
    if (!reference || !actor) throw new Error("PAYMENT_REFERENCE_AND_ACTOR_REQUIRED");
    item.payment = { status: "CONFIRMED", reference, confirmed_at: at, confirmed_by: actor, human_override: override };
    return this.transition(id, "PAYMENT_CONFIRMED", { actor, reason: override ? "RECORDED_HUMAN_OVERRIDE" : "PAYMENT_CONFIRMED", at });
  }
  bindRdl(id, binding, actor) {
    const item = this.get(id); if (!item || item.state !== "PAYMENT_CONFIRMED" || item.payment?.status !== "CONFIRMED") throw new Error("PAYMENT_REQUIRED_BEFORE_RDL_BINDING");
    const required = ["cutoff_at", "envelope_id", "provenance_fields", "cost_caps"];
    if (!required.every((key) => binding?.[key])) throw new Error("INCOMPLETE_RDL_BINDING");
    item.rdl_binding = { ...binding, bound_at: new Date().toISOString() };
    return this.transition(id, "RDL_BOUND", { actor, reason: "PAID_SCOPE_BOUND_TO_RDL" });
  }
}

export class D1DecisionExecutionStore {
  constructor(db) { this.db = db; }
  async create(input, at = new Date().toISOString()) {
    const item = { request_id: `SE-DREQ-${crypto.randomUUID()}`, state: "REQUEST_SUBMITTED", visibility: "CUSTOMER_PRIVATE", created_at: at, updated_at: at, input, quote: null, payment: null, rdl_binding: null };
    await this.db.batch([
      this.db.prepare("INSERT INTO se_decision_requests (request_id, created_at, updated_at, state, visibility, payload_json) VALUES (?, ?, ?, ?, 'CUSTOMER_PRIVATE', ?)").bind(item.request_id, at, at, item.state, JSON.stringify(item)),
      this.db.prepare("INSERT INTO se_decision_events (request_id, event_at, previous_state, new_state, actor, reason, details_json) VALUES (?, ?, NULL, ?, 'REQUESTER', 'REQUEST_CREATED', NULL)").bind(item.request_id, at, item.state),
    ]);
    return item;
  }
  async get(id) {
    const row = await this.db.prepare("SELECT payload_json FROM se_decision_requests WHERE request_id = ?").bind(id).first();
    return row ? JSON.parse(row.payload_json) : null;
  }
  async update(item) {
    item.updated_at = new Date().toISOString();
    const statements = [this.db.prepare("UPDATE se_decision_requests SET updated_at = ?, state = ?, payload_json = ? WHERE request_id = ?").bind(item.updated_at, item.state, JSON.stringify(item), item.request_id)];
    if (item.quote) statements.push(this.db.prepare("INSERT OR REPLACE INTO se_decision_quotes (quote_id, request_id, created_at, valid_until, envelope_id, price_status, payload_json) VALUES (?, ?, ?, ?, ?, ?, ?)").bind(item.quote.quote_id, item.request_id, item.quote.created_at, item.quote.valid_until, item.quote.envelope_id, item.quote.price_status, JSON.stringify(item.quote)));
    await this.db.batch(statements); return item;
  }
  async transition(id, to, { actor, reason, at = new Date().toISOString(), details = null } = {}) {
    const item = await this.get(id); if (!item) throw new Error("REQUEST_NOT_FOUND");
    if (TERMINAL_STATES.has(item.state) || !(TRANSITIONS[item.state] || []).includes(to)) throw new Error("INVALID_STATE_TRANSITION");
    if (!actor || !reason) throw new Error("ACTOR_AND_REASON_REQUIRED");
    if (["RDL_BOUND", "RESEARCH_IN_PROGRESS"].includes(to) && item.state !== "PAYMENT_CONFIRMED" && item.payment?.status !== "CONFIRMED") throw new Error("PAYMENT_REQUIRED_BEFORE_RESEARCH");
    const from = item.state; item.state = to; item.updated_at = at;
    await this.db.batch([
      this.db.prepare("UPDATE se_decision_requests SET updated_at = ?, state = ?, payload_json = ? WHERE request_id = ?").bind(at, to, JSON.stringify(item), id),
      this.db.prepare("INSERT INTO se_decision_events (request_id, event_at, previous_state, new_state, actor, reason, details_json) VALUES (?, ?, ?, ?, ?, ?, ?)").bind(id, at, from, to, actor, reason, details ? JSON.stringify(details) : null),
    ]);
    return item;
  }
  async confirmPayment(id, { reference, actor, at = new Date().toISOString(), override = false } = {}) {
    const item = await this.get(id); if (!item || item.state !== "PAYMENT_PENDING") throw new Error("PAYMENT_NOT_PENDING");
    if (!reference || !actor) throw new Error("PAYMENT_REFERENCE_AND_ACTOR_REQUIRED");
    item.payment = { status: "CONFIRMED", reference, confirmed_at: at, confirmed_by: actor, human_override: override };
    await this.update(item);
    await this.db.prepare("INSERT INTO se_decision_payments (payment_id, request_id, confirmed_at, confirmed_by, human_override, reference) VALUES (?, ?, ?, ?, ?, ?)").bind(`SE-PAY-${crypto.randomUUID()}`, id, at, actor, override ? 1 : 0, reference).run();
    return this.transition(id, "PAYMENT_CONFIRMED", { actor, reason: override ? "RECORDED_HUMAN_OVERRIDE" : "PAYMENT_CONFIRMED", at });
  }
  async bindRdl(id, binding, actor) {
    const item = await this.get(id); if (!item || item.state !== "PAYMENT_CONFIRMED" || item.payment?.status !== "CONFIRMED") throw new Error("PAYMENT_REQUIRED_BEFORE_RDL_BINDING");
    if (!["cutoff_at", "envelope_id", "provenance_fields", "cost_caps"].every((key) => binding?.[key])) throw new Error("INCOMPLETE_RDL_BINDING");
    item.rdl_binding = { ...binding, bound_at: new Date().toISOString() }; await this.update(item);
    return this.transition(id, "RDL_BOUND", { actor, reason: "PAID_SCOPE_BOUND_TO_RDL" });
  }
  async getDelivery(id) {
    const row = await this.db.prepare("SELECT payload_json, proof_json, delivery_hash FROM se_decision_deliveries WHERE request_id = ? ORDER BY created_at DESC LIMIT 1").bind(id).first();
    return row ? { payload: JSON.parse(row.payload_json), proof: JSON.parse(row.proof_json), delivery_hash: row.delivery_hash } : null;
  }
}

export function buildContextFitScope(input) {
  const required = ["decision_context", "jurisdiction", "system_boundary", "requirements"];
  const missing = required.filter((key) => !input?.[key] || (Array.isArray(input[key]) && !input[key].length));
  return { schema_version: "SE_CONTEXT_FIT_SCOPE_v0.1", status: missing.length ? "INPUT_REQUIRED" : "READY_FOR_QUOTE", missing_inputs: missing, architecture_only: true, executed: false, prohibited_output: ["BUY", "ADOPT"] };
}

export function createWatchCycle({ request_id, days, cost_cap, material_candidate = false }) {
  if (![30, 90].includes(days)) throw new Error("WATCH_CYCLE_MUST_BE_30_OR_90_DAYS");
  return { watch_id: `SE-WATCH-${crypto.randomUUID()}`, request_id, days, cost_cap: money(cost_cap), status: "SCHEDULED", deep_research_authorized: material_candidate, escalation_rule: "MATERIAL_CANDIDATE_REQUIRED" };
}

export class CapabilityProviderRegistry {
  constructor() { this.providers = new Map(); }
  register(provider) {
    if (!provider?.provider_id || !["SEARCH", "EXTERNAL_DATA", "MODEL", "HUMAN_REVIEW", "PROOF", "SPECIALIST"].includes(provider.provider_type)) throw new Error("INVALID_PROVIDER");
    this.providers.set(provider.provider_id, { ...provider, performance: provider.completed_tasks > 0 ? provider.performance : UNKNOWN_COST });
  }
  list() { return [...this.providers.values()]; }
}

export function deriveTemporalCanary(record) {
  const points = record.pdre_record.timeline.map((item) => ({ at: item.effective_at, known_at: item.known_at, event: item.event, evidence_refs: item.evidence_refs }));
  const first = Date.parse(points[0]?.at), last = Date.parse(points.at(-1)?.at), elapsedDays = Number.isFinite(first) && Number.isFinite(last) ? Math.max((last - first) / 86_400_000, 0) : null;
  return { event_id: PHASE5B_EVENT_ID, points, state: record.pdre_record.migration_readiness.code, unknown_count: record.pdre_record.unknowns.length,
    evidence_event_rate_per_30_days: elapsedDays > 0 ? Number((points.length / elapsedDays * 30).toFixed(3)) : UNKNOWN_COST,
    state_transition_rate: UNKNOWN_COST, velocity_score: UNKNOWN_COST };
}

export function projectDiscoveryQuestions(inventory) {
  return inventory.dimensions.filter((item) => item.current_state !== "ESTABLISHED").map((item) => ({
    event_id: inventory.event_id, dimension_id: item.dimension_id, question: `What approved evidence would change ${item.dimension_id} from ${item.current_state}?`,
    publication_status: "REVIEW_REQUIRED", auto_publish: false, outbound_enabled: false,
  }));
}

export function deriveUnitEconomics(records) {
  const real = records.filter((item) => !item.internal_canary && !item.human_override);
  const complete = real.filter((item) => ["revenue", "cost"].every((key) => typeof item[key] === "number"));
  return { real_paid_tasks: real.length, measured_tasks: complete.length, revenue: complete.length ? complete.reduce((sum, item) => sum + item.revenue, 0) : UNKNOWN_COST,
    cost: complete.length ? complete.reduce((sum, item) => sum + item.cost, 0) : UNKNOWN_COST,
    gross_margin: complete.length ? complete.reduce((sum, item) => sum + item.revenue - item.cost, 0) : UNKNOWN_COST,
    internal_canaries_excluded: records.length - real.length };
}

export function captureEstimateVsActual({ quote, actual = {} }) {
  const actualComponents = Object.fromEntries(["search", "external_data", "model", "human", "proof", "runtime", "risk"].map((name) => [name, money(actual[name])]));
  const values = Object.values(actualComponents), actualKnown = values.every((value) => value !== UNKNOWN_COST);
  const actual_cost = actualKnown ? values.reduce((sum, value) => sum + value, 0) : UNKNOWN_COST;
  return { quote_id: quote.quote_id, expected_cost: quote.expected_cost, p90_cost: quote.p90_cost, actual_components: actualComponents, actual_cost,
    variance_to_expected: actualKnown && typeof quote.expected_cost === "number" ? Number((actual_cost - quote.expected_cost).toFixed(2)) : UNKNOWN_COST,
    measurement_status: actualKnown ? "OBSERVED" : "INCOMPLETE" };
}

export async function createDeterminationDelivery({ request, determination, recordHash, cutoffAt }) {
  if (!request?.rdl_binding || !request?.payment || request.payment.status !== "CONFIRMED") throw new Error("VERIFIED_PAID_RDL_BINDING_REQUIRED");
  const payload = { schema_version: "SE_GAP_DETERMINATION_v0.1", request_id: request.request_id, determination, canonical_record_hash: recordHash, cutoff_at: cutoffAt,
    evidence_refs: determination.evidence_refs || [], counter_evidence: determination.counter_evidence || [], unknowns: determination.unknowns || [], limitations: determination.limitations || [], favorable_result_guaranteed: false };
  const proof = await new SnapshotChainProvider().createProof({ subject: { request_id: request.request_id }, current_state: payload, change_history: [], supporting_evidence: payload.evidence_refs, counter_evidence: payload.counter_evidence, open_unknowns: payload.unknowns, branches: [], outcomes: [], rdl_history: [request.rdl_binding] });
  const delivery_hash = await objectHash(payload);
  const html = `<article data-delivery-hash="${delivery_hash}"><h1>Gap determination</h1><p>${escapeHtml(String(determination.statement || "UNKNOWN"))}</p><h2>Unknowns</h2><ul>${payload.unknowns.map((item) => `<li>${escapeHtml(String(item))}</li>`).join("")}</ul><p>Cutoff: ${escapeHtml(cutoffAt)}</p><p>No favorable result is guaranteed.</p></article>`;
  return { payload, html, delivery_hash, proof };
}
function escapeHtml(value) { return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;"); }

export function validateSecretTransport(value) { return typeof value === "string" && value.length >= 40 && value.length <= 256 && ASCII.test(value); }
