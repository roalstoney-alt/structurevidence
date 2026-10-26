const endpoint = "https://structevidence-commercial-staging.roalstoney.workers.dev/api/requests";
const key = "STAGING_TEST_IDEMPOTENCY_FIXTURE_20261027";
const expectedRequestId = "STAGING_TEST_FIXTURE_REQUEST_20261027";
const payload = {
  request_type: "VERIFY",
  email: "staging-test-idempotency-fixture@invalid.example",
  contact_name: "STAGING_TEST_FIXTURE",
  company: "STAGING_TEST_FIXTURE",
  decision: "STAGING_TEST fixture decision",
  claim_or_question: "STAGING_TEST fixture claim",
  consent_accepted: true,
  consent_version: "SE-CUSTOMER-PRIVACY-v1",
  turnstile_token: "STAGING_TEST_REPLAY_MUST_NOT_REVERIFY"
};

async function send(body) {
  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "content-type": "application/json", "idempotency-key": key },
    body: JSON.stringify(body)
  });
  const result = await response.json();
  return { status: response.status, request_id: result.request_id || null, idempotency_status: result.idempotency_status || null, error: result.error || null };
}

const [left, right] = await Promise.all([send(payload), send(payload)]);
const conflict = await send({ ...payload, claim_or_question: "STAGING_TEST different payload must conflict" });
const concurrentPass = [left, right].every((result) => result.status === 200 && result.request_id === expectedRequestId && result.idempotency_status === "REPLAYED");
const conflictPass = conflict.status === 409 && !conflict.request_id;
console.log(JSON.stringify({ concurrent_replay: { left, right, pass: concurrentPass }, conflicting_payload: { ...conflict, pass: conflictPass } }));
if (!concurrentPass || !conflictPass) process.exitCode = 1;
