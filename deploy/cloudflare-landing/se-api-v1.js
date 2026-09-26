export const API_VERSION = "SE_API_v1";
export const SE_API_V1_OPERATIONS = Object.freeze([
  ["GET", "/"], ["GET", "/subjects"], ["GET", "/subjects/{subject_id}"], ["GET", "/subjects/{subject_id}/state"],
  ["GET", "/subjects/{subject_id}/states"], ["GET", "/subjects/{subject_id}/changes"], ["GET", "/subjects/{subject_id}/evidence"],
  ["GET", "/subjects/{subject_id}/branches"], ["GET", "/changes"], ["GET", "/states/{state_id}"], ["GET", "/changes/{change_id}"],
  ["GET", "/evidence/{evidence_id}"], ["GET", "/branches/{branch_id}"], ["POST", "/requests"], ["GET", "/requests/{request_id}"],
  ["POST", "/challenges"], ["POST", "/outcomes"], ["POST", "/admin/proposals"], ["GET", "/admin/proposals/{proposal_id}"],
  ["POST", "/admin/proposals/{proposal_id}/validate"], ["POST", "/admin/proposals/{proposal_id}/approve"]
]);
export const EMPTY_PUBLIC_DATA = Object.freeze({ subjects: [], states: [], changes: [], evidence: [], branches: [], outcomes: [] });

const MAX_BODY_BYTES = 65_536;
const ID_PATTERNS = {
  subject: /^SE-SUBJ-[0-9]{6}$/,
  state: /^SE-ST-[0-9]{8}-[0-9]{6}$/,
  change: /^SE-CHG-[0-9]{8}-[0-9]{6}$/,
  evidence: /^SE-EV-[0-9]{8}-[0-9]{6}$/,
  branch: /^SE-BR-[0-9]{8}-[0-9]{6}$/,
};
const jsonHeaders = { "content-type": "application/json; charset=utf-8", "x-content-type-options": "nosniff", "cache-control": "no-store" };
const requestId = (request) => request.headers.get("x-request-id") || `SE-HTTP-${crypto.randomUUID()}`;
const envelope = (data, meta = {}, links = {}) => ({ api_version: API_VERSION, data, meta, links });
const respond = (body, status = 200, headers = {}) => new Response(status === 304 ? null : JSON.stringify(body), { status, headers: { ...jsonHeaders, ...headers } });
const fail = (code, message, status, id, headers = {}) => respond({ api_version: API_VERSION, error: { code, message, request_id: id } }, status, headers);
const publicCors = { "access-control-allow-origin": "*", vary: "Origin" };

