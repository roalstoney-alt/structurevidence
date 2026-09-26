#!/usr/bin/env node
import { readFileSync, statSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { performance } from "node:perf_hooks";
import { createWorker } from "../deploy/cloudflare-landing/worker.js";

const root = join(dirname(fileURLToPath(import.meta.url)), ".."), fixtureRoot = join(root, "tests/se_frr/fixtures");
const load = (kind, id) => JSON.parse(readFileSync(join(fixtureRoot, kind, `${id}.json`), "utf8"));
const paths = [];
for (const kind of ["subjects", "states", "changes", "evidence", "branches"]) {
  const { readdirSync } = await import("node:fs");
  for (const name of readdirSync(join(fixtureRoot, kind)).sort()) paths.push(join(fixtureRoot, kind, name));
}
const data = {
  subjects: [load("subjects", "SE-SUBJ-000001")],
  states: [load("states", "SE-ST-20260925-000001"), load("states", "SE-ST-20260925-000002")],
  changes: [load("changes", "SE-CHG-20260925-000001")],
  evidence: [1, 2, 3, 4, 5].map((n) => load("evidence", `SE-EV-20260925-${String(n).padStart(6, "0")}`)),
  branches: [1, 2].map((n) => load("branches", `SE-BR-20260925-${String(n).padStart(6, "0")}`)),
  outcomes: [],
};
const worker = createWorker({ sePublicData: data }), env = {};
const endpoints = {
  subject_list: "/api/v1/subjects",
  current_state: "/api/v1/subjects/SE-SUBJ-000001/state",
  state_history: "/api/v1/subjects/SE-SUBJ-000001/states",
  change_feed: "/api/v1/changes",
};
const percentile = (values, p) => values[Math.min(Math.ceil(values.length * p) - 1, values.length - 1)];
const measurements = {};
for (const [name, endpoint] of Object.entries(endpoints)) {
  const durations = [];
  for (let i = 0; i < 200; i += 1) {
    const started = performance.now();
    const response = await worker.fetch(new Request(`https://structevidence.com${endpoint}`), env);
    await response.arrayBuffer();
    if (response.status !== 200) throw new Error(`${endpoint} returned ${response.status}`);
    durations.push(performance.now() - started);
  }
  durations.sort((a, b) => a - b);
  measurements[name] = { median_ms: Number(percentile(durations, 0.5).toFixed(3)), p95_ms: Number(percentile(durations, 0.95).toFixed(3)) };
}
console.log(JSON.stringify({ iterations_per_endpoint: 200, fixture_bytes: paths.reduce((total, path) => total + statSync(path).size, 0), object_count: Object.values(data).reduce((total, values) => total + values.length, 0), measurements }, null, 2));
