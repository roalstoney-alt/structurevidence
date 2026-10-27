import assert from "node:assert/strict";

const baseUrl = process.env.LOCAL_INTAKE_BASE_URL || "http://127.0.0.1:8799";
const origin = process.env.LOCAL_REQUEST_ORIGIN || "https://structevidence.com";
const consent = { consent_accepted: true, consent_version: "SE-CUSTOMER-PRIVACY-v1" };
const payload = (token, extra = {}) => ({ request_type: "VERIFY", email: "local-e2e@example.test", claim_or_question: "Is this isolated path atomic?", decision: "Local verification only", turnstile_token: token, ...consent, ...extra });
const post = async (key, body) => {
  const response = await fetch(`${baseUrl}/api/requests`, { method: "POST", headers: { origin, "content-type": "application/json", "idempotency-key": key }, body: JSON.stringify(body) });
  return { status: response.status, body: await response.json() };
};

const firstKey = "local-e2e-first-000000000001";
const first = await post(firstKey, payload("local-valid-first"));
assert.equal(first.status, 201); assert.equal(first.body.idempotency_status, "CREATED");
const replay = await post(firstKey, payload("local-valid-not-consumed"));
assert.equal(replay.status, 200); assert.equal(replay.body.request_id, first.body.request_id); assert.equal(replay.body.idempotency_status, "REPLAYED");
const conflict = await post(firstKey, payload("local-valid-conflict", { claim_or_question: "Different payload" }));
assert.equal(conflict.status, 409); assert.equal(JSON.stringify(conflict.body).includes(first.body.request_id), false);

const [parallelA, parallelB] = await Promise.all([
  post("local-e2e-parallel-00000001", payload("local-valid-parallel-a", { email: "parallel@example.test" })),
  post("local-e2e-parallel-00000001", payload("local-valid-parallel-b", { email: "parallel@example.test" }))
]);
assert.deepEqual([parallelA.status, parallelB.status].sort(), [200, 201]);
assert.equal(parallelA.body.request_id, parallelB.body.request_id);

const noConsent = await post("local-e2e-no-consent-0000001", payload("local-valid-no-consent", { consent_accepted: false }));
assert.equal(noConsent.status, 400);
const badChallenge = await post("local-e2e-bad-challenge-00001", payload("invalid"));
assert.equal(badChallenge.status, 400);

const detailResponse = await fetch(`${baseUrl}/api/admin/requests/${first.body.request_id}`);
assert.equal(detailResponse.status, 200);
const detail = await detailResponse.json();
assert.equal(detail.request.privacy_class, "CUSTOMER_PRIVATE");
assert.equal(detail.request.research_authorization_status, "NOT_AUTHORIZED");
assert.equal(detail.events.length, 1); assert.equal(detail.events[0].event_type, "REQUEST_SUBMITTED");
assert.equal(detail.consent_receipts.length, 1); assert.equal(detail.consent_receipts[0].consent_version, "SE-CUSTOMER-PRIVACY-v1");

console.log(JSON.stringify({ result: "PASS", first, replay, conflict_status: conflict.status, concurrent_statuses: [parallelA.status, parallelB.status], consent_rejection: noConsent.status, challenge_rejection: badChallenge.status, admin_read_after_write: detailResponse.status }, null, 2));
