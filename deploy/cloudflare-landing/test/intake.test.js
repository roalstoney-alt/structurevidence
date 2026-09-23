import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createWorker } from "../worker.js";

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.args = []; }
  bind(...args) { this.args = args; return this; }
  run() { return this.db.execute(this); }
  first() { return this.db.first(this); }
  all() { return this.db.all(this); }
}

class FakeD1 {
  constructor() { this.customers = []; this.requests = []; this.events = []; }
  prepare(sql) { return new Statement(this, sql); }
  async batch(statements) { for (const statement of statements) await this.execute(statement); return statements.map(() => ({ success: true })); }
  async execute({ sql, args }) {
    if (sql.startsWith("INSERT INTO customers")) { this.customers.push(Object.fromEntries(["customer_id","created_at","updated_at","contact_name","email","company"].map((key, i) => [key, args[i]]))); return { success: true }; }
    if (sql.startsWith("INSERT INTO requests")) { this.requests.push({ request_id: args[0], created_at: args[1], updated_at: args[2], request_type: args[3], customer_id: args[4], decision: args[5], claim_or_question: args[6], technical_object: args[7], current_dependency: args[8], alternative_considered: args[9], decision_deadline: args[10], case_reference: args[11], requested_output: args[12], status: "SUBMITTED", privacy_class: "CUSTOMER_PRIVATE", human_owner: null, research_authorization_status: "NOT_AUTHORIZED" }); return { success: true }; }
    if (sql.startsWith("INSERT INTO request_events")) { const fixedSubmission = sql.includes("'REQUEST_SUBMITTED'"); this.events.push({ event_id: args[0], request_id: args[1], event_type: fixedSubmission ? "REQUEST_SUBMITTED" : args[2], event_at: fixedSubmission ? args[2] : args[3], actor: fixedSubmission ? "CUSTOMER" : args[4], previous_state: fixedSubmission ? null : args[5], new_state: fixedSubmission ? args[3] : args[6], note: fixedSubmission ? args[4] : args[7] }); return { success: true }; }
    if (sql.startsWith("UPDATE requests SET")) { const requestId = args.at(-1), record = this.requests.find((item) => item.request_id === requestId); const fields = [...sql.matchAll(/(human_owner|status|research_authorization_status) = \?/g)].map((match) => match[1]); fields.forEach((field, i) => { record[field] = args[i]; }); record.updated_at = args.at(-2); return { success: true }; }
    throw new Error(`Unhandled SQL: ${sql}`);
  }
  join(record) { const customer = this.customers.find((item) => item.customer_id === record.customer_id); return { ...record, ...customer, request_id: record.request_id, created_at: record.created_at, updated_at: record.updated_at }; }
  async first({ sql, args }) {
    if (sql.startsWith("SELECT request_id, human_owner")) { const row = this.requests.find((item) => item.request_id === args[0]); return row && { request_id: row.request_id, human_owner: row.human_owner, status: row.status, research_authorization_status: row.research_authorization_status }; }
    if (sql.startsWith("SELECT r.*")) { const row = this.requests.find((item) => item.request_id === args[0]); return row ? this.join(row) : null; }
    if (sql.startsWith("SELECT request_id FROM requests")) return this.requests.find((item) => item.request_id === args[0]) || null;
    throw new Error(`Unhandled first SQL: ${sql}`);
  }
  async all({ sql, args }) {
    if (sql.startsWith("SELECT event_id")) return { results: this.events.filter((item) => item.request_id === args[0]) };
    if (sql.startsWith("SELECT r.request_id")) { const status = sql.includes("WHERE r.status") ? args[0] : null; return { results: this.requests.filter((item) => !status || item.status === status).map((item) => this.join(item)) }; }
    throw new Error(`Unhandled all SQL: ${sql}`);
  }
}

class FakeRateLimiter {
  constructor(limit = 5) { this.limitValue = limit; this.calls = 0; }
  async limit() { this.calls += 1; return { success: this.calls <= this.limitValue }; }
}

const baseEnv = (db, limiter = new FakeRateLimiter()) => ({ CUSTOMER_CASES_DB: db, PUBLIC_INTAKE_RATE_LIMITER: limiter, PUBLIC_ORIGINS: "https://structevidence.com", TEAM_DOMAIN: "https://team.cloudflareaccess.com", ADMIN_UI_AUD: "ui-aud", ADMIN_API_AUD: "api-aud", ADMIN_EMAILS: "admin@example.com" });
const publicPost = (body, origin = "https://structevidence.com") => new Request("https://structevidence.com/api/requests", { method: "POST", headers: { "content-type": "application/json", origin, "cf-connecting-ip": "192.0.2.8" }, body: JSON.stringify(body) });
const adminWorker = createWorker({ authVerifier: async () => ({ email: "admin@example.com" }) });

test("customer submission persists unique defaults and append-only submission event", async () => {
  const db = new FakeD1(), worker = createWorker();
  const payload = { request_type: "VERIFY", email: "USER@Example.com", claim_or_question: "Is the claim supported?", decision: "Supplier selection", status: "AUTHORIZED", human_owner: "attacker", research_authorization_status: "L3_DEEP_AUTHORIZED" };
  const first = await worker.fetch(publicPost(payload), baseEnv(db));
  const second = await worker.fetch(publicPost(payload), baseEnv(db));
  assert.equal(first.status, 201); assert.equal(second.status, 201);
  const firstBody = await first.json(), secondBody = await second.json();
  assert.match(firstBody.request_id, /^SE-REQ-[A-F0-9]{20}$/); assert.notEqual(firstBody.request_id, secondBody.request_id);
  assert.equal(db.requests[0].status, "SUBMITTED"); assert.equal(db.requests[0].privacy_class, "CUSTOMER_PRIVATE"); assert.equal(db.requests[0].research_authorization_status, "NOT_AUTHORIZED"); assert.equal(db.requests[0].human_owner, null);
  assert.equal(db.events[0].event_type, "REQUEST_SUBMITTED"); assert.equal(db.events[0].actor, "CUSTOMER");
});

