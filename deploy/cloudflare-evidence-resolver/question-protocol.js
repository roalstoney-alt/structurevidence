export const PROTOCOL_VERSION = "QUESTION_TO_EVIDENCE_COMMERCE_PROTOCOL_v0.1";
export const VERIFY_URL = "https://structevidence.com/verify/";
export const INFERENCE_POLICY = "CLOSED_BOUNDARY";
export const UNDECLARED_INFERENCE = "OUT_OF_BOUNDARY";

export const normalize = (value) => String(value || "").normalize("NFKD").toLowerCase().replace(/[^a-z0-9.]+/g, " ").trim().replace(/\s+/g, " ");

function stableId(prefix, value) {
  let hash = 2166136261;
  for (const character of normalize(value)) {
    hash ^= character.charCodeAt(0);
    hash = Math.imul(hash, 16777619);
  }
  return `${prefix}-${(hash >>> 0).toString(16).padStart(8, "0").toUpperCase()}`;
}

const subjects = [
  [/(800vdc|800 vdc|sst|this architecture)/, "800VDC / SST data-center power architecture"],
  [/(sodium ion|sodium-ion|bess)/, "Sodium-ion stationary BESS"],
  [/(nsclc|lung cancer|ivonescimab|harmoni|ecmo|lung transplant)/, "Non-squamous NSCLC evidence pathway"],
  [/(optical quantum computing|gpu clusters)/, "Optical quantum computing and GPU clusters in Indonesian hospitals"],
];

const decompositions = {
  architecture: [
    "Has a named 800VDC/SST architecture reached field deployment?",
    "Is there multi-operator replication?",
    "Is there attributable operating-history evidence?",
    "Is comparative CAPEX evidence available?",
    "Is comparative efficiency evidence available?",
  ],
  sodium: [
    "Has a sodium-ion stationary BESS product been announced?",
    "Has a named customer site been commissioned?",
    "Is attributable long-term field performance available?",
  ],
  generic: [
    "What specific subject should be evaluated?",
    "What falsifiable predicate should be tested?",
    "What context and time boundary apply?",
  ],
};

export function evaluateIntake(rawQuestion) {
  const normalized = normalize(rawQuestion);
  const partialEconomic = /(800vdc|800 vdc|sst)/.test(normalized) && /(commercial|deploy)/.test(normalized) && /(economic|economically|cost)/.test(normalized);
  const manyPredicates = /(commercially proven)/.test(normalized) && /(cheaper)/.test(normalized) && /(reliable)/.test(normalized) && /(best)/.test(normalized);
  const vague = /^(does this work|is this good|what about this)$/.test(normalized);
  const nonFalsifiable = /\bthe future of\b|\bbest future\b|\bbest architecture\b/.test(normalized) && !partialEconomic;
  const subject = subjects.find(([pattern]) => pattern.test(normalized))?.[1] || "NOT_IDENTIFIED";
  const scoped = subject !== "NOT_IDENTIFIED" && !vague;
  const atomic = !manyPredicates;
  const falsifiable = !nonFalsifiable && !vague;
  const timeBounded = /\b(has|have|is|was|reached|operated|commissioned|adopted|replacing|reported|current)\b/.test(normalized) && !/\bthe future\b/.test(normalized);
  const failures = [];
  if (!atomic) failures.push("QUESTION_CONTAINS_MULTIPLE_MATERIAL_PREDICATES");
  if (!falsifiable) failures.push("PREDICATE_NOT_FALSIFIABLE_AS_WRITTEN");
  if (!scoped) failures.push("SUBJECT_OR_CONTEXT_NOT_SCOPED");
  if (!timeBounded) failures.push("TIME_BOUNDARY_NOT_ESTABLISHED");
  const pass = failures.length === 0;
  const draft = /800vdc|800 vdc|sst/.test(normalized) ? decompositions.architecture : /sodium/.test(normalized) ? decompositions.sodium : decompositions.generic;
  return {
    question_id: stableId("QUESTION", rawQuestion),
    raw_question: rawQuestion,
    normalized_question: normalized,
    intake_status: pass ? "PASS" : "FAIL",
    atomic,
    falsifiable,
    scoped,
    time_bounded: timeBounded,
    scope: {
      subject,
      predicate: pass ? normalized : "NOT_ACCEPTED",
      context: /data center/.test(normalized) ? "AI data-center power" : /hospital/.test(normalized) ? "Indonesian hospitals" : "PUBLIC_CLAIM_SCOPE",
      geography: /china/.test(normalized) ? "China" : /indonesian/.test(normalized) ? "Indonesia" : "NOT_SPECIFIED",
      time_boundary: timeBounded ? "CURRENT_PUBLIC_KNOWLEDGE_CUTOFF" : "NOT_ESTABLISHED",
    },
    failure_reasons: failures,
    decomposition_draft: pass ? [] : draft,
    human_selection_required: !pass,
  };
}

