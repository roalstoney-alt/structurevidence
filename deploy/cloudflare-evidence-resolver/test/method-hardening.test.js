import test from "node:test";
import assert from "node:assert/strict";
import { resolveQuery } from "../worker.js";
import { normalizedStateFor } from "../question-protocol.js";


test("SUPPORTED_SINGLE_INSTANCE maps to supported single-instance deployment", () => {
  const state = normalizedStateFor({ state: "SUPPORTED_SINGLE_INSTANCE", as_of: "2026-09-20" });
  assert.equal(state.epistemic_state, "SUPPORTED");
  assert.equal(state.verification_depth, "FIELD_DEPLOYED_SINGLE_INSTANCE");
  assert.equal(state.workflow_state, "NONE");
});

test("SUPPORTED_FOR_TRIAL_POPULATION remains population-scoped", () => {
  const state = normalizedStateFor({ state: "SUPPORTED_FOR_TRIAL_POPULATION", as_of: "2026-09-28" });
  assert.equal(state.epistemic_state, "SUPPORTED");
  assert.equal(state.applicability_scope, "POPULATION_SPECIFIC");
});

test("VERIFICATION_REQUIRED is workflow state rather than epistemic state", () => {
  const state = normalizedStateFor({ state: "VERIFICATION_REQUIRED", as_of: "2026-09-24" });
  assert.equal(state.epistemic_state, "UNKNOWN");
  assert.equal(state.workflow_state, "VERIFICATION_REQUIRED");
  assert.notEqual(state.epistemic_state, "VERIFICATION_REQUIRED");
});

test("resolver exposes the closed boundary without removing legacy fields", () => {
  const result = resolveQuery("Has a named 800VDC SST system been commercially deployed?");
  assert.equal(result.inference_policy, "CLOSED_BOUNDARY");
  assert.equal(result.undeclared_inference, "OUT_OF_BOUNDARY");
  assert.equal(result.public_stop_point.state, "SUPPORTED_SINGLE_INSTANCE");
  assert.equal(result.public_stop_point.normalized_state.epistemic_state, "SUPPORTED");
  for (const field of ["state", "supports", "does_not_support", "unknowns", "as_of"]) {
    assert.ok(Object.hasOwn(result.public_stop_point, field));
  }
});

test("resolver stop-point carries complete temporal state identity", () => {
  const result = resolveQuery("Has a named 800VDC SST system been commercially deployed?");
  const stop = result.public_stop_point;
  assert.ok(stop.as_of);
  assert.equal(stop.protocol_version, "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1");
  assert.match(stop.snapshot.commit, /^[0-9a-f]{40}$/);
  assert.equal(stop.snapshot.permalink, `https://github.com/roalstoney-alt/structurevidence/tree/${stop.snapshot.commit}`);
  assert.equal(stop.decision_ownership.final_decision_authority, "RESPONSIBLE_ACTOR");
  assert.notEqual(stop.decision_ownership.final_decision_authority, "AGENT");
});
