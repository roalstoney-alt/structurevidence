import test from "node:test";
import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const reportUrl = new URL("../../../docs/implementation/SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002-RESULT.json", import.meta.url);

test("final staging acceptance keeps real-provider and deterministic Turnstile evidence separate", async () => {
  const report = JSON.parse(await readFile(reportUrl, "utf8"));
  assert.equal(report.project, "SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002");
  assert.equal(report.locked_head_sha, "fc0615d0e6e2799909d72baaa743dd1bfb3f20cd");
  assert.deepEqual(report.turnstile.real_provider_observed.map(({ case: name }) => name), ["valid_challenge", "invalid_token"]);
  assert.deepEqual(report.turnstile.deterministic_fault_injection.map(({ case: name }) => name), [
    "missing_token", "expired_token", "replayed_token", "wrong_hostname", "wrong_action", "provider_error", "provider_timeout"
  ]);
  assert.equal(report.turnstile.deterministic_cases_claimed_as_real_provider, false);
  assert.ok(report.turnstile.deterministic_fault_injection.every(({ result }) => result === "PASS"));
});

test("owner-review readiness requires Access, privacy, append-only, and production isolation gates", async () => {
  const report = JSON.parse(await readFile(reportUrl, "utf8"));
  assert.equal(report.cloudflare_access.evidence_class, "REAL_PROVIDER_OBSERVED");
  assert.equal(report.cloudflare_access.http_status, 200);
  assert.equal(report.cloudflare_access.target_request.request_id, "SE-REQ-E56EABAB6D574DC3BC7C");
  assert.equal(report.cloudflare_access.target_request.matches_staging_d1, true);
  assert.equal(report.cloudflare_access.authentication_bypassed, false);
  assert.equal(report.cloudflare_access.jwt_persisted, false);
  assert.equal(report.cloudflare_access.otp_persisted, false);
  assert.equal(report.cloudflare_access.identity_persisted, false);
  assert.ok(Object.values(report.gates).every((result) => result === "PASS"));
  assert.equal(report.production_isolation.production_post_count, 0);
  assert.equal(report.production_isolation.production_worker_changed, false);
  assert.equal(report.production_isolation.production_d1_changed, false);
  assert.equal(report.ready_for_owner_production_review, true);
  assert.equal(report.merge_authorized, false);
  assert.equal(report.production_deployment_authorized, false);
});
