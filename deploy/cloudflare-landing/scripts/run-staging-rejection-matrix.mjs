const origin = "https://structevidence-commercial-staging.roalstoney.workers.dev";

const basePayload = () => ({
  request_type: "VERIFY",
  email: "staging-test-rejection@invalid.example",
  contact_name: "STAGING_TEST",
  company: "STAGING_TEST",
  decision: "STAGING_TEST decision",
  claim_or_question: "STAGING_TEST claim",
  consent_accepted: true,
  consent_version: "SE-CUSTOMER-PRIVACY-v1",
  turnstile_token: "STAGING_TEST_INVALID_TURNSTILE_TOKEN"
});

const pause = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
let sequence = 0;

async function post(name, expected, payload, options = {}) {
  sequence += 1;
  const body = options.rawBody ?? JSON.stringify(payload);
  const response = await fetch(`${origin}/api/requests`, {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "idempotency-key": `STAGING_TEST_REJECTION_${String(sequence).padStart(3, "0")}`,
      ...(options.origin ? { origin: options.origin } : {})
    },
    body
  });
  let error = "";
  try { error = String((await response.json()).error || ""); } catch { error = "non-json-response"; }
  const pass = response.status === expected;
  console.log(JSON.stringify({ name, expected, actual: response.status, pass, error }));
  if (!pass) process.exitCode = 1;
}

await post("missing_consent", 400, { ...basePayload(), consent_accepted: false });
await post("invalid_consent_version", 400, { ...basePayload(), consent_version: "STAGING_TEST_OLD" });
await post("invalid_email", 400, { ...basePayload(), email: "not-an-email" });
await post("invalid_request_type", 400, { ...basePayload(), request_type: "STAGING_TEST" });

await pause(11_000);
await post("unknown_json_field", 400, { ...basePayload(), unexpected: "STAGING_TEST" });
await post("invalid_turnstile", 400, basePayload());
await post("oversized_request", 413, basePayload(), { rawBody: JSON.stringify({ ...basePayload(), claim_or_question: "S".repeat(66_000) }) });
await post("disallowed_browser_origin", 403, basePayload(), { origin: "https://staging-test.invalid.example" });

await pause(11_000);
const rateStatuses = [];
for (let batch = 0; batch < 4; batch += 1) {
  const burst = await Promise.all(Array.from({ length: 4 }, async (_unused, offset) => {
    const index = batch * 4 + offset;
    const response = await fetch(`${origin}/api/requests`, {
      method: "POST",
      headers: { "content-type": "application/json", "idempotency-key": `STAGING_TEST_RATE_LIMIT_${String(index).padStart(3, "0")}` },
      body: JSON.stringify({ ...basePayload(), consent_accepted: false })
    });
    return response.status;
  }));
  rateStatuses.push(...burst);
  if (!rateStatuses.includes(429)) await pause(500);
}
const ratePass = rateStatuses.includes(429);
console.log(JSON.stringify({ name: "rate_limit_overflow", expected: 429, actual: rateStatuses, pass: ratePass }));
if (!ratePass) process.exitCode = 1;
