import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createWorker } from "../worker.js";
import { PHASE5B_800V_INVENTORY } from "../phase5b-800v-canary.js";
import {
  CapabilityProviderRegistry, DecisionExecutionStore, QuoteEngine, RESEARCH_ENVELOPES,
  buildContextFitScope, captureEstimateVsActual, createDeterminationDelivery, createWatchCycle, deriveTemporalCanary,
  deriveUnitEconomics, preflightGapVerification, project800vDecisionInventory,
  projectDecisionEventFromInventory, projectDiscoveryQuestions,
} from "../phase5b-core.js";

const recordUrl = new URL("../../../technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json", import.meta.url);
const record = JSON.parse(readFileSync(recordUrl, "utf8"));
const input = { claim: "The 800VDC path has sustained operating history.", decision_context: "Infrastructure migration gate.", decision_deadline: "2026-12-31", dimension_id: "OPERATING_HISTORY" };

test("800V Decision Inventory is derived from the canonical record without upgrading field deployment", async () => {
  const inventory = project800vDecisionInventory(record);
  assert.deepEqual(inventory, PHASE5B_800V_INVENTORY);
  assert.equal(inventory.dimensions.length, 6);
  assert.equal(inventory.dimensions.find((item) => item.dimension_id === "FIELD_DEPLOYMENT").current_state, "NOT_ESTABLISHED");
  assert.equal(inventory.dimensions.find((item) => item.dimension_id === "OPERATING_HISTORY").current_state, "UNKNOWN");
  assert.ok(inventory.dimensions.every((item) => !("confidence" in item)));
  const event = await projectDecisionEventFromInventory(inventory);
  assert.equal(event.canonical_storage_created, false); assert.equal(event.proof.proof_level, "P1_SNAPSHOT_CHAIN");
});

test("preflight is bounded and research envelopes enforce hard caps", () => {
  const result = preflightGapVerification(input, PHASE5B_800V_INVENTORY);
  assert.equal(result.discovery_queries_used, 0); assert.equal(result.deep_research_performed, false); assert.equal(result.recommended_envelope, "G2");
  assert.deepEqual(RESEARCH_ENVELOPES.G1, { queries_max: 4, sources_max: 10, deep_reviews_max: 1, paid_data: false, specialist_review: false });
  assert.equal(RESEARCH_ENVELOPES.G3.queries_max, 15); assert.equal(RESEARCH_ENVELOPES.G3.deep_reviews_max, 5);
  assert.throws(() => preflightGapVerification({ ...input, hidden: "not allowed" }, PHASE5B_800V_INVENTORY), /INVALID_PREFLIGHT_INPUT/);
});

test("QuoteEngine propagates UNKNOWN and computes price only from configured complete inputs", () => {
  const unknown = new QuoteEngine().createQuote({ request_id: "R1", envelope_id: "G2", valid_until: "2026-10-01" });
  assert.equal(unknown.minimum_price, "UNKNOWN"); assert.equal(unknown.research_authorized, false);
  const costs = Object.fromEntries(["search", "external_data", "model", "human", "proof", "runtime", "risk"].map((name) => [name, { expected: 1, p90: 2 }]));
  const priced = new QuoteEngine({ targetMargin: 0.3 }).createQuote({ request_id: "R2", envelope_id: "G1", costs, valid_until: "2026-10-01" });
  assert.equal(priced.expected_cost, 7); assert.equal(priced.p90_cost, 14); assert.equal(priced.minimum_price, 20);
  assert.equal(captureEstimateVsActual({ quote: priced, actual: { search: 1 } }).actual_cost, "UNKNOWN");
  const observed = captureEstimateVsActual({ quote: priced, actual: Object.fromEntries(Object.keys(costs).map((name) => [name, 1])) });
  assert.equal(observed.actual_cost, 7); assert.equal(observed.variance_to_expected, 0);
});

test("payment gate blocks RDL and research until a recorded confirmation", () => {
  const store = new DecisionExecutionStore(), item = store.create(input, "2026-09-27T00:00:00Z");
  assert.throws(() => store.bindRdl(item.request_id, {}, "operator"), /PAYMENT_REQUIRED/);
  store.transition(item.request_id, "PREFLIGHT_COMPLETE", { actor: "operator", reason: "TEST_PREFLIGHT" });
  store.transition(item.request_id, "QUOTE_ISSUED", { actor: "operator", reason: "TEST_QUOTE" });
  store.transition(item.request_id, "QUOTE_ACCEPTED", { actor: "requester", reason: "TEST_ACCEPT" });
  store.transition(item.request_id, "PAYMENT_PENDING", { actor: "operator", reason: "TEST_PAYMENT_REQUEST" });
  assert.throws(() => store.transition(item.request_id, "RESEARCH_IN_PROGRESS", { actor: "operator", reason: "TEST" }), /INVALID_STATE_TRANSITION|PAYMENT_REQUIRED/);
  store.confirmPayment(item.request_id, { reference: "TEST-NONCOMMERCIAL", actor: "operator", override: true });
  store.bindRdl(item.request_id, { cutoff_at: "2026-09-27T00:00:00Z", envelope_id: "G1", provenance_fields: ["effective_at", "known_at"], cost_caps: RESEARCH_ENVELOPES.G1 }, "operator");
  assert.equal(item.state, "RDL_BOUND"); assert.equal(item.payment.human_override, true); assert.equal(store.events.length, 7);
});

