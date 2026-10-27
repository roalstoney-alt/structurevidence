import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const resultUrl = new URL("../../../docs/implementation/SE-IREN-P0-R3-CORS-PRIVACY-CLOSURE-001-RESULT.json", import.meta.url);
const checklistUrl = new URL("../../../docs/implementation/SE-IREN-P0-R3-PRIVACY-LEGAL-SIGNOFF-CHECKLIST.md", import.meta.url);

test("R3 records real allowed and denied CORS boundaries without claiming a same-origin preflight", () => {
  const result = JSON.parse(readFileSync(resultUrl, "utf8"));
  assert.equal(result.cors.allowed_origin_http_options.status, 204);
  assert.deepEqual(result.cors.allowed_origin_http_options.allow_headers, ["content-type", "idempotency-key"]);
  assert.equal(result.cors.disallowed_origin_http_options.allow_origin_present, false);
  assert.equal(result.cors.same_origin_form.result, "BROWSER_PREFLIGHT_NOT_APPLICABLE_SAME_ORIGIN");
  assert.equal(result.cors.cross_origin_browser.browser_outcome, "PREFLIGHT_REJECTED_BEFORE_POST");
  assert.equal(result.cors.cross_origin_browser.staging_post_sent, false);
  assert.equal(result.prohibited_actions.production_post_count, 0);
});

test("R3 keeps human privacy/legal approval pending and stores no purported signature", () => {
  const result = JSON.parse(readFileSync(resultUrl, "utf8"));
  const checklist = readFileSync(checklistUrl, "utf8");
  assert.equal(result.privacy_review.human_privacy_legal_signoff, "PENDING");
  assert.equal(result.privacy_review.assistant_signed, false);
  assert.equal(result.gates.ready_for_owner_production_release, "NO");
  assert.match(checklist, /HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING/);
  assert.doesNotMatch(checklist, /^- \[x\]/m);
  assert.match(checklist, /Complete these fields only in the restricted system of record/);
});

test("R3 source patch does not change the frozen consent version or production boundaries", () => {
  const result = JSON.parse(readFileSync(resultUrl, "utf8"));
  assert.equal(result.localization_patch.consent_version, "SE-CUSTOMER-PRIVACY-v1");
  assert.equal(result.localization_patch.privacy_meaning_changed, false);
  assert.equal(result.localization_patch.research_authorization_meaning_changed, false);
  assert.equal(result.localization_patch.publication_authorization_meaning_changed, false);
  assert.equal(result.localization_patch.deployment_status, "SOURCE_ONLY_NOT_DEPLOYED");
  assert.deepEqual(result.prohibited_actions, {
    production_post_count: 0,
    production_migration: false,
    production_worker_deploy: false,
    staging_worker_deploy: false,
    pull_request_merged: false,
    public_pilot_started: false,
    social_publication: false
  });
});
