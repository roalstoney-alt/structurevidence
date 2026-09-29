import test from "node:test";
import assert from "node:assert/strict";
import worker, { resolveQuery } from "../worker.js";

const claim = (result, id) => result.matched_claims.find((item) => item.claim_id === id);

test("named 800VDC deployment preserves single-instance boundary", () => {
  const result = resolveQuery("Has 800VDC SST been commercially deployed?");
  const item = claim(result, "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT");
  assert.equal(result.result, "MATCHED");
  assert.equal(item.state, "SUPPORTED_SINGLE_INSTANCE");
  assert.equal(item.resolution_status, "BOUNDED_SUPPORT");
  assert.match(item.does_not_support.join(" "), /Industry adoption/i);
});

test("wide 800VDC adoption remains not established", () => {
  const item = claim(resolveQuery("Is 800VDC widely adopted?"), "CML-PDRE-001.INDUSTRY_ADOPTION");
  assert.equal(item.state, "NOT_ESTABLISHED");
  assert.equal(item.resolution_status, "UNRESOLVED");
  assert.equal(item.human_authorization_required, true);
});

test("named sodium-ion commissioning remains not established", () => {
  const item = claim(resolveQuery("Has sodium-ion BESS been commissioned at a named customer site?"), "SE-BESS-SODIUM-001.NAMED_COMMISSIONED_SITE");
  assert.equal(item.state, "NOT_ESTABLISHED");
});

test("sodium-ion cost query does not answer yes", () => {
  const result = resolveQuery("Is sodium-ion universally cheaper than LFP?");
  const item = claim(result, "SE-BESS-SODIUM-001.LIFECYCLE_COST_ADVANTAGE_OVER_LFP");
  assert.ok(item);
  assert.equal(item.state, "NOT_ESTABLISHED");
});

test("HARMONi-A returns trial-group result only", () => {
  const item = claim(resolveQuery("What was HARMONi-A overall survival?"), "SE-ONC-NSQNSCLC-CN-001.HARMONI_A_OS");
  assert.equal(item.state, "SUPPORTED_FOR_TRIAL_POPULATION");
  assert.match(item.does_not_support.join(" "), /personal forecast/i);
});

test("personal medical query returns no probability and explicit boundary", () => {
  const result = resolveQuery("What is my chance of surviving lung cancer with this treatment?");
  const item = claim(result, "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY");
  assert.equal(item.state, "NOT_ESTABLISHED");
  assert.equal(result.medical_boundary, "This public evidence object does not provide patient-specific medical advice.");
  assert.doesNotMatch(JSON.stringify(result), /\b\d+(?:\.\d+)?%/);
});

test("no match does not generate an answer or action", () => {
  const result = resolveQuery("What is the weather on Europa?");
  assert.equal(result.result, "NO_MATCH");
  assert.deepEqual(result.matched_claims, []);
  assert.equal(result.human_action_required, true);
  assert.equal(result.commercial_next_step, null);
});

test("HTTP endpoint is GET-only, deterministic JSON, and exposes no admin surface", async () => {
  const response = await worker.fetch(new Request("https://structurevidence.org/api/resolve?q=Is%20800VDC%20widely%20adopted%3F"));
  assert.equal(response.status, 200);
  assert.equal((await response.json()).result, "MATCHED");
  assert.equal((await worker.fetch(new Request("https://structurevidence.org/api/resolve", { method: "POST" }))).status, 405);
  assert.equal((await worker.fetch(new Request("https://structurevidence.org/api/admin/requests"))).status, 404);
});
