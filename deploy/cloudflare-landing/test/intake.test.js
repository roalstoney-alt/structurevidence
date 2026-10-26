import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createWorker } from "../worker.js";

const CONSENT_VERSION = "SE-CUSTOMER-PRIVACY-v1";
const VALID_KEY = "0123456789abcdef0123456789abcdef";

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.args = []; }
  bind(...args) { this.args = args; return this; }
  run() { return this.db.execute(this); }
  first() { return this.db.first(this); }
  all() { return this.db.all(this); }
}

class FakeD1 {
  constructor() {
    this.customers = []; this.requests = []; this.events = []; this.consents = []; this.idempotency = [];
    this.queue = Promise.resolve(); this.failOn = null;
  }
  prepare(sql) { return new Statement(this, sql); }
  snapshot() { return Object.fromEntries(["customers", "requests", "events", "consents", "idempotency"].map((key) => [key, structuredClone(this[key])])); }
  restore(snapshot) { for (const [key, value] of Object.entries(snapshot)) this[key] = value; }
  async batch(statements) {
    const operation = this.queue.then(async () => {
      const snapshot = this.snapshot();
      try {
        for (const statement of statements) await this.execute(statement);
        return statements.map(() => ({ success: true }));
      } catch (error) { this.restore(snapshot); throw error; }
    });
    this.queue = operation.catch(() => {});
    return operation;
  }
  maybeFail(sql) { if (this.failOn && sql.startsWith(this.failOn)) throw new Error("injected D1 failure"); }
  async execute({ sql, args }) {
    this.maybeFail(sql);
    if (sql.startsWith("DELETE FROM request_idempotency")) {
      this.idempotency = this.idempotency.filter((row) => !(row.scope_sha256 === args[0] && row.idempotency_key_sha256 === args[1] && row.expires_at <= args[2]));
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO customers")) {
      this.customers.push(Object.fromEntries(["customer_id", "created_at", "updated_at", "contact_name", "email", "company"].map((key, index) => [key, args[index]])));
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO requests")) {
      this.requests.push({ request_id: args[0], created_at: args[1], updated_at: args[2], request_type: args[3], customer_id: args[4], decision: args[5], claim_or_question: args[6], technical_object: args[7], current_dependency: args[8], alternative_considered: args[9], decision_deadline: args[10], case_reference: args[11], requested_output: args[12], status: "SUBMITTED", privacy_class: "CUSTOMER_PRIVATE", human_owner: null, research_authorization_status: "NOT_AUTHORIZED" });
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO request_events")) {
      const fixedSubmission = sql.includes("'REQUEST_SUBMITTED'");
      this.events.push({ event_id: args[0], request_id: args[1], event_type: fixedSubmission ? "REQUEST_SUBMITTED" : args[2], event_at: fixedSubmission ? args[2] : args[3], actor: fixedSubmission ? "CUSTOMER" : args[4], previous_state: fixedSubmission ? null : args[5], new_state: fixedSubmission ? args[3] : args[6], note: fixedSubmission ? args[4] : args[7] });
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO request_consent_receipts")) {
      if (this.consents.some((row) => row.request_id === args[1] && row.consent_version === args[2])) throw new Error("UNIQUE consent");
      this.consents.push({ receipt_id: args[0], request_id: args[1], consent_version: args[2], consent_accepted: 1, accepted_at: args[3], actor: "CUSTOMER" });
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO request_idempotency")) {
      if (this.idempotency.some((row) => row.scope_sha256 === args[0] && row.idempotency_key_sha256 === args[1])) throw new Error("UNIQUE idempotency");
      if (this.idempotency.some((row) => row.request_id === args[3])) throw new Error("UNIQUE request idempotency");
      this.idempotency.push(Object.fromEntries(["scope_sha256", "idempotency_key_sha256", "request_fingerprint_sha256", "request_id", "created_at", "expires_at"].map((key, index) => [key, args[index]])));
      return { success: true };
    }
    if (sql.startsWith("UPDATE requests SET")) {
      const requestId = args.at(-1), record = this.requests.find((item) => item.request_id === requestId);
      const fields = [...sql.matchAll(/(human_owner|status|research_authorization_status) = \?/g)].map((match) => match[1]);
      fields.forEach((field, index) => { record[field] = args[index]; }); record.updated_at = args.at(-2);
      return { success: true };
    }
    throw new Error(`Unhandled SQL: ${sql}`);
  }
  join(record) {
    const customer = this.customers.find((item) => item.customer_id === record.customer_id);
    return { ...record, ...customer, request_id: record.request_id, created_at: record.created_at, updated_at: record.updated_at };
  }
  async first({ sql, args }) {
    if (sql.startsWith("SELECT request_id, request_fingerprint_sha256")) return this.idempotency.find((row) => row.scope_sha256 === args[0] && row.idempotency_key_sha256 === args[1] && row.expires_at > args[2]) || null;
    if (sql.startsWith("SELECT request_id, human_owner")) {
      const row = this.requests.find((item) => item.request_id === args[0]);
      return row && { request_id: row.request_id, human_owner: row.human_owner, status: row.status, research_authorization_status: row.research_authorization_status };
    }
    if (sql.startsWith("SELECT r.*")) { const row = this.requests.find((item) => item.request_id === args[0]); return row ? this.join(row) : null; }
    if (sql.startsWith("SELECT request_id FROM requests")) return this.requests.find((item) => item.request_id === args[0]) || null;
    throw new Error(`Unhandled first SQL: ${sql}`);
  }
  async all({ sql, args }) {
    if (sql.startsWith("SELECT event_id")) return { results: this.events.filter((item) => item.request_id === args[0]) };
    if (sql.startsWith("SELECT receipt_id")) return { results: this.consents.filter((item) => item.request_id === args[0]) };
    if (sql.startsWith("SELECT r.request_id")) {
      const status = sql.includes("WHERE r.status") ? args[0] : null;
      return { results: this.requests.filter((item) => !status || item.status === status).map((item) => this.join(item)) };
    }
    throw new Error(`Unhandled all SQL: ${sql}`);
  }
}

