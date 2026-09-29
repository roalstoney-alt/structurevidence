import { CLAIMS } from "./claims.js";

const METHOD_CONTRACT = "https://structurevidence.org/method-contract.json";
const VERIFY_URL = "https://structevidence.com/verify/";
const MEDICAL_CASE = "SE-ONC-NSQNSCLC-CN-001";
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

export function resolveQuery(query) {
  const ranked = CLAIMS.map((claim) => ({ claim, match_score: scoreClaim(query, claim) })).filter((row) => row.match_score > 0).sort((a, b) => b.match_score - a.match_score || a.claim.claim_id.localeCompare(b.claim.claim_id));
  if (!ranked.length) {
    return {
      query,
      result: "NO_MATCH",
      matched_claims: [],
      message: "No existing StructureEvidence public claim matched this query.",
      human_action_required: true,
      next_step: VERIFY_URL,
      method_contract: METHOD_CONTRACT,
      commercial_next_step: null,
    };
  }
  const top = ranked[0].match_score;
  const selected = ranked.filter((row) => row.match_score === top).map((row) => publicClaim(row.claim));
  const personalMedical = selected.some((claim) => claim.case_id === MEDICAL_CASE) && /\b(my|me|mine|personal|patient-specific)\b/i.test(query);
  return {
    query,
    result: "MATCHED",
    matched_claims: selected,
    method_contract: METHOD_CONTRACT,
    commercial_next_step: null,
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
