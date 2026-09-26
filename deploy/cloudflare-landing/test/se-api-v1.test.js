import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createWorker } from "../worker.js";
import { API_VERSION, MemorySeApiStore } from "../se-api-v1.js";

const fixtureRoot = new URL("../../../tests/se_frr/fixtures/", import.meta.url);
const read = (path) => JSON.parse(readFileSync(new URL(path, fixtureRoot), "utf8"));
const publicData = {
  subjects: [read("subjects/SE-SUBJ-000001.json")],
  states: [read("states/SE-ST-20260925-000001.json"), read("states/SE-ST-20260925-000002.json")],
  changes: [read("changes/SE-CHG-20260925-000001.json")],
  evidence: [1, 2, 3, 4, 5].map((n) => read(`evidence/SE-EV-20260925-${String(n).padStart(6, "0")}.json`)),
  branches: [1, 2].map((n) => read(`branches/SE-BR-20260925-${String(n).padStart(6, "0")}.json`)),
  outcomes: [read("outcomes/SE-OUT-20260925-000002.json")],
};
class Limiter { async limit() { return { success: true }; } }
const env = { PUBLIC_ORIGINS: "https://structevidence.com", PUBLIC_INTAKE_RATE_LIMITER: new Limiter(), TEAM_DOMAIN: "https://team.cloudflareaccess.com", ADMIN_API_AUD: "api-aud", ADMIN_EMAILS: "admin@example.com" };
const store = new MemorySeApiStore();
const authorized = async (_request, _env, audience) => {
  if (audience !== "api-aud") throw new Response("Invalid Access audience", { status: 403 });
  return { email: "admin@example.com" };
};
const worker = createWorker({ sePublicData: publicData, seApiStore: store, authVerifier: authorized });
const get = (path, headers = {}) => worker.fetch(new Request(`https://structevidence.com${path}`, { headers }), env);
const post = (path, body, headers = {}) => worker.fetch(new Request(`https://structevidence.com${path}`, { method: "POST", headers: { "content-type": "application/json", origin: "https://structevidence.com", ...headers }, body: typeof body === "string" ? body : JSON.stringify(body) }), env);

test("capabilities freeze SE_API_v1", async () => {
  const response = await get("/api/v1"), body = await response.json();
  assert.equal(response.status, 200); assert.equal(body.api_version, API_VERSION); assert.equal(body.data.capabilities.as_of_queries, true);
});

test("subject list is sanitized and includes current recorded State", async () => {
  const body = await (await get("/api/v1/subjects")).json();
  assert.equal(body.data.items.length, 1); assert.equal(body.data.items[0].current_state.state_code, "ALTERNATIVE_PATH_IDENTIFIED");
  assert.equal(JSON.stringify(body).includes("source_object"), false);
});

test("subject lookup works and hides provenance", async () => {
  const response = await get("/api/v1/subjects/SE-SUBJ-000001"), body = await response.json();
  assert.equal(response.status, 200); assert.equal(body.data.subject_id, "SE-SUBJ-000001"); assert.equal("provenance" in body.data, false);
});

test("current State is explicit and exposes canonical chain hash", async () => {
  const body = await (await get("/api/v1/subjects/SE-SUBJ-000001/state")).json();
  assert.equal(body.data.state_id, "SE-ST-20260925-000002"); assert.equal(body.data.chain_hash, publicData.states[1].chain_hash);
  assert.match(body.meta.interpretation, /NOT_PREDICTION/);
});

test("State history defaults oldest to newest and supports descending", async () => {
  const asc = await (await get("/api/v1/subjects/SE-SUBJ-000001/states")).json();
  const desc = await (await get("/api/v1/subjects/SE-SUBJ-000001/states?order=desc")).json();
  assert.deepEqual(asc.data.map((x) => x.state_id), ["SE-ST-20260925-000001", "SE-ST-20260925-000002"]);
  assert.deepEqual(desc.data.map((x) => x.state_id), ["SE-ST-20260925-000002", "SE-ST-20260925-000001"]);
});

