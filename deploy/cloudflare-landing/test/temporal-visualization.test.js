import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";
import CANONICAL_800V_RECORD from "../../../technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json" with { type: "json" };
import FIELD_DEPLOYMENT_RDL_RECORD from "../../../rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json" with { type: "json" };
import { createWorker } from "../worker.js";
import { projectTemporalVisualization, temporalProjectionCanonicalForm } from "../temporal-visualization.js";
import { BUNDLED_TEMPORAL_STATE_HISTORY, BUNDLED_TEMPORAL_TIMELINE } from "../temporal-canonical-adapter.js";

const researchRecords = [FIELD_DEPLOYMENT_RDL_RECORD];

test("production temporal adapter exactly mirrors canonical JSONL sources", () => {
  const root = new URL("../../../", import.meta.url);
  const readJsonl = (path) => readFileSync(new URL(path, root), "utf8").trim().split("\n").map((line) => JSON.parse(line));
  const timeline = readJsonl("technical-risk/cml-v1.1/pdre/CML-PDRE-001/timeline.jsonl")
    .filter((item) => item.evidence_refs.length && item.event_domain !== "RESEARCH_ADMINISTRATION")
    .map((item) => ({ event_id: item.event_id, event: item.event_type, effective_at: item.effective_at, known_at: item.known_at, evidence_refs: item.evidence_refs, limitations: item.limitations }));
  const stateHistory = readJsonl("technical-risk/cml-v1.1/pdre/CML-PDRE-001/state-history.jsonl")
    .filter((item) => item.event_type === "MIGRATION_READINESS_TRANSITION")
    .map((item) => ({ change_event_id: item.state_event_id, state_before: item.previous_migration_readiness, state_after: item.migration_readiness, known_at: item.known_at, effective_at: item.effective_at, evidence_ids: item.evidence_refs, reason: item.reason || "UNKNOWN", supports: item.interpretation, does_not_support: item.limitations }));
  assert.deepEqual(BUNDLED_TEMPORAL_TIMELINE, timeline);
  assert.deepEqual(BUNDLED_TEMPORAL_STATE_HISTORY, stateHistory);
});

test("TemporalVisualizationProjection is deterministic and does not mutate canonical inputs", async () => {
  const beforeRecord = JSON.stringify(CANONICAL_800V_RECORD), beforeResearch = JSON.stringify(researchRecords);
  const first = await projectTemporalVisualization(CANONICAL_800V_RECORD, { windowDays: 90, researchRecords });
  const second = await projectTemporalVisualization(CANONICAL_800V_RECORD, { windowDays: 90, researchRecords });
  assert.deepEqual(first, second); assert.equal(first.projection_hash, second.projection_hash);
  assert.equal(temporalProjectionCanonicalForm(first), temporalProjectionCanonicalForm(second));
  assert.match(first.projection_hash, /^[a-f0-9]{64}$/); assert.match(first.source_snapshot_hash, /^[a-f0-9]{64}$/);
  assert.equal(JSON.stringify(CANONICAL_800V_RECORD), beforeRecord); assert.equal(JSON.stringify(researchRecords), beforeResearch);
});

test("as_of knowledge-time safety excludes every future-known object", async () => {
  const beforeIngest = await projectTemporalVisualization(CANONICAL_800V_RECORD, { asOf: "2026-09-16T23:59:59Z", windowDays: 90, researchRecords });
  assert.equal(beforeIngest.states.length, 0); assert.equal(beforeIngest.evidence_events.length, 0); assert.equal(beforeIngest.counter_evidence_events.length, 0); assert.equal(beforeIngest.research_decision_events.length, 0); assert.equal(beforeIngest.open_unknowns.length, 0);
  const beforeRdl = await projectTemporalVisualization(CANONICAL_800V_RECORD, { asOf: "2026-09-19T23:59:59Z", windowDays: 90, researchRecords });
  assert.ok(beforeRdl.evidence_events.every((item) => Date.parse(item.timestamp) <= Date.parse(beforeRdl.as_of)));
  assert.equal(beforeRdl.research_decision_events.length, 0);
});

