#!/usr/bin/env node
import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { createWorker } from "../deploy/cloudflare-landing/worker.js";
import { MemorySeApiStore } from "../deploy/cloudflare-landing/se-api-v1.js";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const fixtures = join(root, "tests/se_frr/fixtures");
const read = (kind, id) => JSON.parse(readFileSync(join(fixtures, kind, `${id}.json`), "utf8"));
const data = {
  subjects: [read("subjects", "SE-SUBJ-000001")],
  states: [read("states", "SE-ST-20260925-000001"), read("states", "SE-ST-20260925-000002")],
  changes: [read("changes", "SE-CHG-20260925-000001")],
  evidence: [1, 2, 3, 4, 5].map((n) => read("evidence", `SE-EV-20260925-${String(n).padStart(6, "0")}`)),
  branches: [1, 2].map((n) => read("branches", `SE-BR-20260925-${String(n).padStart(6, "0")}`)),
  outcomes: [],
};
const worker = createWorker({ sePublicData: data, seApiStore: new MemorySeApiStore(), authVerifier: async () => ({ email: "local-reviewer" }) });
const env = { FOUNDING_ACCESS_STATUS: "WAITLIST", PUBLIC_ORIGINS: "http://127.0.0.1:8788", PUBLIC_INTAKE_RATE_LIMITER: { limit: async () => ({ success: true }) } };
const port = Number(process.env.PORT || 8788);

createServer(async (incoming, outgoing) => {
  const chunks = [];
  for await (const chunk of incoming) chunks.push(chunk);
  const request = new Request(`http://127.0.0.1:${port}${incoming.url}`, { method: incoming.method, headers: incoming.headers, body: ["GET", "HEAD"].includes(incoming.method) ? undefined : Buffer.concat(chunks) });
  const response = await worker.fetch(request, env);
  outgoing.writeHead(response.status, Object.fromEntries(response.headers));
  outgoing.end(Buffer.from(await response.arrayBuffer()));
}).listen(port, "127.0.0.1", () => {
  console.log(`Phase 3 test-data preview: http://127.0.0.1:${port}/states`);
  console.log("Local test fixtures are injected only by this script; production remains empty.");
});
