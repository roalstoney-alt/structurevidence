import { createRemoteJWKSet, jwtVerify } from "jose";
import { ADMIN_APP_JS, ADMIN_HTML } from "./admin-ui.js";
import { CAPABILITIES } from "./capabilities.js";
import { COMMERCIAL_APP_JS_UPGRADE as COMMERCIAL_APP_JS, COMMERCIAL_CSS_V2 as COMMERCIAL_CSS, COMMERCIAL_PAGES_V2 as COMMERCIAL_PAGES, localizeIntakePage } from "./commercial-upgrade.js";
import { handleGapAdminApi, handleGapApi } from "./gap-service.js";
import { GAP_APP_JS, GAP_CSS, OPEN_EVIDENCE_GAPS, findGap, renderGapChangeLog, renderGapDetail, renderGapIndex } from "./gaps.js";

const MAX_BODY_BYTES = 65_536;
const CONSENT_VERSION = "SE-CUSTOMER-PRIVACY-v1";
const IDEMPOTENCY_TTL_SECONDS = 86_400;
const PUBLIC_FIELDS = Object.freeze(new Set(["request_type", "email", "decision", "claim_or_question", "decision_deadline", "contact_name", "company", "technical_object", "current_dependency", "alternative_considered", "case_reference", "requested_output", "current_belief", "existing_evidence", "consent_accepted", "consent_version", "turnstile_token"]));
const REQUEST_STATUSES = new Set(["SUBMITTED", "UNDER_REVIEW", "SCOPE_PROPOSED", "AWAITING_CUSTOMER", "AUTHORIZED", "IN_PROGRESS", "DELIVERED", "CLOSED"]);
const AUTH_STATUSES = new Set(["NOT_AUTHORIZED", "L0_REUSE_AUTHORIZED", "L1_VERIFY_AUTHORIZED", "L2_INVESTIGATE_AUTHORIZED", "L3_DEEP_AUTHORIZED"]);
const MANUAL_EVENTS = new Set(["SCOPE_PROPOSED", "CUSTOMER_RESPONSE_RECEIVED", "RESEARCH_STARTED", "DELIVERABLE_SENT", "CASE_CLOSED"]);
const securityHeaders = {
  "x-content-type-options": "nosniff",
  "referrer-policy": "strict-origin-when-cross-origin",
  "permissions-policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
  "x-frame-options": "DENY"
};
const jsonHeaders = { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", ...securityHeaders };
const json = (body, status = 200, extra = {}) => new Response(JSON.stringify(body), { status, headers: { ...jsonHeaders, ...extra } });
const sitemapPaths = Object.freeze([...new Set([
  ...Object.keys(COMMERCIAL_PAGES),
  "/gaps/",
  "/gaps/changes/",
  ...OPEN_EVIDENCE_GAPS.map(({ gap_id }) => `/gaps/${gap_id}/`)
])]);
const sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${sitemapPaths.map((path) => `  <url><loc>https://structevidence.com${path}</loc></url>`).join("\n")}\n</urlset>\n`;
const robotsTxt = "User-agent: *\nAllow: /\nDisallow: /admin/\nDisallow: /api/admin/\nSitemap: https://structevidence.com/sitemap.xml\n";
const now = () => new Date().toISOString();
const externalId = (prefix) => `${prefix}-${crypto.randomUUID().replaceAll("-", "").slice(0, 20).toUpperCase()}`;
const clean = (value, max) => {
  if (value === undefined || value === null) return null;
  const normalized = String(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  return normalized ? normalized.slice(0, max) : null;
};
const strictText = (input, key, max, { required = false } = {}) => {
  const value = input[key];
  if (value === undefined || value === null || value === "") {
    if (required) throw new Response(`${key} is required`, { status: 400 });
    return null;
  }
  if (typeof value !== "string") throw new Response(`${key} must be a string`, { status: 400 });
  if (/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/.test(value)) throw new Response(`${key} contains unsupported control characters`, { status: 400 });
  const normalized = value.trim();
  if (!normalized) {
    if (required) throw new Response(`${key} is required`, { status: 400 });
    return null;
  }
  if (new TextEncoder().encode(normalized).byteLength > max) throw new Response(`${key} is too long`, { status: 400 });
  return normalized;
};
const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) && value.length <= 254;
const validDate = (value) => {
  if (!value) return true;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const parsed = new Date(`${value}T00:00:00.000Z`);
  return !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value;
};

function publicOrigins(env) { return new Set(String(env.PUBLIC_ORIGINS || "").split(",").map((item) => item.trim()).filter(Boolean)); }
function corsHeaders(request, env) {
  const origin = request.headers.get("origin");
  return origin && publicOrigins(env).has(origin) ? { "access-control-allow-origin": origin, "access-control-allow-methods": "POST, OPTIONS", "access-control-allow-headers": "content-type, idempotency-key", vary: "Origin" } : {};
}
function duplicateTopLevelKey(body) {
  const keys = new Set();
  let depth = 0, inString = false, escaped = false, start = -1;
  for (let index = 0; index < body.length; index += 1) {
    const character = body[index];
    if (inString) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === '"') {
        inString = false;
        if (depth === 1) {
          let cursor = index + 1;
          while (/\s/.test(body[cursor] || "")) cursor += 1;
          if (body[cursor] === ":") {
            let key;
            try { key = JSON.parse(body.slice(start, index + 1)); } catch { return null; }
            if (keys.has(key)) return key;
            keys.add(key);
          }
        }
      }
      continue;
    }
    if (character === '"') { inString = true; start = index; }
    else if (character === "{" || character === "[") depth += 1;
    else if (character === "}" || character === "]") depth -= 1;
  }
  return null;
}
async function readJson(request) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  if (!String(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) throw new Response("Content-Type must be application/json", { status: 415 });
  const body = await request.text();
  if (new TextEncoder().encode(body).byteLength > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  if (duplicateTopLevelKey(body)) throw new Response("Duplicate JSON field", { status: 400 });
  try {
    const parsed = JSON.parse(body);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error("not an object");
    return parsed;
  } catch { throw new Response("Invalid JSON object", { status: 400 }); }
}
function normalizeSubmission(input) {
  const unknown = Object.keys(input).find((key) => !PUBLIC_FIELDS.has(key));
  if (unknown) throw new Response("Unsupported public field", { status: 400 });
  const requestType = strictText(input, "request_type", 16, { required: true }).toUpperCase();
  const email = strictText(input, "email", 254, { required: true }).toLowerCase();
  const decision = strictText(input, "decision", 8000);
  const claim = strictText(input, "claim_or_question", 8000);
  if (!new Set(["VERIFY", "CONTEXT"]).has(requestType)) throw new Response("Invalid request_type", { status: 400 });
  if (!email || !validEmail(email)) throw new Response("Valid email is required", { status: 400 });
  if (!decision && !claim) throw new Response("Decision or claim/question is required", { status: 400 });
  if (requestType === "VERIFY" && !claim) throw new Response("Verify requests require claim_or_question", { status: 400 });
  if (requestType === "CONTEXT" && !decision) throw new Response("Context requests require decision", { status: 400 });
  const decisionDeadline = strictText(input, "decision_deadline", 10);
  if (!validDate(decisionDeadline)) throw new Response("Invalid decision_deadline", { status: 400 });
  if (input.consent_accepted !== true) throw new Response("Explicit consent is required", { status: 400 });
  const consentVersion = strictText(input, "consent_version", 80, { required: true });
  if (consentVersion !== CONSENT_VERSION) throw new Response("Unsupported consent version", { status: 400 });
  const turnstileToken = strictText(input, "turnstile_token", 2048, { required: true });
  return { requestType, email, decision, claim, decisionDeadline, consentVersion, turnstileToken, contactName: strictText(input, "contact_name", 200), company: strictText(input, "company", 300), technicalObject: strictText(input, "technical_object", 2000), currentDependency: strictText(input, "current_dependency", 8000), alternativeConsidered: strictText(input, "alternative_considered", 8000), caseReference: strictText(input, "case_reference", 300), requestedOutput: strictText(input, "requested_output", 1000), currentBelief: strictText(input, "current_belief", 4000), existingEvidence: strictText(input, "existing_evidence", 8000) };
}
const hexDigest = async (value) => [...new Uint8Array(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)))].map((byte) => byte.toString(16).padStart(2, "0")).join("");
const fingerprint = (input) => JSON.stringify([input.requestType, input.email, input.decision, input.claim, input.decisionDeadline, input.contactName, input.company, input.technicalObject, input.currentDependency, input.alternativeConsidered, input.caseReference, input.requestedOutput, input.currentBelief, input.existingEvidence, true, input.consentVersion]);
const idempotencyKey = (request) => {
  const value = request.headers.get("idempotency-key");
  if (!value || !/^[A-Za-z0-9_-]{20,128}$/.test(value)) throw new Response("Valid Idempotency-Key is required", { status: 400 });
  return value;
};
async function defaultTurnstileVerifier(token, request, env) {
  const secret = String(env.TURNSTILE_SECRET_KEY || "");
  if (!secret || secret.startsWith("CONFIGURE_")) throw new Response("Human verification is not configured", { status: 503 });
  const form = new FormData();
  form.set("secret", secret); form.set("response", token);
  const remoteIp = request.headers.get("cf-connecting-ip");
  if (remoteIp) form.set("remoteip", remoteIp);
  const configuredTimeout = Number(env.TURNSTILE_TIMEOUT_MS || 5000);
  const timeoutMs = Number.isFinite(configuredTimeout) ? Math.min(Math.max(configuredTimeout, 10), 10_000) : 5000;
  const controller = new AbortController(), timeout = setTimeout(() => controller.abort(), timeoutMs);
  let result;
  try {
    const response = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body: form, signal: controller.signal });
    if (!response.ok) throw new Error("siteverify unavailable");
    result = await response.json();
  } catch { throw new Response("Human verification is temporarily unavailable", { status: 503 }); }
  finally { clearTimeout(timeout); }
  if (!result?.success) throw new Response("Human verification failed", { status: 400 });
  const hostnames = new Set(String(env.TURNSTILE_EXPECTED_HOSTNAMES || "structevidence.com,www.structevidence.com").split(",").map((item) => item.trim()).filter(Boolean));
  if (!result.hostname || !hostnames.has(result.hostname)) throw new Response("Human verification failed", { status: 400 });
  const expectedAction = String(env.TURNSTILE_EXPECTED_ACTION || "public-intake");
  if (result.action !== expectedAction) throw new Response("Human verification failed", { status: 400 });
  return result;
}
async function existingIdempotency(db, scopeHash, keyHash) {
  return db.prepare("SELECT request_id, request_fingerprint_sha256, created_at, expires_at FROM request_idempotency WHERE scope_sha256 = ? AND idempotency_key_sha256 = ? AND expires_at > ?").bind(scopeHash, keyHash, now()).first();
}
async function submitRequest(request, env, turnstileVerifier) {
  const origin = request.headers.get("origin");
  const cors = corsHeaders(request, env);
  if (origin && !cors["access-control-allow-origin"]) return json({ error: "Origin not allowed" }, 403);
  if (!env.CUSTOMER_CASES_DB) return json({ error: "Request service is not configured" }, 503, cors);
  if (!env.PUBLIC_INTAKE_RATE_LIMITER) return json({ error: "Request protection is not configured" }, 503, cors);
  const clientKey = request.headers.get("cf-connecting-ip") || "unknown-client";
  const { success } = await env.PUBLIC_INTAKE_RATE_LIMITER.limit({ key: `public-intake:${clientKey}` });
  if (!success) return json({ error: "Too many requests. Try again in 10 seconds." }, 429, { ...cors, "retry-after": "10" });
  const input = normalizeSubmission(await readJson(request)), rawKey = idempotencyKey(request);
  const scopeHash = await hexDigest(`${input.requestType}\n${input.email}`), keyHash = await hexDigest(rawKey), requestFingerprint = await hexDigest(fingerprint(input));
  const prior = await existingIdempotency(env.CUSTOMER_CASES_DB, scopeHash, keyHash);
  if (prior) {
    if (prior.request_fingerprint_sha256 !== requestFingerprint) return json({ error: "Idempotency key conflicts with a different request" }, 409, cors);
    return json({ request_id: prior.request_id, status: "SUBMITTED", created_at: prior.created_at, idempotency_status: "REPLAYED" }, 200, cors);
  }
  await turnstileVerifier(input.turnstileToken, request, env);
  const createdAt = now(), customerId = externalId("SE-CUS"), requestId = externalId("SE-REQ"), eventId = externalId("SE-EVT");
  const configuredTtl = Number(env.IDEMPOTENCY_TTL_SECONDS || IDEMPOTENCY_TTL_SECONDS);
  const ttlSeconds = Number.isFinite(configuredTtl) ? Math.min(Math.max(configuredTtl, 300), 604_800) : IDEMPOTENCY_TTL_SECONDS;
  const receiptId = externalId("SE-CON"), expiresAt = new Date(Date.parse(createdAt) + ttlSeconds * 1000).toISOString();
  const privateContext = [input.currentBelief && `Current belief: ${input.currentBelief}`, input.existingEvidence && `Existing evidence: ${input.existingEvidence}`].filter(Boolean).join("\n\n") || null;
  const customerInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO customers (customer_id, created_at, updated_at, contact_name, email, company) VALUES (?, ?, ?, ?, ?, ?)").bind(customerId, createdAt, createdAt, input.contactName, input.email, input.company);
  const requestInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO requests (request_id, created_at, updated_at, request_type, customer_id, decision, claim_or_question, technical_object, current_dependency, alternative_considered, decision_deadline, case_reference, requested_output, status, privacy_class, human_owner, research_authorization_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', 'CUSTOMER_PRIVATE', NULL, 'NOT_AUTHORIZED')").bind(requestId, createdAt, createdAt, input.requestType, customerId, input.decision, input.claim, input.technicalObject, input.currentDependency, input.alternativeConsidered, input.decisionDeadline, input.caseReference, input.requestedOutput);
  const eventInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_events (event_id, request_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, 'REQUEST_SUBMITTED', ?, 'CUSTOMER', NULL, ?, ?)").bind(eventId, requestId, createdAt, JSON.stringify({ status: "SUBMITTED", privacy_class: "CUSTOMER_PRIVATE", research_authorization_status: "NOT_AUTHORIZED" }), privateContext);
  const consentInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_consent_receipts (receipt_id, request_id, consent_version, consent_accepted, accepted_at, actor) VALUES (?, ?, ?, 1, ?, 'CUSTOMER')").bind(receiptId, requestId, input.consentVersion, createdAt);
  const idempotencyInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_idempotency (scope_sha256, idempotency_key_sha256, request_fingerprint_sha256, request_id, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)").bind(scopeHash, keyHash, requestFingerprint, requestId, createdAt, expiresAt);
  const expiredDelete = env.CUSTOMER_CASES_DB.prepare("DELETE FROM request_idempotency WHERE scope_sha256 = ? AND idempotency_key_sha256 = ? AND expires_at <= ?").bind(scopeHash, keyHash, createdAt);
  try { await env.CUSTOMER_CASES_DB.batch([expiredDelete, customerInsert, requestInsert, eventInsert, consentInsert, idempotencyInsert]); }
  catch (error) {
    const raced = await existingIdempotency(env.CUSTOMER_CASES_DB, scopeHash, keyHash);
    if (raced && raced.request_fingerprint_sha256 === requestFingerprint) return json({ request_id: raced.request_id, status: "SUBMITTED", created_at: raced.created_at, idempotency_status: "REPLAYED" }, 200, cors);
    if (raced) return json({ error: "Idempotency key conflicts with a different request" }, 409, cors);
    throw error;
  }
  return json({ request_id: requestId, status: "SUBMITTED", created_at: createdAt, idempotency_status: "CREATED" }, 201, cors);
}
async function verifyAccess(request, env, audience) {
  if (!env.TEAM_DOMAIN || !audience || !env.ADMIN_EMAILS || [env.TEAM_DOMAIN, audience, env.ADMIN_EMAILS].some((value) => String(value).startsWith("CONFIGURE_"))) throw new Response("Cloudflare Access is not configured", { status: 503 });
  const token = request.headers.get("cf-access-jwt-assertion");
  if (!token) throw new Response("Cloudflare Access authentication required", { status: 403 });
  const issuer = String(env.TEAM_DOMAIN).replace(/\/$/, "");
  const jwks = createRemoteJWKSet(new URL(`${issuer}/cdn-cgi/access/certs`));
  let payload;
  try { ({ payload } = await jwtVerify(token, jwks, { issuer, audience })); } catch { throw new Response("Invalid Cloudflare Access token", { status: 403 }); }
  const email = clean(payload.email, 254)?.toLowerCase();
  const allowlist = new Set(String(env.ADMIN_EMAILS).split(",").map((item) => item.trim().toLowerCase()).filter(Boolean));
  if (!email || !allowlist.has(email)) throw new Response("Administrator access denied", { status: 403 });
  return { email };
}
async function listRequests(url, env) {
  const status = clean(url.searchParams.get("status"), 32);
  if (status && !REQUEST_STATUSES.has(status)) return json({ error: "Invalid status filter" }, 400);
  const limit = Math.min(Math.max(Number(url.searchParams.get("limit") || 50), 1), 100);
  const query = status ? env.CUSTOMER_CASES_DB.prepare("SELECT r.request_id, r.created_at, r.updated_at, r.request_type, r.status, r.privacy_class, r.human_owner, r.research_authorization_status, c.company, c.contact_name, c.email FROM requests r JOIN customers c ON c.customer_id = r.customer_id WHERE r.status = ? ORDER BY r.created_at DESC LIMIT ?").bind(status, limit) : env.CUSTOMER_CASES_DB.prepare("SELECT r.request_id, r.created_at, r.updated_at, r.request_type, r.status, r.privacy_class, r.human_owner, r.research_authorization_status, c.company, c.contact_name, c.email FROM requests r JOIN customers c ON c.customer_id = r.customer_id ORDER BY r.created_at DESC LIMIT ?").bind(limit);
  const result = await query.all();
  return json({ requests: result.results || [] });
}
async function requestDetail(requestId, env) {
  const record = await env.CUSTOMER_CASES_DB.prepare("SELECT r.*, c.contact_name, c.email, c.company FROM requests r JOIN customers c ON c.customer_id = r.customer_id WHERE r.request_id = ?").bind(requestId).first();
  if (!record) return json({ error: "Request not found" }, 404);
  const events = await env.CUSTOMER_CASES_DB.prepare("SELECT event_id, event_type, event_at, actor, previous_state, new_state, note FROM request_events WHERE request_id = ? ORDER BY event_at ASC, event_id ASC").bind(requestId).all();
  const consents = await env.CUSTOMER_CASES_DB.prepare("SELECT receipt_id, consent_version, consent_accepted, accepted_at, actor FROM request_consent_receipts WHERE request_id = ? ORDER BY accepted_at ASC, receipt_id ASC").bind(requestId).all();
  return json({ request: record, events: events.results || [], consent_receipts: consents.results || [] });
}
function eventTypeFor(field, value) {
  if (field === "human_owner") return "OWNER_ASSIGNED";
  if (field === "research_authorization_status") return "RESEARCH_AUTHORIZED";
  return ({ SCOPE_PROPOSED: "SCOPE_PROPOSED", IN_PROGRESS: "RESEARCH_STARTED", DELIVERED: "DELIVERABLE_SENT", CLOSED: "CASE_CLOSED" })[value] || "STATUS_CHANGED";
}
async function patchRequest(request, requestId, env, actor) {
  const current = await env.CUSTOMER_CASES_DB.prepare("SELECT request_id, human_owner, status, research_authorization_status FROM requests WHERE request_id = ?").bind(requestId).first();
  if (!current) return json({ error: "Request not found" }, 404);
  const input = await readJson(request), note = clean(input.note, 4000), updates = [];
  for (const field of ["human_owner", "status", "research_authorization_status"]) {
    if (!(field in input)) continue;
    const value = clean(input[field], field === "human_owner" ? 254 : 32);
    if (field === "status" && !REQUEST_STATUSES.has(value)) return json({ error: "Invalid status" }, 400);
    if (field === "research_authorization_status" && !AUTH_STATUSES.has(value)) return json({ error: "Invalid research authorization" }, 400);
    if (field === "human_owner" && !value) return json({ error: "human_owner cannot be empty" }, 400);
    if (value !== current[field]) updates.push({ field, value, previous: current[field] });
  }
  const allowed = new Set(["human_owner", "status", "research_authorization_status", "note"]);
  if (Object.keys(input).some((key) => !allowed.has(key))) return json({ error: "Unsupported admin field" }, 400);
  if (!updates.length) return json({ error: "No material change" }, 400);
  const updatedAt = now(), assignments = updates.map(({ field }) => `${field} = ?`).join(", ");
  const statements = [env.CUSTOMER_CASES_DB.prepare(`UPDATE requests SET ${assignments}, updated_at = ? WHERE request_id = ?`).bind(...updates.map(({ value }) => value), updatedAt, requestId)];
  for (const change of updates) statements.push(env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_events (event_id, request_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)").bind(externalId("SE-EVT"), requestId, eventTypeFor(change.field, change.value), updatedAt, actor.email, JSON.stringify({ [change.field]: change.previous }), JSON.stringify({ [change.field]: change.value }), note));
  await env.CUSTOMER_CASES_DB.batch(statements);
  return requestDetail(requestId, env);
}
async function appendManualEvent(request, requestId, env, actor) {
  const exists = await env.CUSTOMER_CASES_DB.prepare("SELECT request_id FROM requests WHERE request_id = ?").bind(requestId).first();
  if (!exists) return json({ error: "Request not found" }, 404);
  const input = await readJson(request), eventType = clean(input.event_type, 64), note = clean(input.note, 4000);
  if (!MANUAL_EVENTS.has(eventType) || !note) return json({ error: "Valid event_type and note are required" }, 400);
  const eventAt = now();
  await env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_events (event_id, request_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, ?, ?, ?, NULL, ?, ?)").bind(externalId("SE-EVT"), requestId, eventType, eventAt, actor.email, JSON.stringify({ event_type: eventType }), note).run();
  return json({ event_type: eventType, event_at: eventAt }, 201);
}
async function adminRoute(request, url, env, authVerifier) {
  let actor;
  const audience = url.pathname.startsWith("/api/admin/") ? env.ADMIN_API_AUD : env.ADMIN_UI_AUD;
  try { actor = await authVerifier(request, env, audience); } catch (error) { return error instanceof Response ? error : new Response("Access denied", { status: 403 }); }
  if (url.pathname === "/admin/requests" || url.pathname === "/admin/requests/") return new Response(ADMIN_HTML, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "content-security-policy": "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'", ...securityHeaders } });
  if (url.pathname === "/admin/requests/app.js") return new Response(ADMIN_APP_JS, { headers: { "content-type": "application/javascript; charset=utf-8", "cache-control": "no-store", ...securityHeaders } });
  if (!env.CUSTOMER_CASES_DB) return json({ error: "Database binding missing" }, 503);
  const gapAdminResponse = await handleGapAdminApi(request, url, env, actor);
  if (gapAdminResponse) return gapAdminResponse;
  const match = url.pathname.match(/^\/api\/admin\/requests\/([^/]+)(?:\/(events))?$/);
  if (url.pathname === "/api/admin/requests" && request.method === "GET") return listRequests(url, env);
  if (match && request.method === "GET" && !match[2]) return requestDetail(match[1], env);
  if (match && request.method === "PATCH" && !match[2]) return patchRequest(request, match[1], env, actor);
  if (match && request.method === "POST" && match[2] === "events") return appendManualEvent(request, match[1], env, actor);
  return json({ error: "Admin route not found" }, 404);
}
const safeTurnstileSiteKey = (env) => {
  const key = String(env.TURNSTILE_SITE_KEY || "");
  return /^[A-Za-z0-9_-]{10,100}$/.test(key) && !key.startsWith("CONFIGURE_") ? key : "";
};
function commercialRoute(request, url, env) {
  if (!new Set(["GET", "HEAD"]).has(request.method)) return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD", ...securityHeaders } });
  const path = url.pathname === "/index.html" ? "/" : url.pathname;
  if (path === "/gaps") return Response.redirect(`${url.origin}/gaps/`, 308);
  if (path === "/robots.txt") return new Response(request.method === "HEAD" ? null : robotsTxt, { headers: { "content-type": "text/plain; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/sitemap.xml") return new Response(request.method === "HEAD" ? null : sitemapXml, { headers: { "content-type": "application/xml; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/gaps/") return htmlResponse(request, renderGapIndex());
  if (path === "/gaps/changes/") return htmlResponse(request, renderGapChangeLog());
  const gapMatch = path.match(/^\/gaps\/([^/]+)\/$/);
  if (gapMatch) {
    const gap = findGap(decodeURIComponent(gapMatch[1]));
    return gap ? htmlResponse(request, renderGapDetail(gap)) : new Response("Not found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8", ...securityHeaders } });
  }
  if (path === "/capabilities.json") return new Response(request.method === "HEAD" ? null : JSON.stringify(CAPABILITIES, null, 2) + "\n", { headers: { "content-type": "application/json; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/assets/app.css") return new Response(`${COMMERCIAL_CSS}\n${GAP_CSS}`, { headers: { "content-type": "text/css; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/assets/app.js") return new Response(COMMERCIAL_APP_JS, { headers: { "content-type": "application/javascript; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/assets/gaps.js") return new Response(GAP_APP_JS, { headers: { "content-type": "application/javascript; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  const siteKey = safeTurnstileSiteKey(env);
  const sourceHtml = COMMERCIAL_PAGES[path];
  const localizedHtml = new Set(["/verify/", "/context/", "/decision-pack/"]).has(path)
    ? localizeIntakePage(sourceHtml, url.searchParams.get("lang"))
    : sourceHtml;
  const html = localizedHtml?.replaceAll("__TURNSTILE_SITE_KEY__", siteKey);
  if (!html) return new Response("Not found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8", ...securityHeaders } });
  return htmlResponse(request, html);
}
function htmlResponse(request, html) {
  const turnstile = html.includes("class=\"cf-turnstile\"");
  const csp = turnstile
    ? "default-src 'none'; script-src 'self' https://challenges.cloudflare.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://challenges.cloudflare.com; frame-src https://challenges.cloudflare.com; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
    : "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'";
  return new Response(request.method === "HEAD" ? null : html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300", "content-security-policy": csp, ...securityHeaders } });
}
export function createWorker({ authVerifier = verifyAccess, turnstileVerifier = defaultTurnstileVerifier } = {}) {
  return { async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.hostname === "www.structevidence.com") return Response.redirect(`https://structevidence.com${url.pathname}${url.search}`, 308);
      if (url.pathname === "/api/requests" && request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request, env) });
      if (url.pathname === "/api/requests" && request.method === "POST") return await submitRequest(request, env, turnstileVerifier);
      const gapApiResponse = await handleGapApi(request, url, env);
      if (gapApiResponse) return gapApiResponse;
      if (url.pathname.startsWith("/api/admin/") || url.pathname.startsWith("/admin/requests")) return await adminRoute(request, url, env, authVerifier);
      return commercialRoute(request, url, env);
    } catch (error) {
      if (error instanceof Response) return json({ error: await error.text() }, error.status, url.pathname === "/api/requests" ? corsHeaders(request, env) : {});
      console.error(JSON.stringify({ event: "request_failed", path: url.pathname, error: error instanceof Error ? error.message : "unknown" }));
      return json({ error: "Internal server error" }, 500, url.pathname === "/api/requests" ? corsHeaders(request, env) : {});
    }
  } };
}
export default createWorker();
