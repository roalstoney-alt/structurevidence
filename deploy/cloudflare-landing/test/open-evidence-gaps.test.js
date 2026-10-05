import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { OPEN_EVIDENCE_GAPS, GAP_SUBMISSION_STATES } from "../gaps.js";
import { createWorker } from "../worker.js";

class Statement {
  constructor(db, sql) { this.db = db; this.sql = sql; this.args = []; }
  bind(...args) { this.args = args; return this; }
  run() { return this.db.execute(this); }
  first() { return this.db.first(this); }
  all() { return this.db.all(this); }
}

class FakeGapD1 {
  constructor() { this.challenges = []; this.events = []; this.publicChanges = []; }
  prepare(sql) { return new Statement(this, sql); }
  async batch(statements) { for (const statement of statements) await this.execute(statement); return statements.map(() => ({ success: true })); }
  async execute({ sql, args }) {
    if (sql.startsWith("INSERT INTO gap_challenges")) {
      if (this.challenges.filter((item) => item.client_key_hash === args[9]).length >= 5) throw new Error("gap_challenge_rate_limited");
      this.challenges.push({ challenge_id: args[0], gap_id: args[1], evidence_reference: args[2], effect: args[3], note: args[4], attribution_preference: args[5], attribution_name: args[6], organization_name: args[7], contact_email: args[8], state: "SUBMITTED", client_key_hash: args[9], created_at: args[10], updated_at: args[11] });
      return { success: true };
    }
    if (sql.startsWith("INSERT INTO gap_challenge_events")) {
      const fixedSubmission = sql.includes("'SUBMITTED'");
      this.events.push(fixedSubmission
        ? { event_id: args[0], challenge_id: args[1], event_type: "SUBMITTED", event_at: args[2], actor: "PUBLIC_CONTRIBUTOR", previous_state: null, new_state: "SUBMITTED", note: args[3] }
        : { event_id: args[0], challenge_id: args[1], event_type: args[2], event_at: args[3], actor: args[4], previous_state: args[5], new_state: args[6], note: args[7] });
      return { success: true };
    }
    if (sql.startsWith("UPDATE gap_challenges SET state")) {
      const item = this.challenges.find((row) => row.challenge_id === args[2]);
      item.state = args[0]; item.updated_at = args[1]; return { success: true };
    }
    if (sql.startsWith("INSERT INTO gap_public_changes")) {
      this.publicChanges.push({ change_id: args[0], gap_id: args[1], challenge_id: args[2], change_type: args[3], summary: args[4], attribution: args[5], previous_state: args[6], new_state: args[7], changed_at: args[8], reviewer: args[9], append_only: 1 });
      return { success: true };
    }
    throw new Error(`Unhandled SQL: ${sql}`);
  }
  async first({ sql, args }) {
    if (sql.startsWith("SELECT challenge_id, gap_id, state, attribution_preference")) return this.challenges.find((item) => item.challenge_id === args[0]) || null;
    if (sql.startsWith("SELECT challenge_id, gap_id, state")) return this.challenges.find((item) => item.challenge_id === args[0]) || null;
    if (sql.startsWith("SELECT challenge_id, gap_id, evidence_reference")) return this.challenges.find((item) => item.challenge_id === args[0]) || null;
    throw new Error(`Unhandled first SQL: ${sql}`);
  }
  async all({ sql, args }) {
    if (sql.startsWith("SELECT change_id")) return { results: this.publicChanges.filter((item) => item.gap_id === args[0]) };
    if (sql.startsWith("SELECT event_id")) return { results: this.events.filter((item) => item.challenge_id === args[0]) };
    if (sql.startsWith("SELECT challenge_id")) {
      const state = sql.includes("WHERE state") ? args[0] : null;
      return { results: this.challenges.filter((item) => !state || item.state === state) };
    }
    throw new Error(`Unhandled all SQL: ${sql}`);
  }
}