test("as_of returns the correct immutable historical State", async () => {
  const body = await (await get("/api/v1/subjects/SE-SUBJ-000001/state?as_of=2026-09-25T12:30:00Z")).json();
  assert.equal(body.data.state_id, "SE-ST-20260925-000001");
});

test("later-observed Evidence cannot leak backward despite earlier publication", async () => {
  const later = publicData.evidence.find((item) => item.evidence_id.endsWith("000004"));
  assert.ok(Date.parse(later.published_at) < Date.parse("2026-09-23T00:00:00Z"));
  assert.ok(Date.parse(later.observed_at) > Date.parse("2026-09-23T00:00:00Z"));
  const response = await get("/api/v1/subjects/SE-SUBJ-000001/state?as_of=2026-09-23T00:00:00Z"), body = await response.json();
  assert.equal(response.status, 404); assert.equal(body.error.code, "STATE_NOT_FOUND_AT_BOUNDARY");
});

test("change feed and subject change view work", async () => {
  const feed = await (await get("/api/v1/changes?materiality=MATERIAL&limit=1")).json();
  const subject = await (await get("/api/v1/subjects/SE-SUBJ-000001/changes")).json();
  assert.equal(feed.data[0].previous.state_code, "WATCH"); assert.equal(feed.data[0].current.state_code, "ALTERNATIVE_PATH_IDENTIFIED");
  assert.equal(subject.data.length, 1);
});

test("Evidence keeps source fact, normalized claim, and review separate", async () => {
  const body = await (await get("/api/v1/evidence/SE-EV-20260925-000001")).json();
  assert.equal(body.data.source.name, "Synthetic protocol source"); assert.ok(body.data.normalized_claim); assert.equal(body.data.review.status, "ACCEPTED");
  assert.equal("raw_reference" in body.data, false); assert.equal("provenance" in body.data, false);
});

test("Branches expose possibilities without probabilities", async () => {
  const body = await (await get("/api/v1/subjects/SE-SUBJ-000001/branches")).json(), encoded = JSON.stringify(body);
  assert.equal(body.data.length, 2); assert.equal(/probability|percent|likelihood/i.test(encoded), false);
});

test("unknown IDs return versioned 404 errors", async () => {
  const response = await get("/api/v1/states/SE-ST-20990101-999999"), body = await response.json();
  assert.equal(response.status, 404); assert.equal(body.error.code, "STATE_NOT_FOUND"); assert.match(body.error.request_id, /^SE-HTTP-/);
});

test("object identifiers cannot traverse paths", async () => {
  const response = await get("/api/v1/states/%2e%2e%2fsecret");
  assert.notEqual(response.status, 200);
});

test("ETag equals canonical hash and If-None-Match returns 304", async () => {
  const first = await get("/api/v1/states/SE-ST-20260925-000002"), etag = first.headers.get("etag");
  assert.equal(etag, `"${publicData.states[1].state_hash}"`);
  const cached = await get("/api/v1/states/SE-ST-20260925-000002", { "if-none-match": etag });
  assert.equal(cached.status, 304); assert.equal(await cached.text(), "");
});

const requestPayload = { subject: "Synthetic path", question: "What changed?", decision_context: "Private selection", urgency: "NORMAL", requested_output: "EVIDENCE_CHAIN", public_case_permission: false };

test("Request is accepted in private plane and idempotency prevents duplicates", async () => {
  const key = "request-key-0001", first = await post("/api/v1/requests", requestPayload, { "idempotency-key": key });
  const second = await post("/api/v1/requests", requestPayload, { "idempotency-key": key });
  const a = await first.json(), b = await second.json();
  assert.equal(first.status, 201); assert.equal(second.status, 200); assert.equal(a.data.request_id, b.data.request_id);
  assert.equal(store.objects.request.filter((item) => item.request_id === a.data.request_id).length, 1);
});

test("protected Request status is inaccessible without Access", async () => {
  const denied = createWorker({ sePublicData: publicData, seApiStore: store });
  const response = await denied.fetch(new Request(`https://structevidence.com/api/v1/requests/${store.objects.request[0].request_id}`), env);
  assert.equal(response.status, 403);
});

