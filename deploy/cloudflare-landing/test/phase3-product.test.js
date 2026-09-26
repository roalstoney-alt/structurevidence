import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { createWorker } from "../worker.js";
import { MemorySeApiStore } from "../se-api-v1.js";

const here = dirname(fileURLToPath(import.meta.url));
const fixtures = join(here, "../../../tests/se_frr/fixtures");
const read = (kind, id) => JSON.parse(readFileSync(join(fixtures, kind, `${id}.json`), "utf8"));
const publicData = {
  subjects: [read("subjects", "SE-SUBJ-000001")],
  states: [read("states", "SE-ST-20260925-000001"), read("states", "SE-ST-20260925-000002")],
  changes: [read("changes", "SE-CHG-20260925-000001")],
  evidence: [1, 2, 3, 4, 5].map((n) => read("evidence", `SE-EV-20260925-${String(n).padStart(6, "0")}`)),
  branches: [1, 2].map((n) => read("branches", `SE-BR-20260925-${String(n).padStart(6, "0")}`)),
  outcomes: [],
};
const store = new MemorySeApiStore();
const authorized = async () => ({ email: "reviewer@example.test" });
const worker = createWorker({ sePublicData: publicData, seApiStore: store, authVerifier: authorized });
const env = { FOUNDING_ACCESS_STATUS: "WAITLIST" };
const get = (path, init = {}) => worker.fetch(new Request(`https://structevidence.com${path}`, init), env);

test("all required public product routes render API-only shells", async () => {
  const routes = ["/states", "/states/SE-SUBJ-000001", "/changes", "/changes/SE-CHG-20260925-000001", "/evidence/SE-EV-20260925-000001", "/request", "/challenge/SE-ST-20260925-000002", "/founding"];
  for (const route of routes) {
    const response = await get(route);
    assert.equal(response.status, 200, route);
    const html = await response.text();
    assert.match(html, /data-product-route=/);
    assert.match(html, /\/assets\/product-surface\.js/);
    assert.doesNotMatch(html, /Synthetic|synthetic|customer@example/i);
  }
});

test("private product routes are noindex and never cached", async () => {
  for (const route of ["/request", "/challenge/SE-ST-20260925-000002", "/outcome/SE-REQ-20260925-000001"]) {
    const response = await get(route);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow, noarchive");
    assert.equal(response.headers.get("cache-control"), "no-store");
    assert.match(await response.text(), /noindex,nofollow,noarchive/);
  }
});

test("outcome route requires Access when verifier denies", async () => {
  const denied = createWorker({ sePublicData: publicData, seApiStore: store, authVerifier: async () => { throw new Response("required", { status: 403 }); } });
  const response = await denied.fetch(new Request("https://structevidence.com/outcome/SE-REQ-20260925-000001"), env);
  assert.equal(response.status, 403);
  assert.doesNotMatch(await response.text(), /Report an outcome/);
});

test("product client exposes State, temporal, evidence, branch, and form experiences", async () => {
  const source = await (await get("/assets/product-surface.js")).text();
  for (const marker of ["STATE_LIST_VIEW", "Current recorded State", "Confidence boundary", "What did StructEvidence know at date X?", "Later Evidence", "Possible branches", "ACCEPTED", "COUNTER", "UNRESOLVED", "REJECTED", "REQUEST RECEIVED", "CHALLENGE SUBMITTED"]) assert.match(source, new RegExp(marker.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")));
  assert.match(source, /fetch\('\/api\/v1'/);
  assert.doesNotMatch(source, /canonical\/|fixtures\/|technical-risk\/records/);
  assert.doesNotMatch(source, /Confidence:\s*\d+%/);
});

test("responsive CSS preserves mobile priority without wide tables", async () => {
  const css = await (await get("/assets/product-surface.css")).text();
  assert.match(css, /@media\(max-width:800px\)/);
  assert.match(css, /grid-template-columns:1fr/);
  assert.match(css, /:focus-visible/);
});

test("State API exposes semantic comparison fields without private provenance", async () => {
  const state = await (await get("/api/v1/states/SE-ST-20260925-000002")).json();
  for (const key of ["accepted_evidence_ids", "counter_evidence_ids", "unresolved_evidence_ids", "unknowns", "branch_ids", "change_event_id"]) assert.ok(key in state.data, key);
  assert.equal("provenance" in state.data, false);
  const history = await (await get("/api/v1/subjects/SE-SUBJ-000001/states")).json();
  assert.equal(history.data[1].change_event_id, "SE-CHG-20260925-000001");
});

test("Change API exposes counter-evidence deltas", async () => {
  const body = await (await get("/api/v1/changes/SE-CHG-20260925-000001")).json();
  assert.ok(Array.isArray(body.data.counter_evidence_added));
  assert.ok(Array.isArray(body.data.counter_evidence_removed));
});

test("telemetry accepts only privacy-safe dimensions", async () => {
  const accepted = await get("/api/product-events", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ event: "STATE_VIEW", route: "/states/SE-SUBJ-000001", subject_id: "SE-SUBJ-000001" }) });
  assert.equal(accepted.status, 202);
  const leaked = await get("/api/product-events", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ event: "REQUEST_SUBMIT", route: "/request", email: "private@example.test" }) });
  assert.equal(leaked.status, 400);
});

test("founding access is configuration-driven and fails to WAITLIST", async () => {
  assert.deepEqual(await (await get("/api/product-config")).json(), { founding_access_status: "WAITLIST" });
  const invalid = await worker.fetch(new Request("https://structevidence.com/api/product-config"), { FOUNDING_ACCESS_STATUS: "INVALID" });
  assert.deepEqual(await invalid.json(), { founding_access_status: "WAITLIST" });
});

test("default Worker public projection remains empty", async () => {
  const defaultWorker = createWorker();
  const response = await defaultWorker.fetch(new Request("https://structevidence.com/api/v1/subjects"), {});
  const body = await response.json();
  assert.deepEqual(body.data.items, []);
});

test("robots and sitemap exclude every private surface and datum", async () => {
  const robots = await (await get("/robots.txt")).text();
  for (const route of ["/request", "/challenge", "/outcome", "/admin", "/api"]) assert.match(robots, new RegExp(`Disallow: ${route}`));
  const sitemap = await (await get("/sitemap.xml")).text();
  for (const forbidden of ["/request", "/challenge", "/outcome", "/admin", "customer@example", "private question"]) assert.equal(sitemap.includes(forbidden), false);
  assert.match(sitemap, /\/states\/SE-SUBJ-000001/);
  assert.match(sitemap, /\/changes\/SE-CHG-20260925-000001/);
});

test("malformed routes and methods fail closed", async () => {
  assert.equal((await get("/states/not-an-id")).status, 404);
  assert.equal((await get("/states", { method: "POST" })).status, 405);
  assert.equal((await get("/api/product-events", { method: "POST", headers: { "content-type": "application/json" }, body: "{" })).status, 400);
});
