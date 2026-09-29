import { CLAIMS } from "./claims.js";
import {
  PROTOCOL_VERSION,
  INFERENCE_POLICY,
  UNDECLARED_INFERENCE,
  applicabilityFor,
  buildVerificationQuote,
  classifyMatch,
  commercialHandoff,
  evaluateIntake,
  freshnessFor,
  minimumEvidenceFor,
  normalizedStateFor,
  rdlCandidate,
  verificationDepthFor,
} from "./question-protocol.js";

const METHOD_CONTRACT = "https://structurevidence.org/method-contract.json";
const VERIFY_URL = "https://structevidence.com/verify/";
const MEDICAL_CASE = "SE-ONC-NSQNSCLC-CN-001";
const SNAPSHOT = Object.freeze({
  commit: "58c7c4fe9fa334e030080cf7ab352c222b326ec2",
  repository: "https://github.com/roalstoney-alt/structurevidence",
  permalink: "https://github.com/roalstoney-alt/structurevidence/tree/58c7c4fe9fa334e030080cf7ab352c222b326ec2",
});
const DECISION_OWNERSHIP = Object.freeze({
  agent_role: "EVIDENCE_INTERPRETATION",
  final_decision_authority: "RESPONSIBLE_ACTOR",
});
const securityHeaders = {
  "access-control-allow-origin": "*",
  "cache-control": "no-store",
  "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
  "x-content-type-options": "nosniff",
  "x-frame-options": "DENY",
  "referrer-policy": "no-referrer",
};

const normalize = (value) => String(value || "").normalize("NFKD").toLowerCase().replace(/[^a-z0-9.]+/g, " ").trim().replace(/\s+/g, " ");
const tokens = (value) => new Set(normalize(value).split(" ").filter(Boolean));
const weakWords = new Set(["a", "an", "and", "as", "at", "be", "been", "for", "has", "have", "in", "is", "it", "of", "or", "the", "this", "to", "was", "what", "with"]);

function scoreClaim(query, claim) {
  const normalized = normalize(query);
  if (!normalized) return 0;
  if (normalized === normalize(claim.claim_id)) return 10000;
  let score = 0;
  for (const alias of claim.aliases || []) {
    const phrase = normalize(alias);
    if (phrase.length >= 4 && (normalized.includes(phrase) || phrase.includes(normalized))) {
      score = Math.max(score, 5000 + phrase.split(" ").length);
    }
  }
  const queryTokens = tokens(query);
  const keywordMatches = (claim.keywords || []).filter((keyword) => {
    const phrase = normalize(keyword);
    return phrase.includes(" ") ? normalized.includes(phrase) : queryTokens.has(phrase);
  }).length;
  if (keywordMatches >= 2) score = Math.max(score, keywordMatches * 200);
  for (const candidate of [claim.statement, claim.case_title]) {
    const candidateTokens = tokens(candidate);
    const overlap = [...queryTokens].filter((token) => token.length >= 3 && !weakWords.has(token) && candidateTokens.has(token)).length;
    if (overlap >= 2) score = Math.max(score, overlap * 100);
  }
  return score;
}

const unresolved = (state) => {
  const value = String(state).toUpperCase();
  return value.includes("UNKNOWN") || value.includes("NOT_ESTABLISHED") || value.includes("VERIFICATION_REQUIRED");
};

function publicClaim(claim) {
  const result = {
    claim_id: claim.claim_id,
    case_id: claim.case_id,
    state: claim.state,
    normalized_state: normalizedStateFor(claim),
    as_of: claim.as_of,
    statement: claim.statement,
    supports: claim.supports,
    does_not_support: claim.does_not_support,
    unknowns: claim.unknowns,
    next_observable: claim.next_observable,
    canonical_url: claim.canonical_url,
    resolution_status: unresolved(claim.state) ? "UNRESOLVED" : "BOUNDED_SUPPORT",
  };
  if (result.resolution_status === "UNRESOLVED") {
    result.available_capability = "VERIFY_CLAIM";
    result.human_authorization_required = true;
  }
  return result;
}

function publicStopPoint(claim) {
  const freshness = freshnessFor(claim);
  return {
    claim_id: claim.claim_id,
    state: claim.state,
    normalized_state: normalizedStateFor(claim),
    supports: claim.supports,
    does_not_support: claim.does_not_support,
    as_of: claim.as_of,
    protocol_version: PROTOCOL_VERSION,
    snapshot: SNAPSHOT,
    freshness: freshness.freshness_state,
    freshness_metadata: freshness,
    verification_depth: verificationDepthFor(claim),
    applicability: applicabilityFor(claim),
    unknowns: claim.unknowns,
    next_observable: claim.next_observable,
    canonical_url: claim.canonical_url,
    inference_policy: INFERENCE_POLICY,
    decision_ownership: DECISION_OWNERSHIP,
  };
}

