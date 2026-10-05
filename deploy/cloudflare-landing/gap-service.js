import {
  ATTRIBUTION_OPTIONS,
  GAP_EFFECTS,
  GAP_SUBMISSION_STATES,
  OPEN_EVIDENCE_GAPS,
  OPEN_EVIDENCE_GAP_PROTOCOL,
  STATIC_GAP_CHANGE_LOG,
  findGap
} from "./gaps.js";

const MAX_BODY_BYTES = 65_536;
const EFFECTS = new Set(GAP_EFFECTS);
const ATTRIBUTIONS = new Set(ATTRIBUTION_OPTIONS);
const STATES = new Set(GAP_SUBMISSION_STATES);
const PUBLIC_CHANGE_TYPES = new Set(["STATE_CHANGED", "NO_STATE_CHANGE", "SCOPE_CLARIFIED"]);
const securityHeaders = {
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "x-frame-options": "DENY"
};
const jsonHeaders = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...securityHeaders };
const json = (body, status = 200, extra = {}) => new Response(JSON.stringify(body), { status, headers: { ...jsonHeaders, ...extra } });
const now = () => new Date().toISOString();
const externalId = (prefix) => `${prefix}-${crypto.randomUUID().replaceAll("-", "").slice(0, 20).toUpperCase()}`;
const clean = (value, max) => {
  if (value === undefined || value === null) return null;
  const normalized = String(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  return normalized ? normalized.slice(0, max) : null;
};
const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) && value.length <= 254;
const publicOrigins = (env) => new Set(String(env.PUBLIC_ORIGINS || "").split(",").map((item) => item.trim()).filter(Boolean));
const challengeCors = (request, env) => {
  const origin = request.headers.get("origin");
  return origin && publicOrigins(env).has(origin)
    ? { "access-control-allow-origin": origin, "access-control-allow-methods": "POST, OPTIONS", "access-control-allow-headers": "content-type", vary: "Origin" }
    : {};
};