test("800V projection shows the accepted RDL decision but never upgrades canonical readiness", async () => {
  const projection = await projectTemporalVisualization(CANONICAL_800V_RECORD, { windowDays: 90, researchRecords });
  assert.equal(projection.current_frame.state, "R3"); assert.equal(projection.r4_to_r5, null);
  assert.equal(projection.transition_availability, "NO_CANONICAL_CHANGE_EVENT");
  assert.equal(projection.research_decision_events.length, 1);
  assert.equal(projection.research_decision_events[0].canonical_state_mutated, false);
  assert.ok(projection.research_decision_events[0].evidence_ids.includes("L1-EV-CML-PDRE-001-FIELD-DEPLOYMENT-001"));
  assert.ok(projection.open_unknowns.some((item) => item.unknown_key.includes("OPERATING_HISTORY")));
  assert.ok(projection.open_unknowns.some((item) => item.unknown_key.includes("MULTI_ENTITY_REPLICATION")));
  assert.equal(projection.current_frame.counter_evidence_count, 2);
});

test("transparent component rates retain source-event traceability and UNKNOWN is not zero", async () => {
  const projection = await projectTemporalVisualization(CANONICAL_800V_RECORD, { windowDays: 90, researchRecords });
  const byName = new Map(projection.velocity_series.map((item) => [item.component, item]));
  assert.equal(byName.get("QUALIFYING_EVIDENCE_RATE").event_count, 2);
  assert.equal(byName.get("COUNTER_EVIDENCE_RATE").event_count, 1);
  assert.equal(byName.get("UNKNOWN_RESOLVED_RATE").event_count, 1);
  assert.equal(byName.get("STATE_TRANSITION_RATE").event_count, "UNKNOWN");
  assert.equal(byName.get("STATE_TRANSITION_RATE").rate_per_day, "UNKNOWN");
  for (const rate of projection.velocity_series) for (const id of rate.source_event_ids) assert.ok(projection.provenance_map[id]);
  assert.equal("velocity_score" in projection, false); assert.equal("confidence" in projection, false);
});

test("TEST_ONLY fixture maps branch timing, unknown resolution, and R4 to R5 when supported", async () => {
  const fixture = structuredClone(CANONICAL_800V_RECORD);
  fixture.core.known_at = "2026-09-01T00:00:00Z"; fixture.core.updated_at = "2026-09-03T00:00:00Z";
  fixture.pdre_record.migration_readiness = { code: "R5", name: "FIELD_DEPLOYED", interpretation: "REAL_WORLD_VALIDATED", evidence_refs: ["TEST-EV-R5"], limitations: ["TEST_ONLY"] };
  fixture.pdre_record.state_history = [{ change_event_id: "TEST-CHG-R4-R5", state_before: "R4", state_after: "R5", known_at: "2026-09-03T00:00:00Z", effective_at: "2026-09-02T00:00:00Z", evidence_ids: ["TEST-EV-R5"], reason: "TEST_ONLY qualifying field evidence", supports: "TEST_ONLY R5", does_not_support: ["TEST_ONLY replication"] }];
  fixture.pdre_record.branches = [{ branch_id: "TEST-BRANCH-1", known_at: "2026-09-02T00:00:00Z", effective_at: "2026-09-02T00:00:00Z", evidence_ids: ["TEST-EV-R5"], status: "ACTIVE" }];
  fixture.pdre_record.unknown_history = [{ unknown_id: "TEST-UNKNOWN-1", status: "RESOLVED", known_at: "2026-09-02T00:00:00Z", effective_at: "2026-09-02T00:00:00Z", evidence_refs: ["TEST-EV-R5"] }];
  const projection = await projectTemporalVisualization(fixture, { asOf: "2026-09-03T00:00:00Z", windowDays: 30 });
  assert.equal(projection.r4_to_r5.change_event_id, "TEST-CHG-R4-R5"); assert.equal(projection.branches[0].branch_id, "TEST-BRANCH-1");
  assert.equal(projection.unknown_events[0].event_type, "UNKNOWN_RESOLVED");
});