class FakeRateLimiter {
  constructor(limit = 50) { this.limitValue = limit; this.calls = 0; }
  async limit() { this.calls += 1; return { success: this.calls <= this.limitValue }; }
}

class FakeTurnstile {
  constructor() { this.used = new Set(); this.calls = 0; }
  async verify(token) {
    this.calls += 1;
    if (["invalid-token", "expired-token"].includes(token) || this.used.has(token)) throw new Response("Human verification failed", { status: 400 });
    if (token === "provider-error") throw new Response("Human verification is temporarily unavailable", { status: 503 });
    this.used.add(token); return { success: true, hostname: "structevidence.com", action: "public-intake" };
  }
}

const baseEnv = (db, limiter = new FakeRateLimiter()) => ({ CUSTOMER_CASES_DB: db, PUBLIC_INTAKE_RATE_LIMITER: limiter, PUBLIC_ORIGINS: "https://structevidence.com", TURNSTILE_SITE_KEY: "0xTEST_PUBLIC_SITE_KEY", TEAM_DOMAIN: "https://team.cloudflareaccess.com", ADMIN_UI_AUD: "ui-aud", ADMIN_API_AUD: "api-aud", ADMIN_EMAILS: "admin@example.com" });
const basePayload = (overrides = {}) => ({ request_type: "VERIFY", email: "user@example.com", claim_or_question: "Is the claim supported?", decision: "Supplier selection", consent_accepted: true, consent_version: CONSENT_VERSION, turnstile_token: "token-1", ...overrides });
const publicPost = (body = basePayload(), { origin = "https://structevidence.com", key = VALID_KEY, raw = null } = {}) => new Request("https://structevidence.com/api/requests", { method: "POST", headers: { "content-type": "application/json", origin, "cf-connecting-ip": "192.0.2.8", ...(key ? { "idempotency-key": key } : {}) }, body: raw ?? JSON.stringify(body) });
const testWorker = (turnstile = new FakeTurnstile()) => ({ worker: createWorker({ turnstileVerifier: turnstile.verify.bind(turnstile) }), turnstile });
const adminWorker = (turnstile = new FakeTurnstile()) => createWorker({ authVerifier: async () => ({ email: "admin@example.com" }), turnstileVerifier: turnstile.verify.bind(turnstile) });

