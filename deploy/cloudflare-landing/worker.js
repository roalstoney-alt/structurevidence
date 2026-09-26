import { createRemoteJWKSet, jwtVerify } from "jose";
import { ADMIN_APP_JS, ADMIN_HTML } from "./admin-ui.js";
import { COMMERCIAL_APP_JS_UPGRADE as COMMERCIAL_APP_JS, COMMERCIAL_CSS_V2 as COMMERCIAL_CSS, COMMERCIAL_PAGES_V2 as COMMERCIAL_PAGES } from "./commercial-upgrade.js";
import { EMPTY_PUBLIC_DATA, handleSeApiV1 } from "./se-api-v1.js";

const MAX_BODY_BYTES = 65_536;
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
const now = () => new Date().toISOString();
const externalId = (prefix) => `${prefix}-${crypto.randomUUID().replaceAll("-", "").slice(0, 20).toUpperCase()}`;
const clean = (value, max) => {
  if (value === undefined || value === null) return null;
  const normalized = String(value).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "").trim();
  return normalized ? normalized.slice(0, max) : null;
};
const validEmail = (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value) && value.length <= 254;
const validDate = (value) => !value || /^\d{4}-\d{2}-\d{2}$/.test(value);

function publicOrigins(env) { return new Set(String(env.PUBLIC_ORIGINS || "").split(",").map((item) => item.trim()).filter(Boolean)); }
function corsHeaders(request, env) {
  const origin = request.headers.get("origin");
  return origin && publicOrigins(env).has(origin) ? { "access-control-allow-origin": origin, "access-control-allow-methods": "POST, OPTIONS", "access-control-allow-headers": "content-type", vary: "Origin" } : {};
}
async function readJson(request) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  if (!String(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) throw new Response("Content-Type must be application/json", { status: 415 });
  const body = await request.text();
  if (new TextEncoder().encode(body).byteLength > MAX_BODY_BYTES) throw new Response("Request body too large", { status: 413 });
  try { return JSON.parse(body); } catch { throw new Response("Invalid JSON", { status: 400 }); }
}
function normalizeSubmission(input) {
  const requestType = clean(input.request_type, 16)?.toUpperCase();
  const email = clean(input.email, 254)?.toLowerCase();
  const decision = clean(input.decision, 8000);
  const claim = clean(input.claim_or_question, 8000);
  if (!new Set(["VERIFY", "CONTEXT"]).has(requestType)) throw new Response("Invalid request_type", { status: 400 });
  if (!email || !validEmail(email)) throw new Response("Valid email is required", { status: 400 });
  if (!decision && !claim) throw new Response("Decision or claim/question is required", { status: 400 });
  if (requestType === "VERIFY" && !claim) throw new Response("Verify requests require claim_or_question", { status: 400 });
  if (requestType === "CONTEXT" && !decision) throw new Response("Context requests require decision", { status: 400 });
  const decisionDeadline = clean(input.decision_deadline, 10);
  if (!validDate(decisionDeadline)) throw new Response("Invalid decision_deadline", { status: 400 });
  return { requestType, email, decision, claim, decisionDeadline, contactName: clean(input.contact_name, 200), company: clean(input.company, 300), technicalObject: clean(input.technical_object, 2000), currentDependency: clean(input.current_dependency, 8000), alternativeConsidered: clean(input.alternative_considered, 8000), caseReference: clean(input.case_reference, 300), requestedOutput: clean(input.requested_output, 1000), currentBelief: clean(input.current_belief, 4000), existingEvidence: clean(input.existing_evidence, 8000) };
}
async function submitRequest(request, env) {
  const origin = request.headers.get("origin");
  const cors = corsHeaders(request, env);
  if (origin && !cors["access-control-allow-origin"]) return json({ error: "Origin not allowed" }, 403);
  if (!env.CUSTOMER_CASES_DB) return json({ error: "Request service is not configured" }, 503, cors);
  if (!env.PUBLIC_INTAKE_RATE_LIMITER) return json({ error: "Request protection is not configured" }, 503, cors);
  const clientKey = request.headers.get("cf-connecting-ip") || "unknown-client";
  const { success } = await env.PUBLIC_INTAKE_RATE_LIMITER.limit({ key: `public-intake:${clientKey}` });
  if (!success) return json({ error: "Too many requests. Try again in 10 seconds." }, 429, { ...cors, "retry-after": "10" });
  const input = normalizeSubmission(await readJson(request));
  const createdAt = now(), customerId = externalId("SE-CUS"), requestId = externalId("SE-REQ"), eventId = externalId("SE-EVT");
  const privateContext = [input.currentBelief && `Current belief: ${input.currentBelief}`, input.existingEvidence && `Existing evidence: ${input.existingEvidence}`].filter(Boolean).join("\n\n") || null;
  const customerInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO customers (customer_id, created_at, updated_at, contact_name, email, company) VALUES (?, ?, ?, ?, ?, ?)").bind(customerId, createdAt, createdAt, input.contactName, input.email, input.company);
  const requestInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO requests (request_id, created_at, updated_at, request_type, customer_id, decision, claim_or_question, technical_object, current_dependency, alternative_considered, decision_deadline, case_reference, requested_output, status, privacy_class, human_owner, research_authorization_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'SUBMITTED', 'CUSTOMER_PRIVATE', NULL, 'NOT_AUTHORIZED')").bind(requestId, createdAt, createdAt, input.requestType, customerId, input.decision, input.claim, input.technicalObject, input.currentDependency, input.alternativeConsidered, input.decisionDeadline, input.caseReference, input.requestedOutput);
  const eventInsert = env.CUSTOMER_CASES_DB.prepare("INSERT INTO request_events (event_id, request_id, event_type, event_at, actor, previous_state, new_state, note) VALUES (?, ?, 'REQUEST_SUBMITTED', ?, 'CUSTOMER', NULL, ?, ?)").bind(eventId, requestId, createdAt, JSON.stringify({ status: "SUBMITTED", privacy_class: "CUSTOMER_PRIVATE", research_authorization_status: "NOT_AUTHORIZED" }), privateContext);
  await env.CUSTOMER_CASES_DB.batch([customerInsert, requestInsert, eventInsert]);
  return json({ request_id: requestId, status: "SUBMITTED", created_at: createdAt }, 201, cors);
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
  return json({ request: record, events: events.results || [] });
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
  const match = url.pathname.match(/^\/api\/admin\/requests\/([^/]+)(?:\/(events))?$/);
  if (url.pathname === "/api/admin/requests" && request.method === "GET") return listRequests(url, env);
  if (match && request.method === "GET" && !match[2]) return requestDetail(match[1], env);
  if (match && request.method === "PATCH" && !match[2]) return patchRequest(request, match[1], env, actor);
  if (match && request.method === "POST" && match[2] === "events") return appendManualEvent(request, match[1], env, actor);
  return json({ error: "Admin route not found" }, 404);
}
function commercialRoute(request, url) {
  if (!new Set(["GET", "HEAD"]).has(request.method)) return new Response("Method not allowed", { status: 405, headers: { allow: "GET, HEAD", ...securityHeaders } });
  const path = url.pathname === "/index.html" ? "/" : url.pathname;
  if (path === "/assets/app.css") return new Response(COMMERCIAL_CSS, { headers: { "content-type": "text/css; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  if (path === "/assets/app.js") return new Response(COMMERCIAL_APP_JS, { headers: { "content-type": "application/javascript; charset=utf-8", "cache-control": "public, max-age=3600", ...securityHeaders } });
  const html = COMMERCIAL_PAGES[path];
  if (!html) return new Response("Not found", { status: 404, headers: { "content-type": "text/plain; charset=utf-8", ...securityHeaders } });
  return new Response(request.method === "HEAD" ? null : html, { headers: { "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=300", "content-security-policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'", ...securityHeaders } });
}
export function createWorker({ authVerifier = verifyAccess, sePublicData = EMPTY_PUBLIC_DATA, seApiStore = null } = {}) {
  return { async fetch(request, env) {
    const url = new URL(request.url);
    try {
      if (url.hostname === "www.structevidence.com") return Response.redirect(`https://structevidence.com${url.pathname}${url.search}`, 308);
      if (url.pathname === "/api/v1" || url.pathname.startsWith("/api/v1/")) {
        const apiRequestId = request.headers.get("x-request-id") || `SE-HTTP-${crypto.randomUUID()}`;
        const headers = new Headers(request.headers); headers.set("x-request-id", apiRequestId);
        const apiRequest = new Request(request, { headers });
        const response = await handleSeApiV1(apiRequest, env, { publicData: sePublicData, store: seApiStore, authorize: authVerifier });
        if (response) { response.headers.set("x-request-id", apiRequestId); return response; }
      }
      if (url.pathname === "/api/requests" && request.method === "OPTIONS") return new Response(null, { status: 204, headers: corsHeaders(request, env) });
      if (url.pathname === "/api/requests" && request.method === "POST") return await submitRequest(request, env);
      if (url.pathname.startsWith("/api/admin/") || url.pathname.startsWith("/admin/requests")) return await adminRoute(request, url, env, authVerifier);
      return commercialRoute(request, url);
    } catch (error) {
      if (error instanceof Response) return json({ error: await error.text() }, error.status, url.pathname === "/api/requests" ? corsHeaders(request, env) : {});
      console.error(JSON.stringify({ event: "request_failed", path: url.pathname, error: error instanceof Error ? error.message : "unknown" }));
      return json({ error: "Internal server error" }, 500, url.pathname === "/api/requests" ? corsHeaders(request, env) : {});
    }
  } };
}
export default createWorker();
