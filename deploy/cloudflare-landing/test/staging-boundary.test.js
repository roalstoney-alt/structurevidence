import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import stagingWorker from "../staging-worker.js";

const stagingEnv = Object.freeze({
  DEPLOYMENT_ENVIRONMENT: "staging",
  STAGING_TEST_ONLY: "true",
  TURNSTILE_SITE_KEY: "CONFIGURE_STAGING_TURNSTILE_SITE_KEY"
});

test("staging wrapper fails closed outside the exact workers.dev boundary", async () => {
  for (const [url, env] of [
    ["https://structevidence.com/", stagingEnv],
    ["https://structevidence-commercial-staging.roalstoney.workers.dev/", { ...stagingEnv, STAGING_TEST_ONLY: "false" }],
    ["https://structevidence-commercial-staging.roalstoney.workers.dev/", { ...stagingEnv, DEPLOYMENT_ENVIRONMENT: "production" }]
  ]) {
    const response = await stagingWorker.fetch(new Request(url), env);
    assert.equal(response.status, 503);
    assert.equal(response.headers.get("x-structurevidence-environment"), "staging");
  }
});

test("staging HTML is visibly marked, uncached, and excluded from indexing", async () => {
  const response = await stagingWorker.fetch(new Request("https://structevidence-commercial-staging.roalstoney.workers.dev/verify/"), stagingEnv);
  assert.equal(response.status, 200);
  assert.equal(response.headers.get("cache-control"), "no-store");
  assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow, noarchive");
  assert.equal(response.headers.get("x-structurevidence-environment"), "staging");
  assert.match(await response.text(), /data-se-staging-banner/);
});

test("staging robots blocks every crawler", async () => {
  const response = await stagingWorker.fetch(new Request("https://structevidence-commercial-staging.roalstoney.workers.dev/robots.txt"), stagingEnv);
  assert.equal(response.status, 200);
  assert.equal(await response.text(), "User-agent: *\nDisallow: /\n");
  assert.equal(response.headers.get("x-robots-tag"), "noindex, nofollow, noarchive");
});

test("staging may pin an idempotency key without bypassing Turnstile or changing production client code", async () => {
  const response = await stagingWorker.fetch(new Request("https://structevidence-commercial-staging.roalstoney.workers.dev/assets/app.js"), stagingEnv);
  const script = await response.text();
  assert.equal(response.status, 200);
  assert.match(script, /staging_idempotency_key/);
  assert.match(script, /location\.hostname === "structevidence-commercial-staging\.roalstoney\.workers\.dev"/);
  assert.match(script, /turnstile_token/);
  assert.match(script, /Complete human verification before submitting/);
  const productionScript = (await (await import("../worker.js")).default.fetch(new Request("https://structevidence.com/assets/app.js"), stagingEnv)).text();
  assert.doesNotMatch(await productionScript, /staging_idempotency_key/);
});

test("staging config cannot bind production resources or routes", () => {
  const staging = JSON.parse(readFileSync(new URL("../wrangler.staging.jsonc", import.meta.url), "utf8"));
  const production = JSON.parse(readFileSync(new URL("../wrangler.jsonc", import.meta.url), "utf8"));
  assert.equal(staging.name, "structevidence-commercial-staging");
  assert.equal(staging.main, "staging-worker.js");
  assert.equal(staging.workers_dev, true);
  assert.equal(staging.preview_urls, false);
  assert.equal(staging.routes, undefined);
  assert.equal(staging.d1_databases[0].database_name, "structurevidence-customer-cases-staging");
  assert.notEqual(staging.d1_databases[0].database_id, production.d1_databases[0].database_id);
  assert.notEqual(staging.ratelimits[0].namespace_id, production.ratelimits[0].namespace_id);
  assert.equal(staging.vars.PUBLIC_ORIGINS, "https://structevidence-commercial-staging.roalstoney.workers.dev");
  assert.equal(staging.vars.TURNSTILE_EXPECTED_HOSTNAMES, "structevidence-commercial-staging.roalstoney.workers.dev");
});