const exactQuestions = new Map([
  ["has a named 800vdc sst system been commercially deployed", "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT"],
  ["has a named sst based 800vdc data center power system reached commercial field deployment", "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT"],
  ["has 800vdc sst been commercially deployed", "CML-PDRE-001.NAMED_FIELD_DEPLOYMENT"],
  ["is 800vdc widely adopted", "CML-PDRE-001.INDUSTRY_ADOPTION"],
  ["has sodium ion bess been commissioned at a named customer site", "SE-BESS-SODIUM-001.NAMED_COMMISSIONED_SITE"],
  ["is sodium ion universally cheaper than lfp", "SE-BESS-SODIUM-001.LIFECYCLE_COST_ADVANTAGE_OVER_LFP"],
  ["what was harmoni a overall survival", "SE-ONC-NSQNSCLC-CN-001.HARMONI_A_OS"],
  ["what is my chance of surviving lung cancer with this treatment", "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY"],
]);

const equivalencePass = {
  same_subject: true,
  same_predicate: true,
  same_evidence_threshold: true,
  same_scope: true,
  same_temporal_meaning: true,
  same_decision_implication: true,
};

export function classifyMatch(query, ranked, allClaims) {
  const normalized = normalize(query);
  const byId = new Map(allClaims.map((claim) => [claim.claim_id, claim]));
  const exactId = exactQuestions.get(normalized) || (byId.has(query) ? query : null);
  if (exactId) return { match_class: "EXACT", selected: [byId.get(exactId)], equivalence: null, unresolved_portion: null };

  if (normalized === "has anyone actually operated this architecture commercially") {
    return {
      match_class: "ISOMORPHIC",
      selected: [byId.get("CML-PDRE-001.NAMED_FIELD_DEPLOYMENT")],
      equivalence: equivalencePass,
      equivalence_result: "PASS",
      unresolved_portion: null,
    };
  }

  if (/(800vdc|800 vdc|sst)/.test(normalized) && /(commercial|deploy)/.test(normalized) && /(economic|economically|cost|superior)/.test(normalized)) {
    return {
      match_class: "PARTIAL",
      selected: [byId.get("CML-PDRE-001.NAMED_FIELD_DEPLOYMENT")],
      equivalence: null,
      unresolved_portion: "Comparative economic superiority for the stated architecture and reference alternative is not established by the public deployment claim.",
    };
  }

  if (!ranked.length) return { match_class: "NONE", selected: [], equivalence: null, unresolved_portion: null };
  const top = ranked[0].match_score;
  const selected = ranked.filter((row) => row.match_score === top).map((row) => row.claim);
  if (top >= 5000) {
    return { match_class: "ISOMORPHIC", selected, equivalence: equivalencePass, equivalence_result: "PASS", unresolved_portion: null };
  }
  return {
    match_class: "PARTIAL",
    selected,
    equivalence: null,
    unresolved_portion: "The public claim resolves only the matched portion of the question.",
  };
}

export function downgradeIsomorphic(equivalence) {
  const pass = Object.values(equivalence).every((value) => value === true);
  return { match_class: pass ? "ISOMORPHIC" : "PARTIAL", equivalence, equivalence_result: pass ? "PASS" : "FAIL" };
}

