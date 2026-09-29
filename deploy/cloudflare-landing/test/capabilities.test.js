import test from "node:test";
import assert from "node:assert/strict";
import worker from "../worker.js";

test("commercial plane exposes only human-authorized capability metadata", async () => {
  const response = await worker.fetch(new Request("https://structevidence.com/capabilities.json"), {});
  assert.equal(response.status, 200);
  const body = await response.json();
  assert.equal(body.provider, "StructureEvidence");
  assert.deepEqual(body.services.map((service) => service.service_id), ["VERIFY_CLAIM", "CUSTOMER_CONTEXT", "DECISION_PACK"]);
  for (const service of body.services) {
    assert.equal(service.human_authorization_required, true);
    assert.equal(service.automatic_research_authorization, false);
  }
  const verify = body.services.find((service) => service.service_id === "VERIFY_CLAIM");
  assert.equal(verify.supports_question_intake, true);
  assert.equal(verify.supports_minimum_missing_evidence, true);
  assert.equal(verify.quote_requires_human_authorization, true);
  assert.equal(verify.outcome_guaranteed, false);
  assert.doesNotMatch(JSON.stringify(body), /customer_cases|admin|claim_id|D1/i);
});
