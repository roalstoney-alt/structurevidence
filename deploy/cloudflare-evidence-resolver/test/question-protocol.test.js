import test from "node:test";
import assert from "node:assert/strict";
import { resolveQuery } from "../worker.js";
import {
  authorizePaidCycle,
  classifyPublicationEligibility,
  downgradeIsomorphic,
  evaluateIntake,
} from "../question-protocol.js";

const getClaim = (result, id) => result.matched_claims.find((claim) => claim.claim_id === id);

test("A question intake passes a bounded falsifiable deployment question", () => {
  const intake = evaluateIntake("Has a named SST-based 800VDC data-center power system reached commercial field deployment?");
  assert.equal(intake.intake_status, "PASS");
  assert.equal(intake.atomic, true);
  assert.equal(intake.falsifiable, true);
  assert.equal(intake.scoped, true);
  assert.equal(intake.time_bounded, true);
});

test("B intake failures decompose and stop for human selection", () => {
  for (const query of [
    "Is 800VDC commercially proven, cheaper, more reliable and the best future architecture?",
    "Is sodium-ion the future of energy storage?",
    "Does this work?",
  ]) {
    const result = resolveQuery(query);
    assert.equal(result.intake.intake_status, "FAIL");
    assert.equal(result.resolution_action, "DECOMPOSE_AND_STOP");
    assert.equal(result.intake.human_selection_required, true);
    assert.ok(result.intake.decomposition_draft.length > 0);
    assert.deepEqual(result.matched_claims, []);
    assert.equal(result.quote_available, false);
  }
});

test("C exact match reuses the public stop point and cites then stops", () => {
  const result = resolveQuery("Has a named 800VDC SST system been commercially deployed?");
  assert.equal(result.match_class, "EXACT");
  assert.equal(result.sufficiency, "SUFFICIENT");
  assert.equal(result.resolution_action, "CITE_AND_STOP");
  assert.equal(result.quote_available, false);
  assert.equal(result.commercial_next_step, null);
  assert.equal(result.public_stop_point.state, "SUPPORTED_SINGLE_INSTANCE");
  for (const field of ["supports", "does_not_support", "as_of", "freshness", "verification_depth", "applicability", "unknowns", "next_observable", "canonical_url"]) assert.ok(result.public_stop_point[field]);
});

test("D isomorphic match requires and passes explicit equivalence", () => {
  const result = resolveQuery("Has anyone actually operated this architecture commercially?");
  assert.equal(result.match_class, "ISOMORPHIC");
  assert.equal(result.equivalence_result, "PASS");
  assert.ok(Object.values(result.equivalence).every(Boolean));
  assert.equal(getClaim(result, "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT").state, "SUPPORTED_SINGLE_INSTANCE");
});

test("E failed isomorphic equivalence downgrades to partial", () => {
  const result = downgradeIsomorphic({
    same_subject: true,
    same_predicate: true,
    same_evidence_threshold: true,
    same_scope: false,
    same_temporal_meaning: true,
    same_decision_implication: true,
  });
  assert.equal(result.equivalence_result, "FAIL");
  assert.equal(result.match_class, "PARTIAL");
});

test("F partial match returns deployment boundary and only minimum economic evidence", () => {
  const result = resolveQuery("Has 800VDC been commercially deployed and proven economically superior?");
  assert.equal(result.intake.intake_status, "PASS");
  assert.equal(result.match_class, "PARTIAL");
  assert.equal(result.sufficiency, "PARTIALLY_SUFFICIENT");
  assert.equal(getClaim(result, "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT").state, "SUPPORTED_SINGLE_INSTANCE");
  assert.equal(result.minimum_missing_evidence.length, 1);
  assert.match(result.minimum_missing_evidence[0].description, /comparative economics/i);
  assert.equal(result.research_level_candidate, "L2_INVESTIGATE");
});

test("G no match returns no public answer and no generated quote", () => {
  const result = resolveQuery("Is optical quantum computing replacing GPU clusters in Indonesian hospitals?");
  assert.equal(result.intake.intake_status, "PASS");
  assert.equal(result.match_class, "NONE");
  assert.equal(result.result, "NO_MATCH");
  assert.deepEqual(result.matched_claims, []);
  assert.equal(result.resolution_action, "NO_PUBLIC_MATCH");
  assert.equal(result.quote_available, false);
});