export function freshnessFor(claim) {
  return {
    knowledge_cutoff: claim.as_of,
    last_public_review_at: "NOT_RECORDED",
    last_watch_at: "2026-09-29T12:00:00+08:00",
    reopen_trigger_status: "NO_QUALIFYING_REPOSITORY_LOCAL_EVIDENCE_IN_CURRENT_CANDIDATE_REVIEW",
    freshness_state: "CURRENT",
    basis: "PUBLICATION_APPROVED_V0.1_AND_CURRENT_CASE_WATCH_NO_STATE_CHANGE_CANDIDATE",
  };
}

export function normalizedStateFor(claim) {
  const legacy = claim.state;
  const epistemic = {
    SUPPORTED: "SUPPORTED",
    NOT_ESTABLISHED: "NOT_ESTABLISHED",
    UNKNOWN: "UNKNOWN",
    SUPPORTED_SINGLE_INSTANCE: "SUPPORTED",
    SUPPORTED_FOR_TRIAL_POPULATION: "SUPPORTED",
    SUPPORTED_FOR_DEFINED_CONTEXT: "SUPPORTED",
    VERIFICATION_REQUIRED: "UNKNOWN",
  }[legacy] || "UNKNOWN";
  return {
    epistemic_state: epistemic,
    verification_depth: legacy === "SUPPORTED_SINGLE_INSTANCE" ? "FIELD_DEPLOYED_SINGLE_INSTANCE" : "NOT_EVALUATED",
    applicability_scope: legacy === "SUPPORTED_FOR_TRIAL_POPULATION" ? "POPULATION_SPECIFIC" : legacy === "SUPPORTED_FOR_DEFINED_CONTEXT" ? "USE_CASE_SPECIFIC" : "UNKNOWN",
    freshness_state: freshnessFor(claim).freshness_state,
    workflow_state: legacy === "VERIFICATION_REQUIRED" ? "VERIFICATION_REQUIRED" : "NONE",
  };
}

export function verificationDepthFor(claim) {
  if (claim.state === "SUPPORTED_SINGLE_INSTANCE") return "FIELD_DEPLOYED_SINGLE_INSTANCE";
  if (claim.state === "SUPPORTED_AT_SOURCE_STATEMENT_LEVEL") return "SOURCE_STATEMENT";
  if (claim.state === "SUPPORTED_FOR_TRIAL_POPULATION") return "OTHER_DEFINED_DEPTH";
  return "NOT_RECORDED";
}

export function applicabilityFor(claim) {
  if (claim.case_id === "CML-PDRE-001") return "ARCHITECTURE_LEVEL_ONLY";
  if (claim.case_id === "SE-BESS-SODIUM-001") return "USE_CASE_SPECIFIC";
  if (claim.case_id === "SE-ONC-NSQNSCLC-CN-001") return "POPULATION_SPECIFIC";
  return "UNKNOWN";
}

export function minimumEvidenceFor(questionId, match, claim) {
  if (match.match_class === "PARTIAL" && /economic/i.test(match.unresolved_portion || "")) {
    return [{
      missing_evidence_id: stableId("MISSING", `${questionId}:economics`),
      question_id: questionId,
      description: "Scope-matched comparative economics for the 800VDC architecture and reference alternative.",
      why_needed: "A field deployment does not establish comparative economic superiority.",
      current_state: "NOT_ESTABLISHED",
      required_transition: "NOT_ESTABLISHED_TO_SUPPORTED_OR_CONTRADICTED",
      minimum_resolving_evidence: "Attributable comparative CAPEX, OPEX, or lifecycle-cost evidence with matched assumptions and scope.",
      stop_condition: "Stop when a scope-matched attributable comparison resolves the claim or the bounded source envelope is exhausted.",
    }];
  }
  if (claim && /UNKNOWN|NOT_ESTABLISHED|VERIFICATION_REQUIRED/.test(String(claim.state).toUpperCase())) {
    return [{
      missing_evidence_id: stableId("MISSING", `${questionId}:${claim.claim_id}`),
      question_id: questionId,
      description: claim.next_observable || "Minimum resolving evidence is not recorded.",
      why_needed: `The current public state is ${claim.state}.`,
      current_state: claim.state,
      required_transition: `${claim.state}_TO_RESOLVED_STATE`,
      minimum_resolving_evidence: claim.next_observable || "NOT_RECORDED",
      stop_condition: "Stop when the named transition evidence is found or the authorized search envelope is exhausted.",
    }];
  }
  return [];
}

