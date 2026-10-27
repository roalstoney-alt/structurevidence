import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const resultUrl = new URL("../../../docs/implementation/SE-IREN-P0-R3-FULL-FORM-LOCALIZATION-003-RESULT.json", import.meta.url);
const markdownUrl = new URL("../../../docs/implementation/SE-IREN-P0-R3-FULL-FORM-LOCALIZATION-003-RESULT.md", import.meta.url);

test("full-form Staging result records three-language 201/200/409 and D1 uniqueness", () => {
  const result = JSON.parse(readFileSync(resultUrl, "utf8"));
  for (const locale of ["en", "zh-CN", "es"]) {
    const observation = result.staging_browser_acceptance.locales[locale];
    assert.equal(observation.create_status, 201);
    assert.equal(observation.replay_status, 200);
    assert.equal(observation.conflict_status, 409);
    assert.match(observation.request_id_sha256, /^[a-f0-9]{64}$/);
  }
  assert.deepEqual(result.staging_d1.new_synthetic_records, {
    customers: 3,
    requests: 3,
    request_events: 3,
    request_consent_receipts: 3,
    request_idempotency: 3,
    bounded_private_not_authorized_unassigned: 3,
    valid_frozen_consents: 3
  });
  assert.equal(result.staging_d1.foreign_key_violations, 0);
});

test("full-form result preserves append-only, Access, CORS, and production isolation", () => {
  const result = JSON.parse(readFileSync(resultUrl, "utf8"));
  assert.deepEqual(new Set(Object.values(result.staging_d1.append_only_probes)), new Set(["REJECTED_SQLITE_CONSTRAINT_TRIGGER"]));
  assert.equal(result.access_and_cors.unauthenticated_admin_get, 302);
  assert.equal(result.access_and_cors.authenticated_browser_admin_read, "PASS_REQUEST_ARRAY_RETURNED");
  assert.equal(result.access_and_cors.browser_cross_origin_options, "CORS_BLOCKED");
  assert.equal(result.access_and_cors.browser_cross_origin_post_sent, false);
  assert.equal(result.environment.production_worker_changed, false);
  assert.equal(result.environment.production_d1_changed, false);
  assert.equal(result.prohibited_actions.production_post_count, 0);
  assert.equal(result.prohibited_actions.pull_request_merged, false);
});

test("full-form result remains redacted and keeps the two human/production gates open", () => {
  const resultText = readFileSync(resultUrl, "utf8");
  const markdown = readFileSync(markdownUrl, "utf8");
  const result = JSON.parse(resultText);
  assert.equal(result.staging_browser_acceptance.raw_request_ids_committed, false);
  assert.equal(result.staging_browser_acceptance.raw_idempotency_keys_committed, false);
  assert.equal(result.staging_browser_acceptance.turnstile_tokens_committed, false);
  assert.equal(result.release_gates.human_privacy_legal_signoff, "PENDING");
  assert.equal(result.release_gates.production_recoverability, "UNKNOWN");
  assert.equal(result.release_gates.remaining_gate_count, 2);
  assert.equal(result.release_gates.ready_for_owner_production_review, "NO");
  assert.doesNotMatch(resultText, /SE-REQ-[A-Z0-9]{20}/);
  assert.doesNotMatch(resultText + markdown, /@example\.invalid/);
  assert.doesNotMatch(resultText + markdown, /cf-access-jwt-assertion|TURNSTILE_SECRET_KEY|ADMIN_EMAILS/);
});