test("approved temporal release is public and local preview remains feature-gated", async () => {
  const worker = createWorker();
  const previewPath = "/__preview__/temporal/800vdc", publicPath = "/events/SE-EVENT-800001/temporal", endpoint = "/api/v1/events/SE-EVENT-800001/temporal-visualization";
  assert.equal((await worker.fetch(new Request(`http://127.0.0.1${previewPath}`), {})).status, 404);
  assert.equal((await worker.fetch(new Request(`https://structevidence.com${previewPath}`), { SE_TEMPORAL_VISUALIZATION: "1" })).status, 404);
  const page = await worker.fetch(new Request(`http://127.0.0.1${previewPath}`), { SE_TEMPORAL_VISUALIZATION: "1" });
  assert.equal(page.status, 200); assert.match(page.headers.get("x-robots-tag"), /noindex/);
  const release = await worker.fetch(new Request(`https://structevidence.com${publicPath}`), {});
  assert.equal(release.status, 200); assert.match(await release.text(), /index,follow/); assert.equal(release.headers.get("x-robots-tag"), null);
  const get = await worker.fetch(new Request(`https://structevidence.com${endpoint}?window=30`), {});
  assert.equal(get.status, 200); const body = await get.json(); assert.equal(body.meta.preview_only, false); assert.equal(body.meta.canonical_mutation, false); assert.equal(body.data.velocity_series[0].window_days, 30);
  assert.equal((await worker.fetch(new Request(`http://127.0.0.1${endpoint}`, { method: "POST" }), { SE_TEMPORAL_VISUALIZATION: "1" })).status, 405);
});

test("motion renderer exposes deterministic motion grammar, central rail, and reduced-motion steps", async () => {
  const worker = createWorker(), env = { SE_TEMPORAL_VISUALIZATION: "1" };
  const js = await (await worker.fetch(new Request("https://structevidence.com/assets/temporal-motion.js"), env)).text();
  const css = await (await worker.fetch(new Request("https://structevidence.com/assets/temporal-motion.css"), env)).text();
  for (const token of ["IDLE", "FLOWING", "DECELERATING", "EVENT_HOLD", "STATE_CHANGE_HOLD", "RESUMING", "PAUSED", "COMPLETE", "data-scrubber", "JUMP R4→R5", "CENTRAL EVIDENCE RAIL", "EVIDENCE CADENCE", "NEXT EVENT", "projection_hash"]) assert.match(js, new RegExp(token));
  assert.match(css, /prefers-reduced-motion:reduce/); assert.match(css, /@media\(max-width:760px\)/); assert.match(css, /@keyframes breathe/); assert.match(css, /@keyframes flow/);
  assert.match(js, /PLAYBACK SPEED ≠ OBSERVED EVENT RATE/); assert.match(js, /Operating history & reliability/); assert.match(js, /Independent performance validation/);
  assert.doesNotMatch(js, /fetch\([^)]*(openai|anthropic)|momentum score|confidence.*%/i);
});

test("temporal projection schema is valid JSON and contains no mutation contract", () => {
  const schema = JSON.parse(readFileSync(new URL("../../../schemas/se-frr/temporal-visualization-projection.schema.json", import.meta.url), "utf8"));
  assert.equal(schema.title, "TemporalVisualizationProjection"); assert.equal(schema.properties.projection_version.const, "SE_TEMPORAL_VISUALIZATION_v0.1");
  const source = readFileSync(new URL("../temporal-visualization.js", import.meta.url), "utf8");
  assert.doesNotMatch(source, /INSERT INTO|UPDATE .*state|DELETE FROM|createEvidence|createState/i);
});
