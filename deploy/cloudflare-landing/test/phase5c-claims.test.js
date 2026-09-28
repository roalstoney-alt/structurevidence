import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import CANONICAL_800V_RECORD from "../../../technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json" with { type: "json" };
import FIELD_DEPLOYMENT_RDL_RECORD from "../../../rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json" with { type: "json" };
import { build800vPublicClaim, CLAIM_ID, CLAIM_RESULTS, CLAIM_SLUG, EXTERNAL_SEARCH_BEFORE_PAYMENT, matchClaimLibrary, normalizeClaim, routeClaimIntake, selectClaimVersion, STOP_STATES } from "../phase5c-claims.js";
import { createWorker } from "../worker.js";

const env = { SE_CLAIM_STOP_POINT: "1" };
const baseInput = { claim: "Qualifying public evidence establishes named commercial field operation of the defined 800VDC data-center power architecture.", decision_context: "Technical selection record", use_deadline: "2026-10-15", known_materials_or_sources: "" };
const claimLibrary = await build800vPublicClaim(CANONICAL_800V_RECORD, FIELD_DEPLOYMENT_RDL_RECORD);

test("ClaimNormalizationProjection preserves raw wording and deterministically resolves the canary", () => {
  const projection = normalizeClaim(baseInput);
  assert.equal(projection.raw_claim, baseInput.claim); assert.equal(projection.subject, "800VDC_DATA_CENTER_POWER_ARCHITECTURE");
  assert.equal(projection.predicate, "NAMED_COMMERCIAL_OR_FIELD_OPERATION"); assert.equal(projection.falsifiable, true); assert.equal(projection.external_retrieval, 0);
});

test("missing claim, context, or deadline returns without research", () => {
  for (const field of ["claim", "decision_context", "use_deadline"]) {
    const result = routeClaimIntake({ ...baseInput, [field]: "" }, claimLibrary);
    assert.equal(result.result, "INSUFFICIENT_INPUT"); assert.equal(result.research_started, false); assert.equal(result.external_search, 0); assert.ok(result.missing.includes(field));
  }
});

test("non-falsifiable wording returns one decomposition draft and performs no verification", () => {
  const result = routeClaimIntake({ ...baseInput, claim: "800VDC will dominate data centers." }, claimLibrary);
  assert.equal(result.result, "NON_FALSIFIABLE_RETURN"); assert.equal(result.decomposition.type, "CLAIM_DECOMPOSITION_DRAFT");
  assert.equal(result.decomposition.external_verification_started, false); assert.equal(result.external_search, 0);
});

test("library-first exact and isomorphic matches return the current Stop-Point at zero retrieval cost", () => {
  const exact = routeClaimIntake(baseInput, claimLibrary);
  assert.equal(exact.result, "EXISTING_STOP_POINT"); assert.equal(exact.match.match_type, "EXACT_MATCH"); assert.equal(exact.claim.claim_id, CLAIM_ID);
  const isomorphic = matchClaimLibrary(normalizeClaim({ ...baseInput, claim: "A named 800VDC field deployment record establishes commercial operation." }));
  assert.equal(isomorphic.match_type, "ISOMORPHIC_MATCH"); assert.equal(isomorphic.retrieval_cost, 0); assert.equal(isomorphic.external_search_performed, false);
});

test("new falsifiable claims reach bounded quote state without deep research or payment", () => {
  const result = routeClaimIntake({ ...baseInput, claim: "A named 800VDC operating history record establishes reliability duration of twelve months.", decision_context: "Credit underwriting material" }, claimLibrary);
  assert.equal(result.result, "NEW_VERIFIABLE_CLAIM_QUOTE"); assert.equal(result.quote.QUERY_LIMIT, 4); assert.equal(result.quote.EXTERNAL_DATA_CAP, 0);
  assert.equal(result.quote.payment_confirmed, false); assert.equal(result.quote.new_external_retrieval, 0); assert.equal(result.research_started, false);
});

test("PublicClaimProjection has stable ID, versioned as_of history, and controlled states", () => {
  assert.equal(claimLibrary.claim_id, CLAIM_ID); assert.equal(claimLibrary.stable_claim_slug, CLAIM_SLUG); assert.equal(claimLibrary.versions.length, 2);
  assert.equal(selectClaimVersion(claimLibrary, "2026-08-01").version, 1); assert.equal(selectClaimVersion(claimLibrary).version, 2);
  assert.equal(selectClaimVersion(claimLibrary, "2026-08-01").stop_point.STATE, "UNKNOWN"); assert.equal(selectClaimVersion(claimLibrary).stop_point.STATE, "ATTRIBUTABLE_ONLY");
  for (const version of claimLibrary.versions) { assert.ok(STOP_STATES.includes(version.stop_point.STATE)); assert.match(version.projection_hash, /^[a-f0-9]{64}$/); }
});

test("Stop-Point key order binds SUPPORTS and DOES_NOT_SUPPORT into a complete boundary", () => {
  const stop = selectClaimVersion(claimLibrary).stop_point;
  assert.deepEqual(Object.keys(stop).slice(0, 18), ["CLAIM", "SCOPE", "AS_OF", "FRESHNESS_STATUS", "STATE", "SUPPORTS", "DOES_NOT_SUPPORT", "QUALIFYING_RECORDS", "REJECTED_OR_COUNTER", "SEARCH_PROVENANCE", "SOURCE_ACCESS_STATUS", "DIRECT_INQUIRY_STATUS", "VERIFICATION_DEPTH", "OPEN_GAP_IF_UNKNOWN", "NEXT_MINIMUM_VERIFICATION", "NOT_A", "CLAIM_ID", "VERSION"]);
  assert.ok(stop.SUPPORTS.length); assert.ok(stop.DOES_NOT_SUPPORT.length); assert.equal(stop.boundary_complete, true);
});

