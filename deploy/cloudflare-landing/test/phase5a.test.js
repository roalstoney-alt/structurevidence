import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import { createWorker } from "../worker.js";
import {
  IPFSProvider, LocalHashProvider, ReplicatedProofProvider, SnapshotChainProvider,
  canonicalSerialize, classifyRealityRadarCandidate, nextRdlLevel, normalizeRdlRun,
  projectStructuralEvent, derivePhase5Metrics,
} from "../phase5-core.js";

const fixtureRoot = new URL("../../../tests/se_frr/fixtures/", import.meta.url);
const read = (path) => JSON.parse(readFileSync(new URL(path, fixtureRoot), "utf8"));
const rdlRun = {
  rdl_run_id: "SE-RDL-TEST-001", subject_id: "SE-SUBJ-000001",
  started_at: "2026-09-25T12:00:00Z", ended_at: "2026-09-25T12:01:00Z",
  trigger: "TEST", question: "What changed?", research_level: "L0_VERIFY",
  queries_executed: [], sources_discovered: 0, sources_checked: 0, sources_rejected: 0, sources_used: 0,
  evidence_created: [], counter_evidence_created: [], unknowns_created: [], unknowns_resolved: [],
  state_before: null, state_after: "SE-ST-20260925-000001", decision_changed: false,
  runtime_seconds: 60, output_hash: "a".repeat(64), snapshot_hash: "b".repeat(64),
};
const publicData = {
  subjects: [read("subjects/SE-SUBJ-000001.json")],
  states: [read("states/SE-ST-20260925-000001.json"), read("states/SE-ST-20260925-000002.json")],
  changes: [read("changes/SE-CHG-20260925-000001.json")],
  evidence: [1, 2, 3, 4, 5].map((n) => read(`evidence/SE-EV-20260925-${String(n).padStart(6, "0")}.json`)),
  branches: [1, 2].map((n) => read(`branches/SE-BR-20260925-${String(n).padStart(6, "0")}.json`)),
  outcomes: [read("outcomes/SE-OUT-20260925-000001.json"), read("outcomes/SE-OUT-20260925-000002.json")],
  rdlRuns: [rdlRun],
};
const worker = createWorker({ sePublicData: publicData });
const get = (path) => worker.fetch(new Request(`https://structevidence.com${path}`), {});

test("StructuralEventProjection preserves canonical objects without creating a canonical event", async () => {
  const before = canonicalSerialize(publicData);
  const event = await projectStructuralEvent("SE-SUBJ-000001", publicData);
  assert.equal(event.projection_type, "StructuralEventProjection");
  assert.equal(event.event_id, "SE-EVENT-000001");
  assert.equal(event.current_state.state_id, "SE-ST-20260925-000002");
  assert.equal(event.outcomes.length, 1);
  assert.equal("provenance" in event.current_state, false);
  assert.equal(canonicalSerialize(publicData), before);
});

test("as_of projection excludes later observations and keeps historical hash compatibility", async () => {
  const originalHash = publicData.states[0].state_hash;
  const event = await projectStructuralEvent("SE-SUBJ-000001", publicData, { asOf: "2026-09-25T12:30:00Z" });
  assert.equal(event.current_state.state_id, "SE-ST-20260925-000001");
  assert.equal(event.change_history.length, 0);
  assert.equal(event.supporting_evidence.some((item) => item.evidence_id.endsWith("000004")), false);
  assert.equal(publicData.states[0].state_hash, originalHash);
});

test("P0 and P1 proofs are deterministic while P2 and P3 remain inactive", async () => {
  const event = await projectStructuralEvent("SE-SUBJ-000001", publicData);
  const localA = await new LocalHashProvider().createProof(event), localB = await new LocalHashProvider().createProof(event);
  assert.equal(localA.object_hash, localB.object_hash);
  const chain = await new SnapshotChainProvider().createProof(event, event.current_state.chain_hash);
  assert.equal(chain.proof_level, "P1_SNAPSHOT_CHAIN"); assert.match(chain.merkle_root, /^[a-f0-9]{64}$/);
  await assert.rejects(() => new IPFSProvider().createProof(), /NOT_ACTIVATED/);
  await assert.rejects(() => new ReplicatedProofProvider().createProof(), /NOT_ACTIVATED/);
});

