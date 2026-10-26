import { readFileSync } from "node:fs";

const staging = JSON.parse(readFileSync(new URL("../wrangler.staging.jsonc", import.meta.url), "utf8"));
const production = JSON.parse(readFileSync(new URL("../wrangler.jsonc", import.meta.url), "utf8"));
const stagingDb = staging.d1_databases?.[0];
const productionDb = production.d1_databases?.[0];
const stagingLimiter = staging.ratelimits?.[0];
const productionLimiter = production.ratelimits?.[0];
const expectedUrl = `https://${staging.name}.roalstoney.workers.dev`;
const blockers = [];

if (staging.name !== "structevidence-commercial-staging") blockers.push("unexpected Worker name");
if (staging.main !== "staging-worker.js") blockers.push("staging boundary wrapper missing");
if (staging.workers_dev !== true || staging.preview_urls !== false) blockers.push("workers.dev boundary is not explicit");
if (Array.isArray(staging.routes) && staging.routes.length) blockers.push("staging must not define production/custom routes");
if (!stagingDb || stagingDb.database_name !== "structurevidence-customer-cases-staging") blockers.push("unexpected staging D1 name");
if (!stagingDb?.database_id || stagingDb.database_id === productionDb?.database_id) blockers.push("staging D1 is missing or reuses production");
if (!stagingLimiter?.namespace_id || stagingLimiter.namespace_id === productionLimiter?.namespace_id) blockers.push("rate limiter namespace is missing or reused");
if (staging.vars?.PUBLIC_ORIGINS !== expectedUrl) blockers.push("public origin does not match staging workers.dev URL");
if (staging.vars?.TURNSTILE_EXPECTED_HOSTNAMES !== new URL(expectedUrl).hostname) blockers.push("Turnstile hostname does not match staging URL");
for (const key of ["ADMIN_UI_AUD", "ADMIN_API_AUD", "TURNSTILE_SITE_KEY"]) {
  if (!staging.vars?.[key] || String(staging.vars[key]).startsWith("CONFIGURE_")) blockers.push(`${key} is not configured`);
}

const manifest = {
  environment: "staging",
  worker: { name: staging.name, entrypoint: staging.main, url: expectedUrl, workers_dev: staging.workers_dev, preview_urls: staging.preview_urls, routes: staging.routes || [] },
  d1: { binding: stagingDb?.binding, name: stagingDb?.database_name, id: stagingDb?.database_id, migrations_dir: stagingDb?.migrations_dir },
  rate_limiter: { binding: stagingLimiter?.name, namespace_id: stagingLimiter?.namespace_id, simple: stagingLimiter?.simple },
  turnstile: { site_key: staging.vars?.TURNSTILE_SITE_KEY, secret_binding: "TURNSTILE_SECRET_KEY (Cloudflare secret; never printed)", expected_hostnames: staging.vars?.TURNSTILE_EXPECTED_HOSTNAMES, expected_action: staging.vars?.TURNSTILE_EXPECTED_ACTION },
  access: { team_domain: staging.vars?.TEAM_DOMAIN, ui_audience: staging.vars?.ADMIN_UI_AUD, api_audience: staging.vars?.ADMIN_API_AUD, admin_allowlist: "ADMIN_EMAILS (Cloudflare secret; never printed)" },
  public_origins: staging.vars?.PUBLIC_ORIGINS,
  production_isolation: { worker_name_distinct: staging.name !== production.name, d1_id_distinct: stagingDb?.database_id !== productionDb?.database_id, rate_limit_namespace_distinct: stagingLimiter?.namespace_id !== productionLimiter?.namespace_id, custom_routes_absent: !(staging.routes || []).length },
  required_secrets: ["TURNSTILE_SECRET_KEY", "GAP_RATE_LIMIT_SALT", "ADMIN_EMAILS"],
  blockers
};

console.log(JSON.stringify(manifest, null, 2));
if (blockers.length) process.exitCode = 2;
