import assert from "node:assert/strict";
import test from "node:test";
import RDL from "../../../rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json" with { type: "json" };
import CANONICAL from "../../../technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json" with { type: "json" };
import { build800vPublicClaim, CLAIM_SLUG, matchClaimLibrary, normalizeClaim, routeClaimIntake } from "../phase5c-claims.js";
import { assessFreshness, atomicClaimGate, claimScopeFingerprint, classifySourceAccess, createConflictedDetermination, createDirectInquiryDraft, createNotFoundWithinScope, createPrivateStopPoint, createSearchProvenance, enforceResearchEnvelope, evidenceLineageSummary, lateEvidenceRecord, mapCanonicalToPublicState, PROVENANCE_CLASSES, publicPromotionGate, publicSearchProvenance, recordDirectInquiryResponse, recordDirectInquirySend, STOP_POINT_FIELD_ORDER, STOP_REASONS, validateResearchCycle, VERIFICATION_DEPTHS } from "../phase5c-spv.js";
import { createWorker } from "../worker.js";

const library = await build800vPublicClaim(CANONICAL, RDL);
const env = { SE_CLAIM_STOP_POINT: "1" };
const baseInput = { claim: "Qualifying public evidence establishes named commercial field operation of the defined 800VDC data-center power architecture.", decision_context: "Technical selection record", use_deadline: "2026-10-15" };

test("Stop-Point v2 binds scope, state, supports, and anti-upgrade boundary", () => {
  const stop = library.versions.at(-1).stop_point;
  assert.deepEqual(Object.keys(stop).slice(0, 18), STOP_POINT_FIELD_ORDER);
  assert.equal(stop.determination.state, stop.STATE);
  assert.deepEqual(stop.determination.supports, stop.SUPPORTS);
  assert.deepEqual(stop.determination.does_not_support, stop.DOES_NOT_SUPPORT);
  assert.equal(stop.boundary_complete, true);
  for (const field of ["subject", "technical_boundary", "deployment_class", "jurisdiction", "attribution_scope", "time_boundary", "population_scope"]) assert.ok(stop.SCOPE[field]);
});

test("NOT_FOUND_WITHIN_SCOPE explicitly refuses a non-existence conclusion", () => {
  const provenance = { actual_query_count: 4, actual_source_count: 9, qualifying_results: 0, stop_reason: "RESEARCH_ENVELOPE_EXHAUSTED" };
  const determination = createNotFoundWithinScope({ subject: "X" }, provenance);
  assert.equal(determination.state, "NOT_FOUND_WITHIN_SCOPE");
  assert.match(determination.supports[0], /within the documented scope/i);
  assert.match(determination.does_not_support[0], /does not establish.*does not exist/i);
  assert.equal(mapCanonicalToPublicState("UNKNOWN", { search_complete: true, qualifying_results: 0, actual_query_count: 4, actual_source_count: 9, stop_reason: "RESEARCH_ENVELOPE_EXHAUSTED" }), "NOT_FOUND_WITHIN_SCOPE");
  assert.equal(mapCanonicalToPublicState("UNKNOWN", { search_complete: true, qualifying_results: 0 }), "UNKNOWN");
  assert.throws(() => createNotFoundWithinScope({ subject: "X" }, { query_count: "UNKNOWN", source_count: "UNKNOWN", qualifying_count: 0, stop_reason: "HUMAN_STOP" }), /COMPLETED_RECORDED_SEARCH/);
});

test("CONFLICTED preserves both sides and the unresolved next action", () => {
  const value = createConflictedDetermination({ supporting: ["Primary record says A"], counter: ["Independent test says not-A"], conflict: "Different operating boundary", next: "Repeat under one defined boundary" });
  assert.equal(value.state, "CONFLICTED"); assert.ok(value.supports.length); assert.ok(value.does_not_support.length); assert.ok(value.next_minimum_verification);
});

test("atomic claim gate decomposes deployment plus cost plus reliability before research", () => {
  const compound = "800VDC is commercially deployed, cheaper and more reliable.";
  assert.equal(atomicClaimGate(compound).ATOMIC_CLAIM_REQUIRED, "FAIL");
  const routed = routeClaimIntake({ ...baseInput, claim: compound }, library);
  assert.equal(routed.result, "NON_FALSIFIABLE_RETURN"); assert.equal(routed.research_started, false); assert.equal(routed.external_search, 0);
});