test("submission atomically preserves private defaults, append-only event, consent, and hashed idempotency", async () => {
  const db = new FakeD1(), { worker } = testWorker();
  const response = await worker.fetch(publicPost(basePayload({ email: "USER@Example.com", current_belief: "Unverified\n\nDecision timing: This quarter", existing_evidence: "Issuer statement" })), baseEnv(db));
  assert.equal(response.status, 201);
  const result = await response.json();
  assert.match(result.request_id, /^SE-REQ-[A-F0-9]{20}$/); assert.equal(result.idempotency_status, "CREATED");
  assert.deepEqual([db.customers.length, db.requests.length, db.events.length, db.consents.length, db.idempotency.length], [1, 1, 1, 1, 1]);
  assert.equal(db.requests[0].privacy_class, "CUSTOMER_PRIVATE"); assert.equal(db.requests[0].research_authorization_status, "NOT_AUTHORIZED"); assert.equal(db.requests[0].human_owner, null);
  assert.equal(db.events[0].event_type, "REQUEST_SUBMITTED"); assert.equal(db.consents[0].consent_version, CONSENT_VERSION); assert.equal(db.consents[0].consent_accepted, 1);
  assert.match(db.idempotency[0].idempotency_key_sha256, /^[a-f0-9]{64}$/); assert.notEqual(db.idempotency[0].idempotency_key_sha256, VALID_KEY); assert.equal(JSON.stringify(db.idempotency).includes("user@example.com"), false);
});

test("same canonical request and scoped key replays without Turnstile or duplicate writes", async () => {
  const db = new FakeD1(), harness = testWorker(), env = baseEnv(db);
  const first = await harness.worker.fetch(publicPost(), env);
  const second = await harness.worker.fetch(publicPost(basePayload({ turnstile_token: "token-not-used" })), env);
  const firstBody = await first.json(), secondBody = await second.json();
  assert.equal(first.status, 201); assert.equal(second.status, 200); assert.equal(firstBody.request_id, secondBody.request_id); assert.equal(secondBody.idempotency_status, "REPLAYED");
  assert.equal(harness.turnstile.calls, 1); assert.deepEqual([db.customers.length, db.requests.length, db.events.length, db.consents.length], [1, 1, 1, 1]);
});

test("same scoped key with a different payload returns 409 without leaking ID or mutation", async () => {
  const db = new FakeD1(), { worker } = testWorker(), env = baseEnv(db);
  const created = await worker.fetch(publicPost(), env), createdId = (await created.json()).request_id;
  const conflict = await worker.fetch(publicPost(basePayload({ claim_or_question: "Different claim", turnstile_token: "token-2" })), env), body = await conflict.json();
  assert.equal(conflict.status, 409); assert.equal(JSON.stringify(body).includes(createdId), false); assert.equal(db.requests.length, 1);
});

test("raw key is safely scoped so different email can use the same key", async () => {
  const db = new FakeD1(), { worker } = testWorker(), env = baseEnv(db);
  assert.equal((await worker.fetch(publicPost(), env)).status, 201);
  assert.equal((await worker.fetch(publicPost(basePayload({ email: "other@example.com", turnstile_token: "token-2" })), env)).status, 201);
  assert.equal(db.requests.length, 2); assert.equal(db.idempotency.length, 2);
});