const envFor = (db) => ({ CUSTOMER_CASES_DB: db, GAP_RATE_LIMIT_SALT: "test-only-gap-rate-limit-salt", PUBLIC_ORIGINS: "https://structevidence.com", TEAM_DOMAIN: "https://team.cloudflareaccess.com", ADMIN_UI_AUD: "ui-aud", ADMIN_API_AUD: "api-aud", ADMIN_EMAILS: "admin@example.com" });
const challengeRequest = (gapId, body, ip = "192.0.2.44") => new Request(`https://structevidence.com/api/gaps/${gapId}/challenge`, { method: "POST", headers: { "content-type": "application/json", origin: "https://structevidence.com", "cf-connecting-ip": ip }, body: JSON.stringify(body) });
const validChallenge = (overrides = {}) => ({ gap_id: "OEG-CML-001", evidence_reference: "https://example.org/public-test-report", effect: "SUPPORT", attribution_preference: "ANONYMOUS", note: "Public report identifies the method and observation period.", ...overrides });
const digestGap = (gap) => createHash("sha256").update(JSON.stringify(gap)).digest("hex");
const externalGapText = (gap) => JSON.stringify({
  claim_text: gap.claim_text,
  current_state: gap.current_state,
  current_scope: gap.current_scope,
  what_is_established: gap.what_is_established,
  what_is_not_established: gap.what_is_not_established,
  what_would_change_this: gap.what_would_change_this,
  acceptable_source_examples: gap.acceptable_source_examples,
  non_qualifying_examples: gap.non_qualifying_examples
});

test("registry contains exactly six complete gaps, two per existing public case", () => {
  assert.equal(OPEN_EVIDENCE_GAPS.length, 6);
  const counts = new Map();
  for (const gap of OPEN_EVIDENCE_GAPS) counts.set(gap.case_id, (counts.get(gap.case_id) || 0) + 1);
  assert.deepEqual([...counts.keys()].sort(), ["CML-PDRE-001", "SE-BESS-SODIUM-001", "SE-ONC-NSQNSCLC-CN-001"]);
  assert.deepEqual([...counts.values()], [2, 2, 2]);
  const required = ["gap_id", "case_id", "claim_id", "claim_text", "current_state", "current_scope", "evidence_cutoff", "what_is_established", "what_is_not_established", "what_would_change_this", "acceptable_source_examples", "non_qualifying_examples", "last_reviewed", "challenge_url"];
  for (const gap of OPEN_EVIDENCE_GAPS) for (const field of required) assert.ok(gap[field], `${gap.gap_id}.${field}`);
});

test("four hard-frozen gaps remain byte-for-byte semantically unchanged", () => {
  const expected = {
    "OEG-CML-001": "1b93172c76b6f6eca76380fd92bf185806d1ad14eb99c32b5693a3d8c81a895b",
    "OEG-CML-002": "defa59b1a9d9eebe3799dc47773f9c9762493e21d34651749eea6a170934f941",
    "OEG-BESS-001": "19bf13f252597f84757e49ea04794335a3dd53f1c14737cad7b07b7fa8d9b461",
    "OEG-ONC-001": "5a884c147daef52d6bfdfd557cf9959de3c09d15eef5fd4e0e56acf2f338ea30"
  };
  for (const [gapId, digest] of Object.entries(expected)) assert.equal(digestGap(OPEN_EVIDENCE_GAPS.find((gap) => gap.gap_id === gapId)), digest, gapId);
});

test("BESS-002 keeps its canonical claim while requiring attributable post-commissioning field evidence", () => {
  const gap = OPEN_EVIDENCE_GAPS.find((item) => item.gap_id === "OEG-BESS-002");
  assert.equal(gap.claim_id, "SE-BESS-SODIUM-001.INDEPENDENT_FIELD_PERFORMANCE");
  assert.equal(gap.claim_text, "Independent field-performance evidence for sodium-ion stationary BESS is established.");
  assert.equal(gap.current_state, "NOT_ESTABLISHED");
  assert.match(gap.what_would_change_this, /attributable independent field-operation or performance evidence collected after commissioning/i);
  assert.match(gap.what_would_change_this, /operating duration, availability, delivered capacity or energy, degradation, cycle history, or reliability/i);
  assert.match(gap.what_would_change_this, /all measures are not required at once/i);
  const nonQualifying = gap.non_qualifying_examples.join(" ");
  for (const phrase of ["Manufacturer brochure", "Lab-only test", "simulation", "Planned deployment", "Shipment without commissioning", "generic product specification"]) assert.match(nonQualifying, new RegExp(phrase, "i"));
});