test("ClaimScopeFingerprint gives exact/isomorphic/partial protection without embeddings", () => {
  const exact = normalizeClaim(baseInput), partial = normalizeClaim({ ...baseInput, claim: "An 800VDC operating history record establishes twelve-month reliability." });
  assert.deepEqual(Object.keys(claimScopeFingerprint(exact)), ["subject", "predicate", "object", "technical_scope", "jurisdiction", "deployment_class", "attribution_scope", "time_boundary", "population_scope"]);
  assert.equal(matchClaimLibrary(exact).match_type, "EXACT_MATCH");
  assert.equal(matchClaimLibrary(partial).match_type, "PARTIAL_MATCH");
});

test("SearchProvenance persists only observed counts and keeps unknown different from zero", async () => {
  const protectedLog = await createSearchProvenance(RDL), publicLog = publicSearchProvenance(protectedLog);
  assert.equal(protectedLog.actual_query_count, 4); assert.equal(protectedLog.actual_source_count, 9); assert.equal(protectedLog.actual_deep_review_count, 1);
  assert.equal(protectedLog.qualifying_results, 1); assert.equal(protectedLog.results_rejected, 8); assert.equal(protectedLog.restricted_sources, "UNKNOWN"); assert.notEqual(protectedLog.restricted_sources, 0);
  assert.ok(STOP_REASONS.includes(protectedLog.stop_reason)); assert.match(protectedLog.search_hash, /^[a-f0-9]{64}$/);
  assert.equal("queries_executed" in publicLog, false); assert.equal(publicLog.query_count, 4);
});

test("source-controlled operating-history request quotes direct written inquiry without research", () => {
  const result = routeClaimIntake({ ...baseInput, claim: "A named 800VDC operating history record establishes reliability duration of twelve months." }, library);
  assert.equal(result.quote.VERIFICATION_MODE, "SOURCE_CONTROLLED_INFORMATION");
  assert.equal(result.quote.NEXT_MINIMUM_VERIFICATION, "DIRECT_WRITTEN_INQUIRY"); assert.equal(result.research_started, false);
});

test("direct inquiry draft cannot become sent without human approval and delivery evidence", async () => {
  const draft = await createDirectInquiryDraft({ claim_id: "SE-CLAIM-1", rdl_run_id: "RDL-1", target_organization: "Operator", target_role_or_department: "Operations", question: "Provide dated record", response_deadline: "2026-10-15" });
  assert.equal(draft.response_status, "NOT_SENT"); assert.equal(draft.auto_send, false);
  await assert.rejects(() => recordDirectInquirySend(draft, { sent_at: new Date().toISOString(), delivery_status: "DELIVERY_CONFIRMED", human_approved: true }), /DELIVERY_EVIDENCE/);
  const sent = await recordDirectInquirySend(draft, { sent_at: new Date().toISOString(), channel: "EMAIL", delivery_status: "DELIVERY_CONFIRMED", delivery_evidence_ref: "MESSAGE-ID:REDACTED", human_approved: true });
  const noResponse = await recordDirectInquiryResponse(sent, { response_status: "NO_RESPONSE_BY_CUTOFF", response_received_at: null, response_summary: null });
  assert.equal(noResponse.claim_state_effect, "NEUTRAL"); assert.match(noResponse.response_hash, /^[a-f0-9]{64}$/);
});

test("VerificationDepth describes process depth and never confidence", () => {
  assert.deepEqual(VERIFICATION_DEPTHS, ["V0_LIBRARY_ONLY", "V1_PUBLIC_SEARCH", "V2_PRIMARY_SOURCE_SEARCH", "V3_RESTRICTED_OR_PAID_SOURCE_CHECK", "V4_DIRECT_WRITTEN_INQUIRY", "V5_INDEPENDENT_THIRD_PARTY_VERIFICATION"]);
  assert.equal(JSON.stringify(library).includes("confidence"), false);
});