test("invalid public requests are rejected", async () => {
  const db = new FakeD1(), worker = createWorker();
  const response = await worker.fetch(publicPost({ request_type: "VERIFY", email: "bad", claim_or_question: "x" }), baseEnv(db));
  assert.equal(response.status, 400); assert.equal(db.requests.length, 0);
});

test("public intake rejects the research origin and rate limits by client", async () => {
  const db = new FakeD1(), limiter = new FakeRateLimiter(1), worker = createWorker(), env = baseEnv(db, limiter);
  const payload = { request_type: "VERIFY", email: "user@example.com", claim_or_question: "A claim" };
  assert.equal((await worker.fetch(publicPost(payload, "https://structurevidence.org"), env)).status, 403);
  assert.equal((await worker.fetch(publicPost(payload), env)).status, 201);
  const limited = await worker.fetch(publicPost(payload), env);
  assert.equal(limited.status, 429); assert.equal(limited.headers.get("retry-after"), "10");
});

test("admin APIs are inaccessible without Access configuration or JWT", async () => {
  const worker = createWorker(), db = new FakeD1();
  const response = await worker.fetch(new Request("https://structevidence.com/api/admin/requests"), baseEnv(db));
  assert.equal(response.status, 403);
});

test("admin list/detail and material changes append events", async () => {
  const db = new FakeD1(), env = baseEnv(db);
  const created = await adminWorker.fetch(publicPost({ request_type: "CONTEXT", email: "user@example.com", decision: "Choose architecture" }), env);
  const id = (await created.json()).request_id;
  const list = await adminWorker.fetch(new Request("https://structevidence.com/api/admin/requests"), env); assert.equal((await list.json()).requests.length, 1);
  const detail = await adminWorker.fetch(new Request(`https://structevidence.com/api/admin/requests/${id}`), env); assert.equal((await detail.json()).request.request_id, id);
  const patch = await adminWorker.fetch(new Request(`https://structevidence.com/api/admin/requests/${id}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ status: "UNDER_REVIEW", human_owner: "admin@example.com", research_authorization_status: "L1_VERIFY_AUTHORIZED", note: "Human review" }) }), env);
  assert.equal(patch.status, 200);
  assert.deepEqual(db.events.map((event) => event.event_type), ["REQUEST_SUBMITTED", "OWNER_ASSIGNED", "STATUS_CHANGED", "RESEARCH_AUTHORIZED"]);
  assert.equal(db.events.length, 4);
});

test("admin routes select independent Access audiences", async () => {
  const audiences = [], db = new FakeD1();
  const worker = createWorker({ authVerifier: async (_request, _env, audience) => { audiences.push(audience); return { email: "admin@example.com" }; } });
  await worker.fetch(new Request("https://structevidence.com/admin/requests/"), baseEnv(db));
  await worker.fetch(new Request("https://structevidence.com/api/admin/requests"), baseEnv(db));
  assert.deepEqual(audiences, ["ui-aud", "api-aud"]);
});

test("migration enforces append-only events and no file table", () => {
  const sql = readFileSync(new URL("../migrations/0001_customer_intake.sql", import.meta.url), "utf8");
  assert.match(sql, /request_events_no_update/); assert.match(sql, /request_events_no_delete/); assert.doesNotMatch(sql, /CREATE TABLE request_files/i);
});

test("commercial pages are direct, concise, and connect forms same-origin", async () => {
  const worker = createWorker(), env = baseEnv(new FakeD1());
  for (const path of ["/", "/verify/", "/context/", "/decision-pack/"]) assert.equal((await worker.fetch(new Request(`https://structevidence.com${path}`), env)).status, 200);
  const home = await (await worker.fetch(new Request("https://structevidence.com/"), env)).text();
  assert.match(home, /From question to defensible decision/); assert.match(home, /href="\/verify\/"/); assert.match(home, /href="\/context\/"/); assert.match(home, /https:\/\/structurevidence\.org\/cases\/800vdc\//);
  assert.doesNotMatch(home, /\b(?:CML|RDL|RTP|ECN)\b/); assert.doesNotMatch(home, /Evidence Archive|internal research credits/i);
  const verify = await (await worker.fetch(new Request("https://structevidence.com/verify/"), env)).text();
  const context = await (await worker.fetch(new Request("https://structevidence.com/context/"), env)).text();
  const app = await (await worker.fetch(new Request("https://structevidence.com/assets/app.js"), env)).text();
  assert.match(app, /fetch\('\/api\/requests'/); assert.match(app, /Request received/); assert.match(app, /Use email fallback/);
  assert.match(verify, /data-request-type="VERIFY"/); assert.match(context, /data-request-type="CONTEXT"/);
  assert.match(verify, /name="email"[^>]*required/); assert.match(context, /name="email"[^>]*required/);
  const redirect = await worker.fetch(new Request("https://www.structevidence.com/context/?intent=DECISION_PACK"), env);
  assert.equal(redirect.status, 308); assert.equal(redirect.headers.get("location"), "https://structevidence.com/context/?intent=DECISION_PACK");
});