test("one determination object renders JSON and HTML with matching hash and P1 proof", async () => {
  const store = new DecisionExecutionStore(), item = store.create(input);
  for (const [to, actor, reason] of [["PREFLIGHT_COMPLETE", "op", "P"], ["QUOTE_ISSUED", "op", "Q"], ["QUOTE_ACCEPTED", "customer", "A"], ["PAYMENT_PENDING", "op", "PENDING"]]) store.transition(item.request_id, to, { actor, reason });
  store.confirmPayment(item.request_id, { reference: "TEST-NONCOMMERCIAL", actor: "op" });
  store.bindRdl(item.request_id, { cutoff_at: "2026-09-27T00:00:00Z", envelope_id: "G1", provenance_fields: ["effective_at", "known_at"], cost_caps: RESEARCH_ENVELOPES.G1 }, "op");
  const delivery = await createDeterminationDelivery({ request: item, recordHash: record.core.record_hash, cutoffAt: "2026-09-27T00:00:00Z", determination: { statement: "UNKNOWN", evidence_refs: [], counter_evidence: record.pdre_record.counter_evidence, unknowns: ["Operating history."], limitations: ["No deep research executed in internal canary."] } });
  assert.match(delivery.html, new RegExp(delivery.delivery_hash)); assert.equal(delivery.payload.determination.statement, "UNKNOWN"); assert.equal(delivery.proof.proof_level, "P1_SNAPSHOT_CHAIN");
});

test("context, watch, provider, temporal, discovery, and economics canaries preserve boundaries", () => {
  assert.deepEqual(buildContextFitScope({}).missing_inputs, ["decision_context", "jurisdiction", "system_boundary", "requirements"]);
  assert.equal(buildContextFitScope({ decision_context: "x", jurisdiction: "x", system_boundary: "x", requirements: ["x"] }).executed, false);
  assert.equal(createWatchCycle({ request_id: "R", days: 30, cost_cap: "UNKNOWN" }).deep_research_authorized, false);
  assert.throws(() => createWatchCycle({ request_id: "R", days: 60 }), /30_OR_90/);
  const registry = new CapabilityProviderRegistry(); registry.register({ provider_id: "P1", provider_type: "SEARCH", completed_tasks: 0, performance: 1 });
  assert.equal(registry.list()[0].performance, "UNKNOWN");
  const temporal = deriveTemporalCanary(record); assert.equal(temporal.points.length, 5); assert.equal(temporal.velocity_score, "UNKNOWN"); assert.equal(temporal.state_transition_rate, "UNKNOWN");
  assert.ok(projectDiscoveryQuestions(PHASE5B_800V_INVENTORY).every((item) => item.publication_status === "REVIEW_REQUIRED" && !item.auto_publish && !item.outbound_enabled));
  assert.deepEqual(deriveUnitEconomics([{ internal_canary: true, revenue: 100, cost: 1 }]), { real_paid_tasks: 0, measured_tasks: 0, revenue: "UNKNOWN", cost: "UNKNOWN", gross_margin: "UNKNOWN", internal_canaries_excluded: 1 });
});

test("public gaps and event routes work while decision routes require protected access", async () => {
  const denied = createWorker({ decisionStore: new DecisionExecutionStore(), authVerifier: null });
  assert.equal((await denied.fetch(new Request("https://structevidence.com/api/v1/decision-requests", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(input) }), {})).status, 403);
  const store = new DecisionExecutionStore(), worker = createWorker({ decisionStore: store, authVerifier: async () => ({ email: "operator@example.test" }) });
  const gaps = await worker.fetch(new Request("https://structevidence.com/api/v1/events/SE-EVENT-800001/gaps"), {}); assert.equal(gaps.status, 200); assert.equal((await gaps.json()).data.dimensions.length, 6);
  const event = await worker.fetch(new Request("https://structevidence.com/api/v1/events/SE-EVENT-800001"), {}); assert.equal(event.status, 200); assert.equal((await event.json()).data.current_state.state_code, "R3");
  const created = await worker.fetch(new Request("https://structevidence.com/api/v1/decision-requests", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(input) }), {});
  assert.equal(created.status, 201); const createdBody = await created.json(); assert.equal(createdBody.data.state, "REQUEST_SUBMITTED");
  const status = await worker.fetch(new Request(`https://structevidence.com/api/v1/decision-requests/${createdBody.data.request_id}/status`), {}); assert.equal(status.status, 200);
});

test("RDL Cost Baseline #001 keeps observed credits separate from unknown money", () => {
  const baseline = JSON.parse(readFileSync(new URL("../../../data/se-frr/RDL_COST_BASELINE_001.json", import.meta.url), "utf8"));
  assert.equal(baseline.account_credit_delta, 37); assert.equal(baseline.usd_cost, "UNKNOWN"); assert.equal(baseline.currency_conversion_performed, false);
});