function allowedOrigin(request, env) {
  const origin = request.headers.get("origin");
  const configured = new Set(String(env.PUBLIC_ORIGINS || "").split(",").map((item) => item.trim()).filter(Boolean));
  return !origin || configured.has(origin) ? origin : null;
}
function submissionCors(request, env) {
  const origin = allowedOrigin(request, env);
  return origin ? { "access-control-allow-origin": origin, "access-control-allow-methods": "POST, OPTIONS", "access-control-allow-headers": "content-type, idempotency-key", vary: "Origin" } : {};
}
function clean(value, max) {
  if (value === null || value === undefined) return null;
  const result = String(value).replace(/[\u0000-\u001F\u007F]/g, "").trim();
  return result ? result.slice(0, max) : null;
}
function exactFields(input, allowed) {
  return input && typeof input === "object" && !Array.isArray(input) && Object.keys(input).every((key) => allowed.has(key));
}
async function readJson(request) {
  const declared = Number(request.headers.get("content-length") || 0);
  if (declared > MAX_BODY_BYTES) throw Object.assign(new Error("Request body too large."), { status: 413, code: "PAYLOAD_TOO_LARGE" });
  if (!String(request.headers.get("content-type") || "").toLowerCase().startsWith("application/json")) throw Object.assign(new Error("Content-Type must be application/json."), { status: 415, code: "UNSUPPORTED_MEDIA_TYPE" });
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > MAX_BODY_BYTES) throw Object.assign(new Error("Request body too large."), { status: 413, code: "PAYLOAD_TOO_LARGE" });
  try { return JSON.parse(text); } catch { throw Object.assign(new Error("Malformed JSON."), { status: 400, code: "MALFORMED_JSON" }); }
}
function parseTime(value, code = "INVALID_TIMESTAMP") {
  if (!value) return null;
  const time = Date.parse(value);
  if (!Number.isFinite(time)) throw Object.assign(new Error("Timestamp must be RFC 3339."), { status: 400, code });
  return time;
}
function sortStates(states) { return [...states].sort((a, b) => a.recorded_at.localeCompare(b.recorded_at) || a.state_id.localeCompare(b.state_id)); }
function currentState(states, asOf = null) {
  const boundary = asOf === null ? Infinity : parseTime(asOf, "INVALID_AS_OF");
  return sortStates(states).filter((item) => Date.parse(item.recorded_at) <= boundary && Date.parse(item.observed_at) <= boundary).at(-1) || null;
}
function etagFor(item) {
  const hash = item?.state_hash || item?.change_hash || item?.content_hash;
  return hash ? `"${hash}"` : null;
}
function immutableResponse(request, body, item, headers = {}) {
  const etag = etagFor(item);
  if (etag && request.headers.get("if-none-match") === etag) return respond(null, 304, { ...headers, etag, "cache-control": "public, max-age=60" });
  return respond(body, 200, { ...headers, ...(etag ? { etag, "cache-control": "public, max-age=60" } : {}) });
}
function publicState(item) {
  return {
    subject_id: item.subject_id, state_id: item.state_id, state_code: item.state_code,
    observed_at: item.observed_at, recorded_at: item.recorded_at, previous_state_id: item.previous_state_id,
    state_changed: item.state_changed, accepted_evidence_count: item.accepted_evidence_ids.length,
    counter_evidence_count: item.counter_evidence_ids.length, unknown_count: item.unknowns.length,
    confidence_boundary: item.confidence_boundary, state_hash: item.state_hash, chain_hash: item.chain_hash,
    links: { history: `/api/v1/subjects/${item.subject_id}/states`, changes: `/api/v1/subjects/${item.subject_id}/changes`, evidence: `/api/v1/subjects/${item.subject_id}/evidence` },
  };
}
function publicEvidence(item) {
  return {
    evidence_id: item.evidence_id, subject_id: item.subject_id, published_at: item.published_at,
    observed_at: item.observed_at, recorded_at: item.recorded_at, effective_at: item.effective_at,
    source: { name: item.source.name, url: item.source.url, type: item.source.type, publisher: item.source.publisher },
    normalized_claim: item.normalized_claim,
    review: { status: item.review.status, reason: item.review.reason }, counter_to: item.counter_to,
    content_hash: item.content_hash,
  };
}
function publicBranch(item) {
  return {
    branch_id: item.branch_id, subject_id: item.subject_id, state_id: item.state_id, status: item.status,
    description: item.description, required_conditions: item.required_conditions,
    strengthening_signals: item.strengthening_signals, weakening_signals: item.weakening_signals,
    kill_conditions: item.kill_conditions, supporting_evidence_ids: item.supporting_evidence_ids,
    contradicting_evidence_ids: item.contradicting_evidence_ids,
  };
}
function publicChange(item, states) {
  const index = new Map(states.map((state) => [state.state_id, state]));
  return {
    change_id: item.change_id, subject_id: item.subject_id, detected_at: item.detected_at,
    previous: { state_id: item.previous_state_id, state_code: index.get(item.previous_state_id)?.state_code || null },
    current: { state_id: item.new_state_id, state_code: index.get(item.new_state_id)?.state_code || null },
    trigger_evidence_ids: item.trigger_evidence_ids, unknowns_resolved: item.unknowns_resolved,
    unknowns_added: item.unknowns_added, materiality: item.materiality, change_summary: item.change_summary,
    change_hash: item.change_hash,
  };
}
function decodeCursor(value) {
  if (!value) return null;
  try { return JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(value.replaceAll("-", "+").replaceAll("_", "/")), (char) => char.charCodeAt(0)))).id; } catch { throw Object.assign(new Error("Invalid cursor."), { status: 400, code: "INVALID_CURSOR" }); }
}
function encodeCursor(id) { return btoa(JSON.stringify({ id })).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", ""); }
function page(items, idField, cursor, limit) {
  const after = decodeCursor(cursor);
  const start = after ? Math.max(items.findIndex((item) => item[idField] === after) + 1, 0) : 0;
  const values = items.slice(start, start + limit);
  return { values, next: start + limit < items.length && values.length ? encodeCursor(values.at(-1)[idField]) : null };
}

export class D1SeApiStore {
  constructor(db) { this.db = db; }
  async replay(scope, key) {
    if (!key) return null;
    const row = await this.db.prepare("SELECT response_json FROM se_api_idempotency WHERE scope = ? AND idempotency_key = ?").bind(scope, key).first();
    return row ? JSON.parse(row.response_json) : null;
  }
  async submit(kind, key, record, response) {
    const replay = await this.replay(kind, key);
    if (replay) return { response: replay, replayed: true };
    const table = ({ request: "se_api_requests", challenge: "se_api_challenges", outcome: "se_api_outcomes" })[kind];
    const id = record[`${kind}_id`];
    const statements = [this.db.prepare(`INSERT INTO ${table} (object_id, created_at, status, payload_json) VALUES (?, ?, ?, ?)`).bind(id, record.created_at, record.status, JSON.stringify(record))];
    if (key) statements.push(this.db.prepare("INSERT INTO se_api_idempotency (scope, idempotency_key, object_id, created_at, response_json) VALUES (?, ?, ?, ?, ?)").bind(kind, key, id, record.created_at, JSON.stringify(response)));
    try {
      await this.db.batch(statements);
    } catch (error) {
      const concurrentReplay = await this.replay(kind, key);
      if (concurrentReplay) return { response: concurrentReplay, replayed: true };
      throw error;
    }
    return { response, replayed: false };
  }
  async getRequest(id) {
    const row = await this.db.prepare("SELECT payload_json FROM se_api_requests WHERE object_id = ?").bind(id).first();
    return row ? JSON.parse(row.payload_json) : null;
  }
  async createProposal(proposal) {
    await this.db.prepare("INSERT INTO se_state_proposals (proposal_id, created_at, status, payload_json) VALUES (?, ?, ?, ?)").bind(proposal.proposal_id, proposal.created_at, proposal.status, JSON.stringify(proposal)).run();
    return proposal;
  }
  async getProposal(id) {
    const row = await this.db.prepare("SELECT payload_json FROM se_state_proposals WHERE proposal_id = ?").bind(id).first();
    return row ? JSON.parse(row.payload_json) : null;
  }
  async updateProposal(proposal) {
    await this.db.prepare("UPDATE se_state_proposals SET status = ?, payload_json = ? WHERE proposal_id = ?").bind(proposal.status, JSON.stringify(proposal), proposal.proposal_id).run();
    return proposal;
  }
}

export class MemorySeApiStore {
  constructor() { this.objects = { request: [], challenge: [], outcome: [] }; this.keys = new Map(); this.proposals = new Map(); }
  async submit(kind, key, record, response) {
    const composite = `${kind}:${key}`;
    if (key && this.keys.has(composite)) return { response: this.keys.get(composite), replayed: true };
    this.objects[kind].push(record);
    if (key) this.keys.set(composite, response);
    return { response, replayed: false };
  }
  async getRequest(id) { return this.objects.request.find((item) => item.request_id === id) || null; }
  async createProposal(proposal) { this.proposals.set(proposal.proposal_id, proposal); return proposal; }
  async getProposal(id) { return this.proposals.get(id) || null; }
  async updateProposal(proposal) { this.proposals.set(proposal.proposal_id, proposal); return proposal; }
}

async function rateLimit(request, env, category) {
  if (!env.PUBLIC_INTAKE_RATE_LIMITER) return true;
  const client = request.headers.get("cf-connecting-ip") || "unknown-client";
  return (await env.PUBLIC_INTAKE_RATE_LIMITER.limit({ key: `${category}:${client}` })).success;
}
function storeFor(env, injected) { return injected || (env.CUSTOMER_CASES_DB ? new D1SeApiStore(env.CUSTOMER_CASES_DB) : null); }
function idempotencyKey(request) {
  const key = request.headers.get("idempotency-key");
  if (!key) return null;
  if (!/^[A-Za-z0-9._:-]{8,128}$/.test(key)) throw Object.assign(new Error("Invalid Idempotency-Key."), { status: 400, code: "INVALID_IDEMPOTENCY_KEY" });
  return key;
}
const objectId = (prefix) => {
  const random = crypto.getRandomValues(new Uint32Array(1))[0] % 1_000_000;
  return `${prefix}-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${String(random).padStart(6, "0")}`;
};

async function submitObject(kind, request, env, store, id) {
  const cors = submissionCors(request, env);
  if (request.headers.get("origin") && !allowedOrigin(request, env)) return fail("ORIGIN_NOT_ALLOWED", "Origin not allowed.", 403, id);
  if (!(await rateLimit(request, env, "PUBLIC_SUBMISSION"))) return fail("RATE_LIMITED", "Too many requests.", 429, id, { ...cors, "retry-after": "10" });
  if (!store) return fail("CUSTOMER_PLANE_UNAVAILABLE", "Protected customer plane is unavailable.", 503, id, cors);
  const input = await readJson(request), createdAt = new Date().toISOString(), key = idempotencyKey(request);
  let record, response;
  if (kind === "request") {
    const allowed = new Set(["subject", "question", "decision_context", "urgency", "requested_output", "public_case_permission"]);
    if (!exactFields(input, allowed)) throw Object.assign(new Error("Unexpected request field."), { status: 400, code: "UNEXPECTED_FIELD" });
    const subject = clean(input.subject, 500), question = clean(input.question, 8000), context = clean(input.decision_context, 8000);
    if (!subject || !question || !context || !["LOW", "NORMAL", "HIGH", "URGENT"].includes(input.urgency) || !["EVIDENCE_CHAIN", "STATE_HISTORY", "CHANGE_REVIEW"].includes(input.requested_output) || typeof input.public_case_permission !== "boolean") throw Object.assign(new Error("Invalid Request submission."), { status: 400, code: "INVALID_REQUEST" });
    const request_id = objectId("SE-REQ");
    record = { request_id, created_at: createdAt, status: "SUBMITTED", visibility: "CUSTOMER_PRIVATE", subject, question, decision_context: context, urgency: input.urgency, requested_output: input.requested_output, public_case_permission: input.public_case_permission };
    response = { request_id, status: "SUBMITTED", created_at: createdAt };
  } else if (kind === "challenge") {
    const allowed = new Set(["state_id", "claim", "evidence_url", "notes"]);
    if (!exactFields(input, allowed) || !ID_PATTERNS.state.test(input.state_id || "") || !clean(input.claim, 8000) || (input.evidence_url && !/^https:\/\//.test(input.evidence_url))) throw Object.assign(new Error("Invalid Challenge submission."), { status: 400, code: "INVALID_CHALLENGE" });
    const challenge_id = objectId("SE-CLG");
    record = { challenge_id, created_at: createdAt, status: "CHALLENGE_SUBMITTED", visibility: "CUSTOMER_PRIVATE", state_id: input.state_id, claim: clean(input.claim, 8000), evidence_url: clean(input.evidence_url, 2000), notes: clean(input.notes, 8000) };
    response = { challenge_id, status: "CHALLENGE_SUBMITTED", created_at: createdAt };
  } else {
    const allowed = new Set(["request_id", "state_id_used", "action", "reported_result", "authorization_for_public_use"]);
    if (!exactFields(input, allowed) || !clean(input.request_id, 100) || !ID_PATTERNS.state.test(input.state_id_used || "") || !clean(input.action, 8000) || !clean(input.reported_result, 8000) || typeof input.authorization_for_public_use !== "boolean") throw Object.assign(new Error("Invalid Outcome submission."), { status: 400, code: "INVALID_OUTCOME" });
    const outcome_id = objectId("SE-OUT");
    record = { outcome_id, created_at: createdAt, status: "OUTCOME_REPORTED", visibility: "CUSTOMER_PRIVATE", request_id: clean(input.request_id, 100), state_id_used: input.state_id_used, action: clean(input.action, 8000), reported_result: clean(input.reported_result, 8000), authorization_for_public_use: input.authorization_for_public_use };
    response = { outcome_id, status: "OUTCOME_REPORTED", created_at: createdAt };
  }
  const result = await store.submit(kind, key, record, response);
  return respond(envelope(result.response, { idempotency_replayed: result.replayed }), result.replayed ? 200 : 201, cors);
}

export async function handleSeApiV1(request, env, { publicData = EMPTY_PUBLIC_DATA, store = null, authorize = null } = {}) {
  const url = new URL(request.url), path = url.pathname, id = requestId(request), method = request.method;
  const db = storeFor(env, store);
  try {
    if (method === "OPTIONS" && ["/api/v1/requests", "/api/v1/challenges", "/api/v1/outcomes"].includes(path)) return new Response(null, { status: 204, headers: submissionCors(request, env) });
    if (method === "GET" && path === "/api/v1") return respond(envelope({ capabilities: { subjects: true, state_history: true, as_of_queries: true, change_feed: true, evidence: true, branches: true, requests: true, challenges: true, outcomes: true }, schema_versions: { state: "SE_STATE_v0.1", evidence: "SE_EVIDENCE_v0.1" } }), 200, publicCors);
    if (method === "GET" && path === "/api/v1/subjects") {
      const items = publicData.subjects.map((subject) => {
        const state = currentState(publicData.states.filter((item) => item.subject_id === subject.subject_id));
        const changed = publicData.changes.filter((item) => item.subject_id === subject.subject_id).sort((a, b) => a.detected_at.localeCompare(b.detected_at)).at(-1);
        return { subject_id: subject.subject_id, canonical_name: subject.canonical_name, subject_type: subject.subject_type, current_state: state ? { state_id: state.state_id, state_code: state.state_code, observed_at: state.observed_at, chain_hash: state.chain_hash } : null, last_changed_at: changed?.detected_at || null, visibility: "PUBLIC" };
      });
      return respond(envelope({ items, next_cursor: null }, { count: items.length }), 200, publicCors);
    }
    if (method === "GET" && path === "/api/v1/changes") {
      let items = [...publicData.changes].sort((a, b) => a.detected_at.localeCompare(b.detected_at) || a.change_id.localeCompare(b.change_id));
      const subject = url.searchParams.get("subject_id"), materiality = url.searchParams.get("materiality"), since = parseTime(url.searchParams.get("since")), until = parseTime(url.searchParams.get("until"));
      if (subject) items = items.filter((item) => item.subject_id === subject);
      if (materiality) items = items.filter((item) => item.materiality === materiality);
      if (since !== null) items = items.filter((item) => Date.parse(item.detected_at) >= since);
      if (until !== null) items = items.filter((item) => Date.parse(item.detected_at) <= until);
      const limit = Math.min(Math.max(Number(url.searchParams.get("limit") || 25), 1), 100), result = page(items, "change_id", url.searchParams.get("cursor"), limit);
      return respond(envelope(result.values.map((item) => publicChange(item, publicData.states)), { next_cursor: result.next, limit }), 200, publicCors);
    }
    const subjectMatch = path.match(/^\/api\/v1\/subjects\/(SE-SUBJ-[0-9]{6})(?:\/(state|states|changes|evidence|branches))?$/);
    if (method === "GET" && subjectMatch) {
      const subject = publicData.subjects.find((item) => item.subject_id === subjectMatch[1]);
      if (!subject) return fail("SUBJECT_NOT_FOUND", "Subject not found.", 404, id, publicCors);
      const resource = subjectMatch[2];
      if (!resource) return respond(envelope({ subject_id: subject.subject_id, canonical_name: subject.canonical_name, subject_type: subject.subject_type, aliases: subject.aliases, industry: subject.industry, geography: subject.geography, description: subject.description, status: subject.status, tags: subject.tags, visibility: "PUBLIC" }), 200, publicCors);
      if (resource === "state") {
        const state = currentState(publicData.states.filter((item) => item.subject_id === subject.subject_id), url.searchParams.get("as_of"));
        if (!state) return fail("STATE_NOT_FOUND_AT_BOUNDARY", "No State existed at the requested boundary.", 404, id, publicCors);
        return immutableResponse(request, envelope(publicState(state), { interpretation: "CURRENT_RECORDED_STATE_NOT_PREDICTION_RECOMMENDATION_OR_GUARANTEE", as_of: url.searchParams.get("as_of") }), state, publicCors);
      }
      if (resource === "states") {
        let values = sortStates(publicData.states.filter((item) => item.subject_id === subject.subject_id));
        if (url.searchParams.get("order") === "desc") values.reverse();
        else if (url.searchParams.get("order") && url.searchParams.get("order") !== "asc") return fail("INVALID_ORDER", "Order must be asc or desc.", 400, id, publicCors);
        return respond(envelope(values.map((item) => ({ state_id: item.state_id, observed_at: item.observed_at, recorded_at: item.recorded_at, state_code: item.state_code, previous_state_id: item.previous_state_id, state_hash: item.state_hash, chain_hash: item.chain_hash })), { order: url.searchParams.get("order") || "asc" }), 200, publicCors);
      }
      if (resource === "changes") return respond(envelope(publicData.changes.filter((item) => item.subject_id === subject.subject_id).map((item) => publicChange(item, publicData.states))), 200, publicCors);
      if (resource === "evidence") return respond(envelope(publicData.evidence.filter((item) => item.subject_id === subject.subject_id).map(publicEvidence)), 200, publicCors);
      if (resource === "branches") return respond(envelope(publicData.branches.filter((item) => item.subject_id === subject.subject_id).map(publicBranch)), 200, publicCors);
    }
    const objectMatch = path.match(/^\/api\/v1\/(states|changes|evidence|branches)\/([^/]+)$/);
    if (method === "GET" && objectMatch) {
      const [kind, rawId] = [objectMatch[1], objectMatch[2]], singular = ({ states: "state", changes: "change", evidence: "evidence", branches: "branch" })[kind];
      if (!ID_PATTERNS[singular].test(rawId)) return fail("INVALID_OBJECT_ID", "Invalid object identifier.", 400, id, publicCors);
      const idField = `${singular}_id`, item = publicData[kind].find((value) => value[idField] === rawId);
      if (!item) return fail(`${singular.toUpperCase()}_NOT_FOUND`, `${singular[0].toUpperCase()}${singular.slice(1)} not found.`, 404, id, publicCors);
      const data = kind === "states" ? publicState(item) : kind === "changes" ? publicChange(item, publicData.states) : kind === "evidence" ? publicEvidence(item) : publicBranch(item);
      return immutableResponse(request, envelope(data), item, publicCors);
    }
    if (method === "POST" && path === "/api/v1/requests") return await submitObject("request", request, env, db, id);
    if (method === "POST" && path === "/api/v1/challenges") return await submitObject("challenge", request, env, db, id);
    if (method === "POST" && path === "/api/v1/outcomes") return await submitObject("outcome", request, env, db, id);
    const requestMatch = path.match(/^\/api\/v1\/requests\/([^/]+)$/);
    if (method === "GET" && requestMatch) {
      if (!authorize) return fail("ACCESS_DENIED", "Protected access required.", 403, id);
      await authorize(request, env, env.ADMIN_API_AUD);
      const item = await db?.getRequest(requestMatch[1]);
      return item ? respond(envelope({ request_id: item.request_id, status: item.status, created_at: item.created_at, visibility: "CUSTOMER_PRIVATE" })) : fail("REQUEST_NOT_FOUND", "Request not found.", 404, id);
    }
    const proposalMatch = path.match(/^\/api\/v1\/admin\/proposals(?:\/([^/]+)(?:\/(validate|approve))?)?$/);
    if (proposalMatch) {
      if (!authorize) return fail("ACCESS_DENIED", "Administrator access required.", 403, id);
      const actor = await authorize(request, env, env.ADMIN_API_AUD);
      if (!db) return fail("CONTROL_PLANE_UNAVAILABLE", "Control plane is unavailable.", 503, id);
      if (method === "POST" && !proposalMatch[1]) {
        const input = await readJson(request), allowed = new Set(["subject_id", "proposed_evidence_ids", "proposed_evidence", "previous_state_id", "previous_state_hash", "proposed_state", "proposed_change_event"]);
        if (!exactFields(input, allowed) || !ID_PATTERNS.subject.test(input.subject_id || "") || !Array.isArray(input.proposed_evidence_ids) || !Array.isArray(input.proposed_evidence) || !/^[a-f0-9]{64}$/.test(input.previous_state_hash || "") || !input.proposed_state || !input.proposed_change_event) throw Object.assign(new Error("Invalid proposal."), { status: 400, code: "INVALID_PROPOSAL" });
        const proposal = { schema_version: "SE_STATE_CHANGE_PROPOSAL_v0.1", proposal_id: objectId("SE-PROP"), subject_id: input.subject_id, created_at: new Date().toISOString(), created_by: actor.email, proposed_evidence_ids: input.proposed_evidence_ids, proposed_evidence: input.proposed_evidence, previous_state_id: input.previous_state_id, previous_state_hash: input.previous_state_hash, proposed_state: input.proposed_state, proposed_change_event: input.proposed_change_event, validation_status: "NOT_RUN", chain_verification_status: "NOT_RUN", review_status: "REVIEW_REQUIRED", materialization_status: "NOT_MATERIALIZED", commit_sha: null, status: "DRAFT" };
        await db.createProposal(proposal); return respond(envelope(proposal), 201);
      }
      const proposal = await db.getProposal(proposalMatch[1]);
      if (!proposal) return fail("PROPOSAL_NOT_FOUND", "Proposal not found.", 404, id);
      if (method === "GET" && !proposalMatch[2]) return respond(envelope(proposal));
      if (method === "POST" && proposalMatch[2] === "validate") {
        proposal.validation_status = proposal.proposed_state.subject_id === proposal.subject_id && proposal.proposed_change_event.subject_id === proposal.subject_id ? "VALIDATED" : "VALIDATION_FAILED";
        proposal.chain_verification_status = "REPOSITORY_VERIFICATION_REQUIRED"; proposal.status = proposal.validation_status === "VALIDATED" ? "REVIEW_REQUIRED" : "VALIDATION_FAILED";
        await db.updateProposal(proposal); return respond(envelope(proposal));
      }
      if (method === "POST" && proposalMatch[2] === "approve") {
        if (proposal.status !== "REVIEW_REQUIRED" || proposal.validation_status !== "VALIDATED") return fail("PROPOSAL_NOT_VALIDATED", "Proposal must be validated before approval.", 409, id);
        proposal.review_status = "APPROVED"; proposal.status = "APPROVED"; await db.updateProposal(proposal); return respond(envelope(proposal));
      }
    }
    if (path.startsWith("/api/v1/")) return fail("ROUTE_NOT_FOUND", "API route not found.", 404, id, method === "GET" ? publicCors : {});
    return null;
  } catch (error) {
    if (error instanceof Response) return fail("ACCESS_DENIED", await error.text(), error.status, id);
    return fail(error.code || "INTERNAL_ERROR", error.status ? error.message : "Internal server error.", error.status || 500, id);
  }
}