test("H-M public stop point, freshness, applicability, missing evidence and RDL remain bounded", () => {
  const result = resolveQuery("Is 800VDC widely adopted?");
  assert.equal(result.public_stop_point.state, "NOT_ESTABLISHED");
  assert.equal(result.freshness.freshness_state, "CURRENT");
  assert.equal(result.freshness.last_public_review_at, "NOT_RECORDED");
  assert.equal(result.public_stop_point.verification_depth, "NOT_RECORDED");
  assert.equal(result.public_stop_point.applicability, "ARCHITECTURE_LEVEL_ONLY");
  assert.equal(result.sufficiency, "INSUFFICIENT");
  assert.equal(result.minimum_missing_evidence.length, 1);
  assert.equal(result.research_level_candidate, "L1_VERIFY");
});

test("N-P verification quote buys process, never outcome or authorization", () => {
  const result = resolveQuery("Has 800VDC been commercially deployed and proven economically superior?");
  const quote = result.verification_quote;
  assert.equal(result.quote_available, true);
  assert.equal(quote.quote_status, "AVAILABLE");
  assert.equal(quote.price.status, "TO_BE_DEFINED");
  assert.equal(quote.price.amount, null);
  assert.equal(quote.human_authorization_required, true);
  assert.equal(quote.payment_required, true);
  assert.equal(quote.research_authorized, false);
  assert.equal(quote.outcome_guaranteed, false);
  assert.ok(quote.stop_conditions.length > 0);
});

test("O paid cycle requires quote acceptance, payment, and explicit authorization record", () => {
  assert.equal(authorizePaidCycle({ quote_status: "QUOTE_ACCEPTED", payment_status: "PAYMENT_CONFIRMED" }).research_status, "NOT_AUTHORIZED");
  const authorized = authorizePaidCycle({ quote_status: "QUOTE_ACCEPTED", payment_status: "PAYMENT_CONFIRMED", authorization_record: "RESEARCH_AUTHORIZED" });
  assert.equal(authorized.research_status, "RESEARCH_AUTHORIZED");
  assert.equal(authorized.outcome_guaranteed, false);
});

test("Q-S publication eligibility protects private and mixed evidence", () => {
  const common = { evidence_result_id: "RESULT-001", rights_status: "PUBLIC_REUSE_ALLOWED", source_accessibility: "PUBLIC", redaction_possible: false, public_claim_impact: "NOT_EVALUATED" };
  const publicResult = classifyPublicationEligibility({ ...common, customer_confidentiality: "NONE" });
  const privateResult = classifyPublicationEligibility({ ...common, customer_confidentiality: "CONFIDENTIAL" });
  const mixedResult = classifyPublicationEligibility({ ...common, customer_confidentiality: "MIXED", redaction_possible: true });
  assert.equal(publicResult.publication_eligibility, "PUBLIC_ELIGIBLE");
  assert.equal(privateResult.publication_eligibility, "CUSTOMER_PRIVATE");
  assert.equal(mixedResult.publication_eligibility, "MIXED_REDACTABLE");
  for (const result of [publicResult, privateResult, mixedResult]) {
    assert.equal(result.human_publication_review_required, true);
    assert.equal(result.public_transition_authorized, false);
  }
});

test("V legacy resolver fields remain present", () => {
  const result = resolveQuery("Has a named 800VDC SST system been commercially deployed?");
  for (const field of ["query", "result", "matched_claims", "method_contract", "commercial_next_step"]) assert.ok(Object.hasOwn(result, field));
});

test("W medical boundary blocks personal quote and commercial action", () => {
  const result = resolveQuery("What is my chance of surviving lung cancer with this treatment?");
  assert.equal(getClaim(result, "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY").state, "NOT_ESTABLISHED");
  assert.equal(result.medical_boundary, "This public evidence object does not provide patient-specific medical advice.");
  assert.equal(result.quote_available, false);
  assert.equal(result.commercial_next_step, null);
});

test("Z commercial handoff is prefilled but remains human-authorized", () => {
  const result = resolveQuery("Has 800VDC been commercially deployed and proven economically superior?");
  assert.equal(result.commercial_next_step.capability, "VERIFY_CLAIM");
  assert.equal(result.commercial_next_step.quote_ready, true);
  assert.equal(result.commercial_next_step.human_authorization_required, true);
  assert.match(result.commercial_next_step.url, /^https:\/\/structevidence\.com\/verify\/\?/);
  assert.equal(result.verification_quote.research_authorized, false);
});
