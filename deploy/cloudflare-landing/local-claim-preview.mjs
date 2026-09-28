import { createServer } from "node:http";
import { createWorker } from "./worker.js";

const worker = createWorker();
const port = Number(process.env.SE_CLAIM_PREVIEW_PORT || 8792);
const host = "127.0.0.1";
const env = { SE_CLAIM_STOP_POINT: "1", SE_TEMPORAL_VISUALIZATION: "1" };

const server = createServer(async (incoming, outgoing) => {
  try {
    const chunks = []; for await (const chunk of incoming) chunks.push(chunk);
    const request = new Request(`http://${host}:${port}${incoming.url}`, { method: incoming.method, headers: incoming.headers, body: ["GET", "HEAD"].includes(incoming.method) ? undefined : Buffer.concat(chunks) });
    const response = await worker.fetch(request, env);
    outgoing.writeHead(response.status, Object.fromEntries(response.headers));
    outgoing.end(Buffer.from(await response.arrayBuffer()));
  } catch (error) {
    outgoing.writeHead(500, { "content-type": "text/plain; charset=utf-8" });
    outgoing.end("Local claim preview failed.");
    console.error(error);
  }
});

server.listen(port, host, () => console.log(`SE_CLAIM_PREVIEW http://${host}:${port}/__preview__/claim-intake`));
for (const signal of ["SIGINT", "SIGTERM"]) process.on(signal, () => server.close(() => process.exit(0)));