test("source access, freshness, and customer material provenance remain controlled classifications", () => {
  assert.equal(classifySourceAccess("SOURCE_CONTROLLED"), "SOURCE_CONTROLLED");
  assert.throws(() => classifySourceAccess("HIGH_QUALITY"), /INVALID_SOURCE_ACCESS_STATUS/);
  assert.equal(assessFreshness("2026-01-01T00:00:00Z", null), "UNASSESSED");
  assert.equal(assessFreshness("2026-09-20T00:00:00Z", { current_days: 30, stale_days: 90 }, "2026-09-27T00:00:00Z"), "CURRENT");
  assert.ok(PROVENANCE_CLASSES.includes("CUSTOMER_PROVIDED_UNVERIFIED"));
  assert.notEqual("CUSTOMER_PROVIDED_UNVERIFIED", "CUSTOMER_PROVIDED_VERIFIED");
});

test("late old evidence preserves published reality time and later knowledge time", () => {
  const record = lateEvidenceRecord({ published_at: "2025-06-01T00:00:00Z", effective_at: "2025-06-01T00:00:00Z", observed_at: "2027-01-01T00:00:00Z", recorded_at: "2027-01-02T00:00:00Z" });
  assert.equal(record.historical_state_rewritten, false); assert.notEqual(record.published_at, record.observed_at);
});

test("lineage dedupe prevents syndicated copies and AI summaries multiplying origins", () => {
  const records = [{ id: "vendor", origin_id: "origin-1", independence_class: "PRIMARY_ORIGIN" }, ...Array.from({ length: 20 }, (_, i) => ({ id: `copy-${i}`, origin_id: "origin-1", independence_class: "SYNDICATED_COPY" })), ...Array.from({ length: 100 }, (_, i) => ({ id: `ai-${i}`, origin_id: "origin-1", independence_class: "AI_SUMMARY" }))];
  assert.deepEqual(evidenceLineageSummary(records), { DOCUMENT_COUNT: 121, INDEPENDENT_ORIGIN_COUNT: 1, INDEPENDENT_CONFIRMATION_COUNT: 0 });
});

test("private Stop-Point remains isolated until every public promotion gate passes", () => {
  const privateStop = createPrivateStopPoint(library.versions.at(-1).stop_point, { provenance_class: "CUSTOMER_PROVIDED_UNVERIFIED" });
  assert.equal(privateStop.public_library_eligible, false);
  assert.equal(publicPromotionGate({ provenance_validation: true, privacy_validation: true, license_validation: true, human_acceptance: false }).promoted, false);
  assert.equal(publicPromotionGate({ provenance_validation: true, privacy_validation: true, license_validation: true, human_acceptance: true, customer_authorization: true }).promoted, true);
});

test("paid cycles require cutoff and hard caps; payment buys process only", () => {
  assert.equal(validateResearchCycle({ query_limit: 4, source_limit: 10, deep_review_limit: 1, external_data_cap: 0, deadline: "2099-01-01T00:00:00Z" }).reason, "CUTOFF_REQUIRED");
  const cycle = validateResearchCycle({ query_limit: 4, source_limit: 10, deep_review_limit: 1, external_data_cap: 0, deadline: "2099-01-01T00:00:00Z", cutoff: "2098-12-31T23:59:59Z" });
  assert.equal(cycle.hard_cap, true); assert.equal(cycle.payment_buys_process, true); assert.equal(cycle.payment_buys_preferred_outcome, false);
  const stopped = enforceResearchEnvelope({ query_limit: 4, source_limit: 10, deep_review_limit: 2, external_data_cap: 0 }, { query_count: 4, source_count: 9, deep_review_count: 1, external_data_cost: 0 });
  assert.equal(stopped.continue_research, false); assert.equal(stopped.stop_reason, "RESEARCH_ENVELOPE_EXHAUSTED"); assert.equal(stopped.next_cycle_requires_new_quote, true);
});

test("local verification and protected-like provenance/inquiry routes exist without automatic send", async () => {
  const worker = createWorker();
  assert.equal((await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}/verification`), env)).status, 200);
  const created = await (await worker.fetch(new Request("http://127.0.0.1/claim-requests", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(baseInput) }), env)).json();
  const id = created.data.request_id;
  const provenance = await (await worker.fetch(new Request(`http://127.0.0.1/claim-requests/${id}/search-provenance`), env)).json();
  assert.equal(provenance.private_queries_published, false); assert.equal(provenance.data.query_count, 4);
  const draft = await (await worker.fetch(new Request(`http://127.0.0.1/claim-requests/${id}/direct-inquiry/draft`, { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }), env)).json();
  assert.equal(draft.automatic_send_performed, false); assert.equal(draft.data.response_status, "NOT_SENT");
});