async function readJson(request) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  if (!String(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) throw new Response("Content-Type must be application/json", { status: 415 });
  const body = await request.text();
  if (new TextEncoder().encode(body).byteLength > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  try { return JSON.parse(body); } catch { throw new Response("Invalid JSON", { status: 400 }); }
}

function normalizeChallenge(input, gapId) {
  const allowed = new Set(["gap_id", "evidence_reference", "effect", "note", "attribution_preference", "attribution_name", "organization_name", "contact_email"]);
  if (!input || typeof input !== "object" || Array.isArray(input) || Object.keys(input).some((key) => !allowed.has(key))) throw new Response("Unsupported challenge field", { status: 400 });
  const bodyGapId = clean(input.gap_id, 64);
  if (bodyGapId && bodyGapId !== gapId) throw new Response("gap_id does not match route", { status: 400 });
  const evidenceReference = clean(input.evidence_reference, 2000);
  const effect = clean(input.effect, 32)?.toUpperCase();
  const attributionPreference = clean(input.attribution_preference, 32)?.toUpperCase();
  let attributionName = clean(input.attribution_name, 200);
  let organizationName = clean(input.organization_name, 300);
  const contactEmail = clean(input.contact_email, 254)?.toLowerCase() ?? null;
  if (!evidenceReference || evidenceReference.length < 8) throw new Response("A public URL or document reference is required", { status: 400 });
  if (!EFFECTS.has(effect)) throw new Response("Invalid effect", { status: 400 });
  if (!ATTRIBUTIONS.has(attributionPreference)) throw new Response("Invalid attribution_preference", { status: 400 });
  if (contactEmail && !validEmail(contactEmail)) throw new Response("Invalid contact_email", { status: 400 });
  if (attributionPreference === "NAMED" && !attributionName) throw new Response("NAMED attribution requires attribution_name", { status: 400 });
  if (attributionPreference === "ORGANIZATION_ONLY" && !organizationName) throw new Response("ORGANIZATION_ONLY attribution requires organization_name", { status: 400 });
  if (attributionPreference === "ANONYMOUS") { attributionName = null; organizationName = null; }
  if (attributionPreference === "ORGANIZATION_ONLY") attributionName = null;
  return { evidenceReference, effect, note: clean(input.note, 4000), attributionPreference, attributionName, organizationName, contactEmail };
}

async function clientKeyHash(request, env) {
  const salt = clean(env.GAP_RATE_LIMIT_SALT, 500);
  if (!salt || salt.startsWith("CONFIGURE_")) throw new Response("Challenge protection is not configured", { status: 503 });
  const clientIp = request.headers.get("cf-connecting-ip") || "unknown-client";
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(`${salt}:${clientIp}`));
  return [...new Uint8Array(digest)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

async function publicChanges(gapId, env) {
  const initial = STATIC_GAP_CHANGE_LOG.filter((change) => change.gap_id === gapId);
  if (!env.CUSTOMER_CASES_DB) return initial;
  try {
    const result = await env.CUSTOMER_CASES_DB.prepare("SELECT change_id, gap_id, challenge_id, change_type, summary, attribution, previous_state, new_state, changed_at, 1 AS append_only FROM gap_public_changes WHERE gap_id = ? ORDER BY changed_at ASC, change_id ASC").bind(gapId).all();
    return [...initial, ...(result.results || [])];
  } catch (error) {
    console.error(JSON.stringify({ event: "gap_public_change_read_failed", gap_id: gapId, error: error instanceof Error ? error.message : "unknown" }));
    return initial;
  }
}

async function submitChallenge(request, gap, env) {
  const origin = request.headers.get("origin"), cors = challengeCors(request, env);
  if (origin && !cors["access-control-allow-origin"]) return json({ error: "Origin not allowed" }, 403);
  if (!env.CUSTOMER_CASES_DB) return json({ error: "Challenge service is not configured" }, 503, cors);
  const input = normalizeChallenge(await readJson(request), gap.gap_id);
  const createdAt = now(), challengeId = externalId("SE-GAP-CHL"), eventId = externalId("SE-GAP-EVT"), clientHash = await clientKeyHash(request, env);
  const challengeInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO gap_challenges (challenge_id, gap_id, evidence_reference, effect, note, attribution_preference, attribution_name, organization_name, contact_email, state, client_key_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', ?, ?, ?)").bind(challengeId, gap.gap_id, input.evidenceReference, input.effect, input.note, input.attributionPreference, input.attributionName, input.organizationName, input.contactEmail, clientHash, createdAt, createdAt);
  const eventInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO gap_challenge_events (event_id, challenge_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, 'SUBMITTED', ?, 'PUBLIC_CONTRIBUTOR', NULL, 'SUBMITTED', ?)").bind(eventId, challengeId, createdAt, "Public evidence challenge recorded for human screening; no gap or claim state changed.");
  try { await env.CUSTOMER_CASES_DB.batch([challengeInsert, eventInsert]); }
  catch (error) {
    if (String(error instanceof Error ? error.message : error).includes("gap_challenge_rate_limited")) return json({ error: "Rate limit exceeded: maximum 5 submissions per 10 minutes" }, 429, { ...cors, "retry-after": "600" });
    throw error;
  }
  return json({ challenge_id: challengeId, gap_id: gap.gap_id, state: "SUBMITTED", acknowledgement_target: OPEN_EVIDENCE_GAP_PROTOCOL.acknowledgement_target, initial_review_target: OPEN_EVIDENCE_GAP_PROTOCOL.initial_review_target, state_changed: false }, 201, cors);
}

export async function handleGapApi(request, url, env) {
  if (url.pathname === "/api/gaps" && request.method === "GET") return json({ protocol: OPEN_EVIDENCE_GAP_PROTOCOL, count: OPEN_EVIDENCE_GAPS.length, gaps: OPEN_EVIDENCE_GAPS }, 200, { "access-control-allow-origin": "*", "cache-control": "public, max-age=300" });
  const match = url.pathname.match(/^\/api\/gaps\/([^/]+)(?:\/(challenge))?$/);
  if (!match) return null;
  const gap = findGap(decodeURIComponent(match[1]));
  if (!gap) return json({ error: "Gap not found" }, 404, request.method === "GET" ? { "access-control-allow-origin": "*" } : challengeCors(request, env));
  if (!match[2] && request.method === "GET") return json({ gap, change_log: await publicChanges(gap.gap_id, env), no_auto_state_change: true }, 200, { "access-control-allow-origin": "*", "cache-control": "public, max-age=60" });
  if (match[2] === "challenge" && request.method === "OPTIONS") return new Response(null, { status: 204, headers: challengeCors(request, env) });
  if (match[2] === "challenge" && request.method === "POST") return submitChallenge(request, gap, env);
  return json({ error: "Method not allowed" }, 405, { allow: match[2] ? "POST, OPTIONS" : "GET" });
}

async function listChallenges(url, env) {
  const state = clean(url.searchParams.get("state"), 32);
  if (state && !STATES.has(state)) return json({ error: "Invalid state filter" }, 400);
  const limit = Math.min(Math.max(Number(url.searchParams.get("limit") || 50), 1), 100);
  const query = state
    ? env.CUSTOMER_CASES_DB.prepare("SELECT challenge_id, gap_id, evidence_reference, effect, attribution_preference, attribution_name, organization_name, contact_email, state, created_at, updated_at FROM gap_challenges WHERE state = ? ORDER BY created_at DESC LIMIT ?").bind(state, limit)
    : env.CUSTOMER_CASES_DB.prepare("SELECT challenge_id, gap_id, evidence_reference, effect, attribution_preference, attribution_name, organization_name, contact_email, state, created_at, updated_at FROM gap_challenges ORDER BY created_at DESC LIMIT ?").bind(limit);
  const result = await query.all();
  return json({ challenges: result.results || [] });
}

async function challengeDetail(challengeId, env) {
  const challenge = await env.CUSTOMER_CASES_DB.prepare("SELECT challenge_id, gap_id, evidence_reference, effect, note, attribution_preference, attribution_name, organization_name, contact_email, state, created_at, updated_at FROM gap_challenges WHERE challenge_id = ?").bind(challengeId).first();
  if (!challenge) return json({ error: "Challenge not found" }, 404);
  const events = await env.CUSTOMER_CASES_DB.prepare("SELECT event_id, event_type, event_at, actor, previous_state, new_state, note FROM gap_challenge_events WHERE challenge_id = ? ORDER BY event_at ASC, event_id ASC").bind(challengeId).all();
  return json({ challenge, events: events.results || [] });
}

async function patchChallenge(request, challengeId, env, actor) {
  const current = await env.CUSTOMER_CASES_DB.prepare("SELECT challenge_id, gap_id, state FROM gap_challenges WHERE challenge_id = ?").bind(challengeId).first();
  if (!current) return json({ error: "Challenge not found" }, 404);
  const input = await readJson(request), state = clean(input.state, 32)?.toUpperCase(), note = clean(input.note, 4000);
  if (Object.keys(input).some((key) => !new Set(["state", "note"]).has(key))) return json({ error: "Unsupported admin field" }, 400);
  if (!STATES.has(state)) return json({ error: "Invalid state" }, 400);
  if (state === current.state) return json({ error: "No material change" }, 400);
  const updatedAt = now();
  const update = env.CUSTOMER_CASES_DB.prepare("UPDATE gap_challenges SET state = ?, updated_at = ? WHERE challenge_id = ?").bind(state, updatedAt, challengeId);
  const event = env.CUSTOMER_CASES_DB.prepare("INSERT INTO gap_challenge_events (event_id, challenge_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)").bind(externalId("SE-GAP-EVT"), challengeId, state, updatedAt, actor.email, current.state, state, note);
  await env.CUSTOMER_CASES_DB.batch([update, event]);
  return challengeDetail(challengeId, env);
}

function publicAttribution(challenge) {
  if (challenge.attribution_preference === "ANONYMOUS") return "Anonymous contributor";
  if (challenge.attribution_preference === "ORGANIZATION_ONLY") return challenge.organization_name;
  return [challenge.attribution_name, challenge.organization_name].filter(Boolean).join(" — ");
}

async function publishChallengeOutcome(request, challengeId, env, actor) {
  const challenge = await env.CUSTOMER_CASES_DB.prepare("SELECT challenge_id, gap_id, state, attribution_preference, attribution_name, organization_name FROM gap_challenges WHERE challenge_id = ?").bind(challengeId).first();
  if (!challenge) return json({ error: "Challenge not found" }, 404);
  const input = await readJson(request), changeType = clean(input.change_type, 32)?.toUpperCase(), summary = clean(input.summary, 4000), previousState = clean(input.previous_state, 200), newState = clean(input.new_state, 200);
  const allowed = new Set(["change_type", "summary", "previous_state", "new_state"]);
  if (Object.keys(input).some((key) => !allowed.has(key))) return json({ error: "Unsupported public change field" }, 400);
  if (!PUBLIC_CHANGE_TYPES.has(changeType) || !summary) return json({ error: "Valid change_type and summary are required" }, 400);
  if (challenge.state !== changeType) return json({ error: "Challenge must first be moved by a human reviewer to the matching final state" }, 409);
  const changeId = externalId("SE-GAP-CHANGE"), changedAt = now(), attribution = publicAttribution(challenge);
  await env.CUSTOMER_CASES_DB.prepare("INSERT INTO gap_public_changes (change_id, gap_id, challenge_id, change_type, summary, attribution, previous_state, new_state, changed_at, reviewer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)").bind(changeId, challenge.gap_id, challengeId, changeType, summary, attribution, previousState, newState, changedAt, actor.email).run();
  return json({ change_id: changeId, gap_id: challenge.gap_id, challenge_id: challengeId, change_type: changeType, summary, attribution, previous_state: previousState, new_state: newState, changed_at: changedAt, append_only: true }, 201);
}

export async function handleGapAdminApi(request, url, env, actor) {
  if (url.pathname === "/api/admin/gap-challenges" && request.method === "GET") return listChallenges(url, env);
  const match = url.pathname.match(/^\/api\/admin\/gap-challenges\/([^/]+)(?:\/(public-change))?$/);
  if (!match) return null;
  const challengeId = decodeURIComponent(match[1]);
  if (!match[2] && request.method === "GET") return challengeDetail(challengeId, env);
  if (!match[2] && request.method === "PATCH") return patchChallenge(request, challengeId, env, actor);
  if (match[2] === "public-change" && request.method === "POST") return publishChallengeOutcome(request, challengeId, env, actor);
  return json({ error: "Method not allowed" }, 405);
}