test("concurrent identical requests converge through the durable unique constraint", async () => {
  const db = new FakeD1(), harness = testWorker(), env = baseEnv(db);
  const [left, right] = await Promise.all([
    harness.worker.fetch(publicPost(basePayload({ turnstile_token: "parallel-a" })), env),
    harness.worker.fetch(publicPost(basePayload({ turnstile_token: "parallel-b" })), env)
  ]);
  assert.deepEqual([left.status, right.status].sort(), [200, 201]);
  const ids = [(await left.json()).request_id, (await right.json()).request_id]; assert.equal(ids[0], ids[1]);
  assert.deepEqual([db.customers.length, db.requests.length, db.events.length, db.consents.length, db.idempotency.length], [1, 1, 1, 1, 1]);
});

test("expired mapping can be replaced without deleting historical request, event, or consent", async () => {
  const db = new FakeD1(), { worker } = testWorker(), env = baseEnv(db);
  const first = await worker.fetch(publicPost(), env), firstId = (await first.json()).request_id;
  db.idempotency[0].expires_at = "2000-01-01T00:00:00.000Z";
  const second = await worker.fetch(publicPost(basePayload({ claim_or_question: "New request after retention", turnstile_token: "token-2" })), env), secondId = (await second.json()).request_id;
  assert.equal(second.status, 201); assert.notEqual(firstId, secondId); assert.equal(db.idempotency.length, 1);
  assert.deepEqual([db.requests.length, db.events.length, db.consents.length], [2, 2, 2]);
});

test("server rejects missing/false/version-mismatched consent before any write", async () => {
  for (const override of [{ consent_accepted: false }, { consent_accepted: null }, { consent_version: "old-version" }]) {
    const db = new FakeD1(), { worker, turnstile } = testWorker();
    const response = await worker.fetch(publicPost(basePayload(override)), baseEnv(db));
    assert.equal(response.status, 400); assert.equal(turnstile.calls, 0); assert.equal(db.requests.length, 0);
  }
});

test("Turnstile missing, invalid, expired, replayed, and provider failure fail closed", async () => {
  const db = new FakeD1(), harness = testWorker(), env = baseEnv(db);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ turnstile_token: null })), env)).status, 400);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ turnstile_token: "invalid-token" }), { key: "11111111111111111111" }), env)).status, 400);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ turnstile_token: "expired-token" }), { key: "22222222222222222222" }), env)).status, 400);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ turnstile_token: "single-use" }), { key: "33333333333333333333" }), env)).status, 201);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ email: "other@example.com", turnstile_token: "single-use" }), { key: "44444444444444444444" }), env)).status, 400);
  assert.equal((await harness.worker.fetch(publicPost(basePayload({ turnstile_token: "provider-error" }), { key: "55555555555555555555" }), env)).status, 503);
  assert.equal(db.requests.length, 1);
});