export function resolveQuery(query) {
  const intake = evaluateIntake(query);
  const protocolBase = {
    protocol_version: PROTOCOL_VERSION,
    query,
    intake,
    method_contract: METHOD_CONTRACT,
    human_authorization_required: true,
    inference_policy: INFERENCE_POLICY,
    undeclared_inference: UNDECLARED_INFERENCE,
    snapshot: SNAPSHOT,
    decision_ownership: DECISION_OWNERSHIP,
  };
  if (intake.intake_status === "FAIL") {
    return {
      ...protocolBase,
      result: "NO_MATCH",
      match_class: null,
      matched_claims: [],
      public_stop_point: null,
      sufficiency: "UNKNOWN",
      resolution_action: "DECOMPOSE_AND_STOP",
      minimum_missing_evidence: [],
      research_level_candidate: null,
      available_capability: null,
      quote_available: false,
      verification_quote: null,
      commercial_next_step: null,
      human_action_required: true,
      message: "Question intake failed. Human selection or reframing is required before claim matching.",
    };
  }
  const ranked = CLAIMS.map((claim) => ({ claim, match_score: scoreClaim(query, claim) })).filter((row) => row.match_score > 0).sort((a, b) => b.match_score - a.match_score || a.claim.claim_id.localeCompare(b.claim.claim_id));
  const match = classifyMatch(query, ranked, CLAIMS);
  if (match.match_class === "NONE") {
    return {
      ...protocolBase,
      result: "NO_MATCH",
      match_class: "NONE",
      matched_claims: [],
      public_stop_point: null,
      sufficiency: "UNKNOWN",
      resolution_action: "NO_PUBLIC_MATCH",
      minimum_missing_evidence: [],
      research_level_candidate: null,
      available_capability: null,
      quote_available: false,
      verification_quote: null,
      message: "No existing StructureEvidence public claim matched this query.",
      human_action_required: true,
      next_step: VERIFY_URL,
      commercial_next_step: null,
    };
  }
  const rawSelected = match.selected;
  const selected = rawSelected.map((claim) => publicClaim(claim));
  const personalMedical = selected.some((claim) => claim.case_id === MEDICAL_CASE) && /\b(my|me|mine|personal|patient-specific)\b/i.test(query);
  const primary = rawSelected[0];
  const stopPoint = publicStopPoint(primary);
  const missingEvidence = personalMedical ? [] : minimumEvidenceFor(intake.question_id, match, primary);
  const researchLevel = missingEvidence.length ? rdlCandidate(match.match_class, missingEvidence) : "L0_REUSE";
  const unresolvedClaim = selected.some((claim) => claim.resolution_status === "UNRESOLVED");
  const sufficiency = match.match_class === "PARTIAL" ? "PARTIALLY_SUFFICIENT" : unresolvedClaim ? "INSUFFICIENT" : stopPoint.freshness === "CURRENT" ? "SUFFICIENT" : "UNKNOWN";
  const resolutionAction = sufficiency === "SUFFICIENT" ? "CITE_AND_STOP" : missingEvidence.length ? "MINIMUM_MISSING_EVIDENCE_IDENTIFIED" : "STOP";
  const quote = personalMedical ? { quote_status: "NOT_READY", missing_scope_fields: ["SEPARATELY_GOVERNED_MEDICAL_PRODUCT_PATH"] } : buildVerificationQuote({
    intake,
    claimIds: selected.map((claim) => claim.claim_id),
    scope: match.unresolved_portion || `Resolve ${primary.claim_id} within its public boundary.`,
    missingEvidence,
    researchLevel: missingEvidence.length ? researchLevel : null,
    knowledgeCutoff: primary.as_of,
  });
  const quoteReady = quote.quote_status === "AVAILABLE";
  return {
    ...protocolBase,
    result: "MATCHED",
    match_class: match.match_class,
    ...(match.match_class === "ISOMORPHIC" ? { equivalence: match.equivalence, equivalence_result: match.equivalence_result } : {}),
    matched_claims: selected,
    public_stop_point: stopPoint,
    freshness: stopPoint.freshness_metadata,
    sufficiency,
    resolution_action: resolutionAction,
    unresolved_portion: match.unresolved_portion,
    minimum_missing_evidence: missingEvidence,
    research_level_candidate: researchLevel,
    available_capability: quoteReady ? "VERIFY_CLAIM" : null,
    quote_available: quoteReady,
    verification_quote: quote,
    commercial_next_step: commercialHandoff({ intake, matchClass: match.match_class, claimIds: selected.map((claim) => claim.claim_id), missingEvidence, researchLevel, quoteReady }),
    ...(personalMedical ? { medical_boundary: "This public evidence object does not provide patient-specific medical advice." } : {}),
  };
}

function json(value, status = 200, method = "GET") {
  return new Response(method === "HEAD" ? null : JSON.stringify(value, null, 2) + "\n", {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...securityHeaders },
  });
}

export function createWorker() {
  return {
    async fetch(request) {
      const url = new URL(request.url);
      if (url.pathname !== "/resolve") return json({ error: "Not found" }, 404, request.method);
      if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: { allow: "GET, OPTIONS", "access-control-allow-methods": "GET, OPTIONS", ...securityHeaders } });
      if (request.method !== "GET") return new Response("Method not allowed", { status: 405, headers: { allow: "GET, OPTIONS", ...securityHeaders } });
      const query = (url.searchParams.get("q") || "").trim();
      if (!query) return json({ error: "Missing q query parameter" }, 400, request.method);
      return json(resolveQuery(query), 200, request.method);
    },
  };
}

export default createWorker();
