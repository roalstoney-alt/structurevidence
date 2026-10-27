import productionWorker from "./worker.js";

const STAGING_HOST = "structevidence-commercial-staging.roalstoney.workers.dev";
const STAGING_BANNER = '<aside role="status" data-se-staging-banner style="padding:.75rem 1rem;background:#4a2400;color:#fff;text-align:center;font-weight:700">STAGING TEST — synthetic submissions only; not a production service.</aside>';
const IDEMPOTENCY_ASSIGNMENT = 'form.dataset.idempotencyKey ||= crypto.randomUUID().replaceAll("-", "");';
const STAGING_IDEMPOTENCY_ASSIGNMENT = `const stagingTestIdempotencyKey = location.hostname === "${STAGING_HOST}" ? params.get("staging_idempotency_key") : null;
    form.dataset.idempotencyKey ||= /^[A-Za-z0-9_-]{20,128}$/.test(stagingTestIdempotencyKey || "") ? stagingTestIdempotencyKey : crypto.randomUUID().replaceAll("-", "");`;

function stagingHeaders(source) {
  const headers = new Headers(source);
  headers.set("cache-control", "no-store");
  headers.set("x-robots-tag", "noindex, nofollow, noarchive");
  headers.set("x-structurevidence-environment", "staging");
  headers.delete("content-length");
  return headers;
}

export default {
  async fetch(request, env, context) {
    const url = new URL(request.url);
    if (env.DEPLOYMENT_ENVIRONMENT !== "staging" || env.STAGING_TEST_ONLY !== "true" || url.hostname !== STAGING_HOST) {
      return new Response("Staging boundary is not configured", { status: 503, headers: stagingHeaders() });
    }
    if (url.pathname === "/robots.txt") {
      return new Response(request.method === "HEAD" ? null : "User-agent: *\nDisallow: /\n", {
        status: 200,
        headers: { ...Object.fromEntries(stagingHeaders()), "content-type": "text/plain; charset=utf-8" }
      });
    }
    const response = await productionWorker.fetch(request, env, context);
    const headers = stagingHeaders(response.headers);
    if (url.pathname === "/assets/app.js" && String(headers.get("content-type") || "").startsWith("application/javascript")) {
      const script = await response.text();
      const instrumented = script.replace(IDEMPOTENCY_ASSIGNMENT, STAGING_IDEMPOTENCY_ASSIGNMENT);
      if (instrumented === script) return new Response("Staging client instrumentation failed", { status: 503, headers });
      return new Response(instrumented, { status: response.status, statusText: response.statusText, headers });
    }
    if (!String(headers.get("content-type") || "").startsWith("text/html") || request.method === "HEAD") {
      return new Response(request.method === "HEAD" ? null : response.body, { status: response.status, statusText: response.statusText, headers });
    }
    const html = await response.text();
    const marked = html.includes("data-se-staging-banner") ? html : html.replace(/<body([^>]*)>/, `<body$1>${STAGING_BANNER}`);
    return new Response(marked, { status: response.status, statusText: response.statusText, headers });
  }
};