test("default Turnstile verifier calls Siteverify and validates hostname/action before D1", async () => {
  const originalFetch = globalThis.fetch;
  try {
    let siteverifyCalls = 0;
    globalThis.fetch = async (url, options) => {
      siteverifyCalls += 1;
      assert.equal(url, "https://challenges.cloudflare.com/turnstile/v0/siteverify"); assert.equal(options.method, "POST");
      assert.equal(options.body.get("secret"), "local-test-secret"); assert.equal(options.body.get("response"), "siteverify-success"); assert.equal(options.body.get("remoteip"), "192.0.2.8");
      return new Response(JSON.stringify({ success: true, hostname: "structevidence.com", action: "public-intake" }), { headers: { "content-type": "application/json" } });
    };
    const db = new FakeD1(), env = { ...baseEnv(db), TURNSTILE_SECRET_KEY: "local-test-secret" };
    const accepted = await createWorker().fetch(publicPost(basePayload({ turnstile_token: "siteverify-success" })), env);
    assert.equal(accepted.status, 201); assert.equal(siteverifyCalls, 1); assert.equal(db.requests.length, 1);

    globalThis.fetch = async () => new Response(JSON.stringify({ success: true, hostname: "attacker.example", action: "public-intake" }), { headers: { "content-type": "application/json" } });
    const rejectedDb = new FakeD1(), rejectedEnv = { ...baseEnv(rejectedDb), TURNSTILE_SECRET_KEY: "local-test-secret" };
    assert.equal((await createWorker().fetch(publicPost(basePayload({ turnstile_token: "wrong-host" }), { key: "77777777777777777777" }), rejectedEnv)).status, 400); assert.equal(rejectedDb.requests.length, 0);

    globalThis.fetch = async () => new Response(JSON.stringify({ success: true, hostname: "structevidence.com", action: "wrong-action" }), { headers: { "content-type": "application/json" } });
    const actionDb = new FakeD1(), actionEnv = { ...baseEnv(actionDb), TURNSTILE_SECRET_KEY: "local-test-secret" };
    assert.equal((await createWorker().fetch(publicPost(basePayload({ turnstile_token: "wrong-action" }), { key: "79797979797979797979" }), actionEnv)).status, 400); assert.equal(actionDb.requests.length, 0);

    globalThis.fetch = async () => { throw new Error("provider unavailable"); };
    const failedDb = new FakeD1(), failedEnv = { ...baseEnv(failedDb), TURNSTILE_SECRET_KEY: "local-test-secret" };
    assert.equal((await createWorker().fetch(publicPost(basePayload({ turnstile_token: "provider-down" }), { key: "88888888888888888888" }), failedEnv)).status, 503); assert.equal(failedDb.requests.length, 0);

    globalThis.fetch = async (_url, { signal }) => new Promise((_resolve, reject) => signal.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")), { once: true }));
    const timeoutDb = new FakeD1(), timeoutEnv = { ...baseEnv(timeoutDb), TURNSTILE_SECRET_KEY: "local-test-secret", TURNSTILE_TIMEOUT_MS: "10" };
    assert.equal((await createWorker().fetch(publicPost(basePayload({ turnstile_token: "provider-timeout" }), { key: "89898989898989898989" }), timeoutEnv)).status, 503); assert.equal(timeoutDb.requests.length, 0);
  } finally { globalThis.fetch = originalFetch; }
});

test("strict input rejects unknown fields, wrong types, duplicate keys, invalid keys, malformed and oversized bodies", async () => {
  const cases = [
    publicPost(basePayload({ status: "AUTHORIZED" })), publicPost(basePayload({ email: ["user@example.com"] })), publicPost(basePayload(), { key: "short" }),
    publicPost(null, { raw: '{"request_type":"VERIFY","request_type":"CONTEXT"}' }), publicPost(null, { raw: "{" }), publicPost(basePayload({ claim_or_question: "x".repeat(8001) })), publicPost(basePayload({ decision_deadline: "2026-02-31" }))
  ];
  for (const request of cases) {
    const db = new FakeD1(), { worker } = testWorker();
    const response = await worker.fetch(request, baseEnv(db)); assert.ok([400, 413].includes(response.status)); assert.equal(db.requests.length, 0);
  }
  const db = new FakeD1(), { worker } = testWorker();
  const oversized = publicPost(null, { raw: JSON.stringify(basePayload({ claim_or_question: "x".repeat(66_000) })) });
  assert.equal((await worker.fetch(oversized, baseEnv(db))).status, 413);
});

test("bound values preserve SQL-like text without changing schema or authorization defaults", async () => {
  const db = new FakeD1(), { worker } = testWorker(), text = "x'); DROP TABLE requests; --";
  assert.equal((await worker.fetch(publicPost(basePayload({ claim_or_question: text })), baseEnv(db))).status, 201);
  assert.equal(db.requests[0].claim_or_question, text); assert.equal(db.requests[0].research_authorization_status, "NOT_AUTHORIZED");
});

test("origin, CORS preflight, non-browser compatibility, and rate limiter are bounded", async () => {
  const db = new FakeD1(), limiter = new FakeRateLimiter(2), { worker } = testWorker(), env = baseEnv(db, limiter);
  assert.equal((await worker.fetch(publicPost(basePayload(), { origin: "https://structurevidence.org" }), env)).status, 403);
  const missingOrigin = publicPost(basePayload({ turnstile_token: "no-origin" })); missingOrigin.headers.delete("origin");
  const nonBrowser = await worker.fetch(missingOrigin, env); assert.equal(nonBrowser.status, 201); assert.equal(nonBrowser.headers.get("access-control-allow-origin"), null);
  const preflight = await worker.fetch(new Request("https://structevidence.com/api/requests", { method: "OPTIONS", headers: { origin: "https://structevidence.com" } }), env);
  assert.equal(preflight.status, 204); assert.match(preflight.headers.get("access-control-allow-headers"), /idempotency-key/);
  assert.equal((await worker.fetch(publicPost(basePayload({ email: "second@example.com", turnstile_token: "token-2" }), { key: "66666666666666666666" }), env)).status, 201);
  const limited = await worker.fetch(publicPost(basePayload({ turnstile_token: "token-3" }), { key: "99999999999999999999" }), env);
  assert.equal(limited.status, 429); assert.equal(limited.headers.get("retry-after"), "10");
});

test("D1 batch failure rolls back every intake record", async () => {
  const db = new FakeD1(), { worker } = testWorker(); db.failOn = "INSERT INTO request_consent_receipts";
  const response = await worker.fetch(publicPost(), baseEnv(db)); assert.equal(response.status, 500);
  assert.deepEqual([db.customers.length, db.requests.length, db.events.length, db.consents.length, db.idempotency.length], [0, 0, 0, 0, 0]);
});

test("admin read-after-write returns consent audit while anonymous GET leaks nothing", async () => {
  const db = new FakeD1(), worker = adminWorker(), env = baseEnv(db);
  const created = await worker.fetch(publicPost(basePayload({ request_type: "CONTEXT", decision: "Choose architecture", claim_or_question: null })), env);
  const id = (await created.json()).request_id;
  const anonymous = await createWorker().fetch(new Request(`https://structevidence.com/api/admin/requests/${id}`), env); assert.equal(anonymous.status, 403);
  const detail = await worker.fetch(new Request(`https://structevidence.com/api/admin/requests/${id}`), env), body = await detail.json();
  assert.equal(body.request.request_id, id); assert.equal(body.events.length, 1); assert.equal(body.consent_receipts.length, 1); assert.equal(body.consent_receipts[0].consent_version, CONSENT_VERSION);
  const list = await worker.fetch(new Request("https://structevidence.com/api/admin/requests"), env); assert.equal((await list.json()).requests.length, 1);
});

test("admin material changes retain independent Access audiences and append events", async () => {
  const audiences = [], db = new FakeD1(), turnstile = new FakeTurnstile();
  const worker = createWorker({ authVerifier: async (_request, _env, audience) => { audiences.push(audience); return { email: "admin@example.com" }; }, turnstileVerifier: turnstile.verify.bind(turnstile) });
  const env = baseEnv(db), created = await worker.fetch(publicPost(), env), id = (await created.json()).request_id;
  await worker.fetch(new Request("https://structevidence.com/admin/requests/"), env);
  const patchResponse = await worker.fetch(new Request(`https://structevidence.com/api/admin/requests/${id}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ status: "UNDER_REVIEW", human_owner: "admin@example.com", research_authorization_status: "L1_VERIFY_AUTHORIZED", note: "Human review" }) }), env);
  assert.equal(patchResponse.status, 200); assert.deepEqual(audiences, ["ui-aud", "api-aud"]);
  assert.deepEqual(db.events.map((event) => event.event_type), ["REQUEST_SUBMITTED", "OWNER_ASSIGNED", "STATUS_CHANGED", "RESEARCH_AUTHORIZED"]);
});

test("migration is additive, durable, append-only, and documents rollback boundary", () => {
  const original = readFileSync(new URL("../migrations/0001_customer_intake.sql", import.meta.url), "utf8");
  const hardening = readFileSync(new URL("../migrations/0003_intake_hardening.sql", import.meta.url), "utf8");
  const rollback = readFileSync(new URL("../migrations/0003_intake_hardening_ROLLBACK.md", import.meta.url), "utf8");
  assert.match(original, /request_events_no_update/); assert.match(original, /request_events_no_delete/);
  assert.match(hardening, /PRIMARY KEY \(scope_sha256, idempotency_key_sha256\)/); assert.match(hardening, /UNIQUE \(request_id\)/);
  assert.match(hardening, /request_consent_receipts_no_update/); assert.match(hardening, /request_consent_receipts_no_delete/);
  assert.doesNotMatch(hardening, /\b(?:DROP|ALTER)\b/i); assert.match(rollback, /not.*authorized rollback/is);
});

test("commercial forms ship consent, Turnstile, stable idempotency, graceful errors, and no secret", async () => {
  const { worker } = testWorker(), env = baseEnv(new FakeD1());
  for (const path of ["/", "/verify/", "/context/", "/decision-pack/"]) assert.equal((await worker.fetch(new Request(`https://structevidence.com${path}`), env)).status, 200);
  const verify = await (await worker.fetch(new Request("https://structevidence.com/verify/"), env)).text();
  const context = await (await worker.fetch(new Request("https://structevidence.com/context/"), env)).text();
  const app = await (await worker.fetch(new Request("https://structevidence.com/assets/app.js"), env)).text();
  assert.match(verify, /name="consent_accepted"[^>]*required/); assert.match(context, /name="consent_accepted"[^>]*required/);
  assert.match(verify, /class="cf-turnstile"/); assert.match(verify, /data-sitekey="0xTEST_PUBLIC_SITE_KEY"/); assert.match(verify, /data-action="public-intake"/);
  assert.match(app, /SE-CUSTOMER-PRIVACY-v1/); assert.match(app, /"idempotency-key"/); assert.match(app, /crypto\.randomUUID/); assert.match(app, /Human verification is unavailable/); assert.match(app, /Use email fallback/);
  assert.doesNotMatch(verify + app, /TURNSTILE_SECRET_KEY|secret.*siteverify/i);
  const unconfigured = await (await worker.fetch(new Request("https://structevidence.com/verify/"), { ...env, TURNSTILE_SITE_KEY: "CONFIGURE_TURNSTILE_SITE_KEY" })).text();
  assert.match(unconfigured, /data-sitekey=""/);
});

test("commercial language routes, public research links, prices, and redirects remain unchanged", async () => {
  const { worker } = testWorker(), env = baseEnv(new FakeD1());
  for (const path of ["/en/", "/zh-cn/", "/es/", "/pricing/"]) assert.equal((await worker.fetch(new Request(`https://structevidence.com${path}`), env)).status, 200);
  const home = await (await worker.fetch(new Request("https://structevidence.com/"), env)).text();
  const pricing = await (await worker.fetch(new Request("https://structevidence.com/pricing/"), env)).text();
  assert.match(home, /https:\/\/structurevidence\.org\/cases\/800vdc\//); assert.match(pricing, /USD 199/); assert.match(pricing, /USD 1,999/); assert.match(pricing, /USD 4,999/);
  const redirect = await worker.fetch(new Request("https://www.structevidence.com/context/?intent=DECISION_PACK"), env);
  assert.equal(redirect.status, 308); assert.equal(redirect.headers.get("location"), "https://structevidence.com/context/?intent=DECISION_PACK");
});