test("anti-upgrade boundary persists canonical gaps and rejects R4 to R5 escalation", () => {
  const text = selectClaimVersion(claimLibrary).stop_point.DOES_NOT_SUPPORT.join(" ");
  for (const phrase of ["Industry-wide adoption", "Multi-operator replication", "Long-term operating reliability", "Economic superiority", "canonical R4→R5 transition"]) assert.match(text, new RegExp(phrase, "i"));
});

test("local claim routes fail closed outside localhost feature flag", async () => {
  const worker = createWorker();
  assert.equal((await worker.fetch(new Request(`https://structevidence.com/claims/${CLAIM_SLUG}`), env)).status, 404);
  assert.equal((await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}`), {})).status, 404);
  assert.equal((await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}`), env)).status, 200);
});

test("HTML, embedded machine object, and JSON endpoint preserve one semantic Stop-Point", async () => {
  const worker = createWorker();
  const html = await (await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}`), env)).text();
  const machine = JSON.parse(html.match(/<script type="application\/ld\+json">([^<]+)<\/script>/)[1]);
  const endpoint = await (await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}.json`), env)).json();
  assert.deepEqual(machine, endpoint); assert.equal(machine.boundary_complete, true); assert.match(html, /Any summary that drops DOES_NOT_SUPPORT is incomplete/);
});

test("EN, ZH-CN, and ES preserve claim ID, State, evidence refs, as_of, version, and hash", async () => {
  const worker = createWorker(), semantic = [];
  for (const lang of ["EN", "ZH-CN", "ES"]) {
    const html = await (await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}?lang=${lang}`), env)).text();
    if (lang === "ZH-CN") assert.match(html, /停止点|支持范围/);
    if (lang === "ES") assert.match(html, /PUNTO DE PARADA|RESPALDA/);
    const item = JSON.parse(html.match(/<script type="application\/ld\+json">([^<]+)<\/script>/)[1]);
    semantic.push([item.claim_id, item.STATE, item.canonical_evidence_refs, item.AS_OF, item.version, item.projection_hash]);
  }
  assert.deepEqual(semantic[0], semantic[1]); assert.deepEqual(semantic[1], semantic[2]);
});

test("PublicClaimProjection schema freezes required paired-boundary fields", () => {
  const schema = JSON.parse(readFileSync(new URL("../../../schemas/se-frr/public-claim-projection.schema.json", import.meta.url), "utf8"));
  assert.equal(schema.title, "PublicClaimProjection"); assert.ok(schema.required.includes("SUPPORTS")); assert.ok(schema.required.includes("DOES_NOT_SUPPORT")); assert.equal(schema.properties.boundary_complete.const, true);
});

test("claim request response keeps private decision context out of public projection", async () => {
  const worker = createWorker();
  const response = await worker.fetch(new Request("http://127.0.0.1/claim-requests", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ ...baseInput, decision_context: "CONFIDENTIAL COMPANY PROCUREMENT" }) }), env);
  assert.equal(response.status, 201); const body = await response.json(); assert.equal(body.data.private_context_published, false);
  const publicJson = JSON.stringify(await (await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}.json`), env)).json());
  assert.doesNotMatch(publicJson, /CONFIDENTIAL COMPANY PROCUREMENT/);
});

test("UNKNOWN is a valid historical delivery rather than failure", () => {
  const historical = selectClaimVersion(claimLibrary, "2026-08-01");
  assert.equal(historical.stop_point.STATE, "UNKNOWN"); assert.equal(historical.stop_point.boundary_complete, true); assert.ok(historical.stop_point.OPEN_GAP_IF_UNKNOWN.length);
});

test("local payment endpoint is disabled and cannot authorize retrieval", async () => {
  const worker = createWorker();
  const created = await (await worker.fetch(new Request("http://127.0.0.1/claim-requests", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(baseInput) }), env)).json();
  const payment = await worker.fetch(new Request(`http://127.0.0.1/claim-requests/${created.data.request_id}/confirm-payment`, { method: "POST" }), env);
  assert.equal(payment.status, 409); const body = await payment.json(); assert.equal(body.payment_confirmed, false); assert.equal(body.new_external_retrieval, 0);
});

test("zero demand performs zero research and no proactive acquisition or content factory exists", () => {
  assert.equal(EXTERNAL_SEARCH_BEFORE_PAYMENT, 0); assert.deepEqual(CLAIM_RESULTS, ["EXISTING_STOP_POINT", "NEW_VERIFIABLE_CLAIM_QUOTE", "CONTEXT_MAPPING_QUOTE", "NON_FALSIFIABLE_RETURN", "INSUFFICIENT_INPUT"]);
  const sources = ["../phase5c-claims.js", "../phase5c-claim-surface.js"].map((path) => readFileSync(new URL(path, import.meta.url), "utf8")).join("\n");
  assert.doesNotMatch(sources, /lead discovery|buyer intent|customer prospecting|forum prospecting|auto-generated videos/i);
  assert.doesNotMatch(sources, /fetch\([^)]*(google|bing|search|anthropic|openai)/i);
});

test("Temporal visualization is present only as a secondary explanation layer", async () => {
  const html = await (await createWorker().fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}`), env)).text();
  assert.ok(html.indexOf("STOP-POINT") < html.indexOf("HOW THIS STATE CHANGED")); assert.match(html, /secondary explanation layer/i);
});