test("protected Request status returns no private body fields", async () => {
  const response = await get(`/api/v1/requests/${store.objects.request[0].request_id}`), body = await response.json();
  assert.equal(response.status, 200); assert.equal(body.data.visibility, "CUSTOMER_PRIVATE"); assert.equal("decision_context" in body.data, false);
});

test("Challenge submission cannot change canonical State", async () => {
  const before = JSON.stringify(publicData.states), response = await post("/api/v1/challenges", { state_id: "SE-ST-20260925-000002", claim: "Deployment remains unsupported.", evidence_url: "https://example.com/evidence", notes: "Synthetic test" }, { "idempotency-key": "challenge-key-01" });
  const body = await response.json(); assert.equal(response.status, 201); assert.equal(body.data.status, "CHALLENGE_SUBMITTED"); assert.equal(JSON.stringify(publicData.states), before);
});

test("Outcome submission cannot change canonical State", async () => {
  const before = JSON.stringify(publicData.states), response = await post("/api/v1/outcomes", { request_id: store.objects.request[0].request_id, state_id_used: "SE-ST-20260925-000002", action: "Synthetic trial", reported_result: "Synthetic result", authorization_for_public_use: false }, { "idempotency-key": "outcome-key-0001" });
  const body = await response.json(); assert.equal(response.status, 201); assert.equal(body.data.status, "OUTCOME_REPORTED"); assert.equal(JSON.stringify(publicData.states), before);
});

test("private Request and Outcome are absent from all public responses", async () => {
  for (const path of ["/api/v1/subjects", "/api/v1/changes", "/api/v1/subjects/SE-SUBJ-000001/state"]) {
    const text = await (await get(path)).text(); assert.equal(text.includes("Private selection"), false); assert.equal(text.includes("Synthetic result"), false);
  }
});

test("unexpected fields, malformed JSON, and oversized bodies fail closed", async () => {
  assert.equal((await post("/api/v1/requests", { ...requestPayload, hidden: "attack" })).status, 400);
  assert.equal((await post("/api/v1/requests", "{")).status, 400);
  assert.equal((await post("/api/v1/requests", { ...requestPayload, question: "x".repeat(70_000) })).status, 413);
});

test("wrong Access audience is rejected", async () => {
  const wrongEnv = { ...env, ADMIN_API_AUD: "wrong-aud" };
  const response = await worker.fetch(new Request("https://structevidence.com/api/v1/admin/proposals/none"), wrongEnv);
  assert.equal(response.status, 403);
});

test("proposal requires validation before approval", async () => {
  const proposed_state = { ...publicData.states[1] }, proposed_change_event = { ...publicData.changes[0] };
  const created = await post("/api/v1/admin/proposals", { subject_id: "SE-SUBJ-000001", proposed_evidence_ids: [], previous_state_id: "SE-ST-20260925-000002", proposed_state, proposed_change_event });
  const proposal = (await created.json()).data;
  assert.equal(created.status, 201); assert.equal(proposal.status, "DRAFT");
  assert.equal((await post(`/api/v1/admin/proposals/${proposal.proposal_id}/approve`, {})).status, 409);
  const validated = await post(`/api/v1/admin/proposals/${proposal.proposal_id}/validate`, {}), checked = (await validated.json()).data;
  assert.equal(checked.status, "REVIEW_REQUIRED"); assert.equal(checked.chain_verification_status, "REPOSITORY_VERIFICATION_REQUIRED");
  const approved = await post(`/api/v1/admin/proposals/${proposal.proposal_id}/approve`, {}), final = (await approved.json()).data;
  assert.equal(final.status, "APPROVED"); assert.equal(final.materialization_status, "NOT_MATERIALIZED");
});

test("Phase 2 migration freezes private input and proposal tables", () => {
  const sql = readFileSync(new URL("../migrations/0002_se_api_v1.sql", import.meta.url), "utf8");
  assert.match(sql, /CREATE TABLE se_api_idempotency/); assert.match(sql, /se_api_outcomes_no_update/); assert.match(sql, /CREATE TABLE se_state_proposals/);
});