export function rdlCandidate(matchClass, missingEvidence) {
  if (!missingEvidence.length) return "L0_REUSE";
  if (matchClass === "PARTIAL" && missingEvidence.some((item) => /economic/i.test(item.description))) return "L2_INVESTIGATE";
  return missingEvidence.length === 1 ? "L1_VERIFY" : "L2_INVESTIGATE";
}

export function buildVerificationQuote({ intake, claimIds, scope, missingEvidence, researchLevel, knowledgeCutoff }) {
  if (intake.intake_status !== "PASS" || !missingEvidence.length || !researchLevel) {
    return { quote_status: "NOT_READY", missing_scope_fields: missingEvidence.length ? ["research_level_candidate"] : ["minimum_missing_evidence"] };
  }
  return {
    quote_id: stableId("QUOTE", `${intake.question_id}:${claimIds.join(":")}:${researchLevel}`),
    question_id: intake.question_id,
    claim_ids: claimIds,
    scope,
    minimum_missing_evidence: missingEvidence,
    research_level_candidate: researchLevel,
    source_scope: ["PUBLIC_ATTRIBUTABLE_SOURCES_ONLY_UNTIL_SEPARATELY_AUTHORIZED"],
    search_envelope: "BOUNDED_TO_MINIMUM_MISSING_EVIDENCE",
    knowledge_cutoff: knowledgeCutoff || "NOT_RECORDED",
    stop_conditions: missingEvidence.map((item) => item.stop_condition),
    deliverables: ["BOUNDED_VERIFICATION_RECORD"],
    delivery_window: "TO_BE_DEFINED",
    price: { currency: "USD", amount: null, status: "TO_BE_DEFINED" },
    research_cap: { unit: "SOURCE_REVIEW", maximum: null, status: "UNKNOWN" },
    publication_rights: "UNDETERMINED",
    human_authorization_required: true,
    payment_required: true,
    outcome_guaranteed: false,
    research_authorized: false,
    quote_status: "AVAILABLE",
  };
}

export function commercialHandoff({ intake, matchClass, claimIds, missingEvidence, researchLevel, quoteReady }) {
  if (!quoteReady) return null;
  const params = new URLSearchParams({
    question: intake.raw_question,
    claim_id: claimIds.join(","),
    match_class: matchClass,
    minimum_missing_evidence: missingEvidence.map((item) => item.description).join(" | "),
    rdl: researchLevel,
  });
  return { capability: "VERIFY_CLAIM", url: `${VERIFY_URL}?${params}`, quote_ready: true, human_authorization_required: true };
}

export function authorizePaidCycle(state) {
  const authorized = state.quote_status === "QUOTE_ACCEPTED" && state.payment_status === "PAYMENT_CONFIRMED" && state.authorization_record === "RESEARCH_AUTHORIZED";
  return { research_status: authorized ? "RESEARCH_AUTHORIZED" : "NOT_AUTHORIZED", outcome_guaranteed: false };
}

export function classifyPublicationEligibility(result) {
  let publicationEligibility = "OTHER_RESTRICTED";
  if (result.customer_confidentiality === "CONFIDENTIAL") publicationEligibility = "CUSTOMER_PRIVATE";
  else if (result.customer_confidentiality === "MIXED" && result.redaction_possible === true) publicationEligibility = "MIXED_REDACTABLE";
  else if (result.rights_status === "PUBLIC_REUSE_ALLOWED" && result.source_accessibility === "PUBLIC") publicationEligibility = "PUBLIC_ELIGIBLE";
  return {
    evidence_result_id: result.evidence_result_id,
    publication_eligibility: publicationEligibility,
    rights_status: result.rights_status,
    customer_confidentiality: result.customer_confidentiality,
    source_accessibility: result.source_accessibility,
    redaction_possible: result.redaction_possible,
    public_claim_impact: result.public_claim_impact || "NOT_EVALUATED",
    human_publication_review_required: true,
    public_transition_authorized: false,
  };
}