test("public medical gaps cannot expose patient-specific probability or individualized recommendations", () => {
  const medicalGaps = OPEN_EVIDENCE_GAPS.filter((gap) => gap.case_id === "SE-ONC-NSQNSCLC-CN-001");
  const publicText = medicalGaps.map(externalGapText).join(" ");
  const prohibited = [
    /patient-specific/i,
    /specific patient/i,
    /personal(?:ized)? prognosis/i,
    /personal success/i,
    /individualized treatment/i,
    /treatment success probability/i,
    /patient-specific benefit/i,
    /patient-specific survival/i
  ];
  for (const pattern of prohibited) assert.doesNotMatch(publicText, pattern);
  assert.doesNotMatch(publicText, /ECMO\s+(?:is|as)\s+(?:a\s+)?tumou?r therapy/i);
  assert.ok(medicalGaps.every((gap) => gap.claim_id !== "SE-ONC-NSQNSCLC-CN-001.PATIENT_SPECIFIC_SUCCESS_PROBABILITY"));
});

test("ONC-002 is replaced by the existing population-level regulatory claim", () => {
  const gap = OPEN_EVIDENCE_GAPS.find((item) => item.gap_id === "OEG-ONC-002");
  const canonical = JSON.parse(readFileSync(new URL("../../../claims/SE-ONC-NSQNSCLC-CN-001.IVONESCIMAB_APPROVAL.json", import.meta.url), "utf8"));
  assert.equal(gap.claim_id, canonical.claim_id);
  assert.equal(gap.claim_text, canonical.statement);
  assert.equal(gap.current_state, canonical.state);
  assert.match(gap.current_scope, /^Population-level regulatory status/);
  assert.match(gap.what_would_change_this, /official regulator record/i);
});

test("external gap fields are concise and avoid unnecessary internal protocol jargon", () => {
  for (const gap of OPEN_EVIDENCE_GAPS) {
    const text = externalGapText(gap);
    assert.ok(text.length < 2200, `${gap.gap_id} external content is too long`);
    assert.doesNotMatch(text, /\b(?:VCF|RDL|GDR|OIL)\b/, gap.gap_id);
    assert.ok(gap.what_is_established.length > 0 && gap.what_is_not_established.length > 0);
    assert.ok(gap.acceptable_source_examples.length > 0 && gap.non_qualifying_examples.length > 0);
  }
});

test("public gap pages and machine-readable GET routes expose the same frozen registry", async () => {
  const worker = createWorker(), env = envFor(new FakeGapD1());
  const home = await (await worker.fetch(new Request("https://structevidence.com/"), env)).text();
  assert.match(home, /href="\/gaps\/">Open Evidence Gaps/);
  const index = await worker.fetch(new Request("https://structevidence.com/gaps/"), env);
  assert.equal(index.status, 200); const indexHtml = await index.text();
  assert.match(indexHtml, /Open Evidence Gaps/); assert.match(indexHtml, /Six bounded stop points/); assert.match(indexHtml, /No bounty, leaderboard, or contributor score/);
  const page = await worker.fetch(new Request("https://structevidence.com/gaps/OEG-CML-001/"), env);
  assert.equal(page.status, 200); const html = await page.text();
  assert.match(html, /data-gap-challenge-form/); assert.match(html, /No bounty, leaderboard, or contributor score/); assert.match(html, /never changes a state automatically/); assert.doesNotMatch(html, /type="file"/);
  const list = await (await worker.fetch(new Request("https://structevidence.com/api/gaps"), env)).json();
  assert.equal(list.count, 6); assert.equal(list.gaps[0].gap_id, "OEG-CML-001");
  const detailResponse = await worker.fetch(new Request("https://structevidence.com/api/gaps/OEG-CML-001"), env);
  assert.equal(detailResponse.headers.get("access-control-allow-origin"), "*");
  const detail = await detailResponse.json(); assert.equal(detail.gap.claim_id, "CML-PDRE-001.INDEPENDENT_VALIDATION"); assert.equal(detail.change_log[0].change_type, "GAP_OPENED");
});

test("challenge submission records a SUBMITTED event without changing evidence state", async () => {
  const db = new FakeGapD1(), worker = createWorker(), env = envFor(db);
  const response = await worker.fetch(challengeRequest("OEG-CML-001", validChallenge()), env);
  assert.equal(response.status, 201); const result = await response.json();
  assert.match(result.challenge_id, /^SE-GAP-CHL-[A-F0-9]{20}$/); assert.equal(result.state, "SUBMITTED"); assert.equal(result.state_changed, false);
  assert.equal(db.challenges[0].state, "SUBMITTED"); assert.equal(db.challenges[0].attribution_name, null); assert.equal(db.challenges[0].organization_name, null);
  assert.equal(db.events[0].event_type, "SUBMITTED"); assert.equal(db.events[0].previous_state, null); assert.equal(db.events[0].new_state, "SUBMITTED");
  assert.equal(db.challenges[0].client_key_hash.length, 64); assert.doesNotMatch(JSON.stringify(db.challenges[0]), /192\.0\.2\.44/);
});