test("RDL missing costs are UNKNOWN and escalation stops on no material change", () => {
  const normalized = normalizeRdlRun(rdlRun);
  assert.equal(normalized.compute_cost, "UNKNOWN"); assert.equal(normalized.search_cost, "UNKNOWN"); assert.equal(normalized.observed_credit_delta, "UNKNOWN");
  assert.equal(nextRdlLevel({ research_level: "L0_SCAN" }), "L0_VERIFY");
  assert.equal(nextRdlLevel({ research_level: "L0_VERIFY" }), "STOP_NO_STATE_CHANGE");
  assert.equal(nextRdlLevel({ research_level: "L0_VERIFY", materially_changes_unknown: true }), "L1_VERIFY");
  const metrics = derivePhase5Metrics(publicData);
  assert.equal(metrics.ACTIVE_EVOLVING_OBJECTS, 1); assert.equal(metrics.COST_PER_EVIDENCE, "UNKNOWN");
});

test("Reality Event Radar classifies evidence and contains no acquisition behavior", () => {
  assert.equal(classifyRealityRadarCandidate({ public_source: "https://example.test", normalized_claim: "Observed", counter_to: ["SE-EV-X"] }), "NEW_COUNTER_EVIDENCE");
  assert.equal(classifyRealityRadarCandidate({ public_source: "https://example.test", normalized_claim: "Observed", resolves_unknown: true }), "UNKNOWN_RESOLUTION_CANDIDATE");
  assert.equal(classifyRealityRadarCandidate({}, {}), "NOISE");
  const core = readFileSync(new URL("../phase5-core.js", import.meta.url), "utf8");
  assert.doesNotMatch(core, /lead generation|outreach draft|contact_status|customer score/i);
});

test("event and atlas API endpoints expose projections and all subresources", async () => {
  const events = await (await get("/api/v1/events")).json();
  assert.equal(events.data.items.length, 2); assert.equal(events.data.items[0].event_id, "SE-EVENT-000001");
  assert.ok(events.data.items.some((item) => item.event_id === "SE-EVENT-800001"));
  const atlas = await (await get("/api/v1/atlas")).json(); assert.equal(atlas.data.events.length, 2);
  for (const suffix of ["", "/timeline", "/evidence", "/branches", "/unknowns", "/outcomes", "/proof", "/rdl"]) {
    const response = await get(`/api/v1/events/SE-EVENT-000001${suffix}`);
    assert.equal(response.status, 200, suffix);
    assert.equal((await response.text()).includes("provenance"), false);
  }
});

test("event surface is public, text-first, and exposes required sections", async () => {
  const index = await (await get("/events")).text(), event = await (await get("/events/SE-EVENT-000001")).text();
  assert.match(index, /Structural Events Now/); assert.match(event, /Structural Event/);
  const app = await (await get("/assets/phase5-surface.js")).text();
  for (const label of ["CURRENT STATE", "WHAT CHANGED", "TIMELINE", "EVIDENCE", "COUNTER EVIDENCE", "OPEN UNKNOWNS", "BRANCHES", "OUTCOMES", "WHAT WOULD CHANGE THIS STATE", "PROOF", "RDL HISTORY"]) assert.match(app, new RegExp(label));
});

test("Phase 4 customer acquisition is disabled by default", async () => {
  const response = await worker.fetch(new Request("https://structevidence.com/api/requests", { method: "POST", headers: { "content-type": "application/json" }, body: "{}" }), {});
  assert.equal(response.status, 410); assert.match(await response.text(), /disabled by strategy/);
  const config = await (await get("/api/product-config")).json(); assert.equal(config.founding_access_status, "CLOSED");
  for (const policyPath of ["../../../apps/community-bot/runtime-policy.json", "../../../apps/demand-signal-radar/runtime-policy.json"]) {
    const policy = JSON.parse(readFileSync(new URL(policyPath, import.meta.url), "utf8")); assert.equal(policy.enabled_by_default, false);
  }
});

test("domain-neutral schema permits geography and culture without industrial fields", () => {
  const subject = JSON.parse(readFileSync(new URL("../../../schemas/se-frr/subject.schema.json", import.meta.url), "utf8"));
  const state = JSON.parse(readFileSync(new URL("../../../schemas/se-frr/state.schema.json", import.meta.url), "utf8"));
  assert.ok(subject.properties.domain.enum.includes("geography")); assert.ok(subject.properties.domain.enum.includes("culture"));
  assert.equal(subject.required.includes("industry"), false); assert.equal(subject.required.includes("geography"), false);
  assert.equal(state.required.includes("migration_readiness"), false); assert.equal(state.required.includes("field_deployment_status"), false);
});

test("five seed projections reference existing artifacts without synthetic evidence", () => {
  const seeds = JSON.parse(readFileSync(new URL("../../../data/se-frr/phase5-seed-event-projections.json", import.meta.url), "utf8"));
  assert.equal(seeds.events.length, 5); assert.equal(seeds.canonical_storage_created, false);
  assert.ok(seeds.events.every((event) => event.evidence_refs.length === 0));
  assert.ok(seeds.events.some((event) => event.state === "UNKNOWN"));
});
