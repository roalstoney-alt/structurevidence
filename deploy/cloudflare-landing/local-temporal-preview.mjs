import { createServer } from "node:http";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { createWorker } from "./worker.js";

const root = new URL("../../", import.meta.url);
const readJson = (path) => JSON.parse(readFileSync(new URL(path, root), "utf8"));
const readJsonl = (path) => readFileSync(new URL(path, root), "utf8").trim().split("\n").filter(Boolean).map((line) => JSON.parse(line));
const canonical = readJson("technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json");
const temporalRecord = structuredClone(canonical);
temporalRecord.pdre_record.timeline = readJsonl("technical-risk/cml-v1.1/pdre/CML-PDRE-001/timeline.jsonl")
  .filter((item) => item.evidence_refs.length && item.event_domain !== "RESEARCH_ADMINISTRATION")
  .map((item) => ({ event_id: item.event_id, event: item.event_type, effective_at: item.effective_at, known_at: item.known_at, evidence_refs: item.evidence_refs, limitations: item.limitations }));
temporalRecord.pdre_record.state_history = readJsonl("technical-risk/cml-v1.1/pdre/CML-PDRE-001/state-history.jsonl")
  .filter((item) => item.event_type === "MIGRATION_READINESS_TRANSITION")
  .map((item) => ({ change_event_id: item.state_event_id, state_before: item.previous_migration_readiness, state_after: item.migration_readiness,
    known_at: item.known_at, effective_at: item.effective_at, evidence_ids: item.evidence_refs, reason: item.reason,
    supports: item.interpretation, does_not_support: item.limitations }));
const researchRecords = [readJson("rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json")];
const worker = createWorker({ temporalRecord, temporalResearchRecords: researchRecords });
const port = Number(process.env.SE_TEMPORAL_PORT || 8791);
const host = "127.0.0.1";

const server = createServer(async (incoming, outgoing) => {
  try {
    const url = `http://${host}:${port}${incoming.url}`;
    const chunks = []; for await (const chunk of incoming) chunks.push(chunk);
    const request = new Request(url, { method: incoming.method, headers: incoming.headers, body: ["GET", "HEAD"].includes(incoming.method) ? undefined : Buffer.concat(chunks) });
    const response = await worker.fetch(request, { SE_TEMPORAL_VISUALIZATION: "1" });
    outgoing.writeHead(response.status, Object.fromEntries(response.headers));
    outgoing.end(Buffer.from(await response.arrayBuffer()));
  } catch (error) {
    outgoing.writeHead(500, { "content-type": "text/plain; charset=utf-8" }); outgoing.end("Local preview failed.");
    console.error(error);
  }
});
server.listen(port, host, () => console.log(`SE_TEMPORAL_PREVIEW http://${host}:${port}/__preview__/temporal/800vdc`));
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => server.close(() => process.exit(0)));