test("challenge validation rejects state injection, mismatched gaps, missing attribution, and file-like fields", async () => {
  const db = new FakeGapD1(), worker = createWorker(), env = envFor(db);
  const payloads = [
    validChallenge({ state: "ACCEPTED" }),
    validChallenge({ gap_id: "OEG-CML-002" }),
    validChallenge({ attribution_preference: "NAMED", attribution_name: null }),
    validChallenge({ file: "base64-data" })
  ];
  for (const payload of payloads) assert.equal((await worker.fetch(challengeRequest("OEG-CML-001", payload), env)).status, 400);
  assert.equal(db.challenges.length, 0);
});

test("database-backed rolling boundary rejects the sixth submission per IP-derived key", async () => {
  const db = new FakeGapD1(), worker = createWorker(), env = envFor(db);
  for (let index = 0; index < 5; index += 1) assert.equal((await worker.fetch(challengeRequest("OEG-CML-001", validChallenge({ note: `submission ${index}` })), env)).status, 201);
  const limited = await worker.fetch(challengeRequest("OEG-CML-001", validChallenge({ note: "sixth" })), env);
  assert.equal(limited.status, 429); assert.equal(limited.headers.get("retry-after"), "600"); assert.equal(db.challenges.length, 5);
});

test("human-only admin review appends states and separately publishes an attributed change", async () => {
  const db = new FakeGapD1(), env = envFor(db), publicWorker = createWorker();
  const created = await publicWorker.fetch(challengeRequest("OEG-CML-001", validChallenge({ attribution_preference: "NAMED", attribution_name: "Evidence Reviewer", organization_name: "Open Lab" })), env);
  const challengeId = (await created.json()).challenge_id;
  assert.equal((await publicWorker.fetch(new Request("https://structevidence.com/api/admin/gap-challenges"), env)).status, 403);
  const adminWorker = createWorker({ authVerifier: async () => ({ email: "admin@example.com" }) });
  const patch = await adminWorker.fetch(new Request(`https://structevidence.com/api/admin/gap-challenges/${challengeId}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ state: "STATE_CHANGED", note: "Human review accepted qualifying evidence." }) }), env);
  assert.equal(patch.status, 200); assert.equal(db.challenges[0].state, "STATE_CHANGED"); assert.equal(db.events.at(-1).actor, "admin@example.com");
  const published = await adminWorker.fetch(new Request(`https://structevidence.com/api/admin/gap-challenges/${challengeId}/public-change`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ change_type: "STATE_CHANGED", summary: "Independent operating record accepted after human review.", previous_state: "NOT_ESTABLISHED", new_state: "SUPPORTED" }) }), env);
  assert.equal(published.status, 201); const publicChange = await published.json();
  assert.equal(publicChange.attribution, "Evidence Reviewer — Open Lab"); assert.equal(publicChange.append_only, true);
  const detail = await (await publicWorker.fetch(new Request("https://structevidence.com/api/gaps/OEG-CML-001"), env)).json();
  assert.equal(detail.change_log.length, 2); assert.equal(detail.change_log[1].challenge_id, challengeId);
});

test("submission vocabulary is exactly controlled", () => {
  assert.deepEqual([...GAP_SUBMISSION_STATES], ["SUBMITTED", "SCREENED", "IN_SCOPE", "OUT_OF_SCOPE", "QUALIFYING", "NON_QUALIFYING", "NEEDS_CLARIFICATION", "ACCEPTED", "REJECTED", "STATE_CHANGED", "NO_STATE_CHANGE", "SCOPE_CLARIFIED"]);
});

test("migration enforces append-only histories, exact rate window, and URL-only storage", () => {
  const sql = readFileSync(new URL("../migrations/0002_open_evidence_gaps.sql", import.meta.url), "utf8");
  assert.match(sql, /gap_challenge_rate_limit/); assert.match(sql, /datetime\(NEW\.created_at, '-10 minutes'\)/); assert.match(sql, />= 5/);
  assert.match(sql, /gap_challenge_events_no_update/); assert.match(sql, /gap_challenge_events_no_delete/);
  assert.match(sql, /gap_public_changes_no_update/); assert.match(sql, /gap_public_changes_no_delete/);
  assert.doesNotMatch(sql, /BLOB|CREATE TABLE\s+gap_files|file_upload/i);
});
