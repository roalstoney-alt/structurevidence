import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import test from "node:test";
import { COMMERCIAL_FEATURE_AVAILABILITY, PUBLIC_800VDC_SNAPSHOT } from "../decision-boundary.js";
import { createWorker } from "../worker.js";

const worker = createWorker();
const expectedFeatures = Object.freeze({
  PUBLIC_EVIDENCE_AND_READ_APIS: "LIVE",
  PRIVATE_INTAKE_AND_REQUEST_HISTORY: "LIVE",
  SCOPED_PRIVATE_DECISION_RECORD: "AVAILABLE_WITH_HUMAN_SCOPE",
  PRIVATE_MANAGED_GAP_REGISTER: "AVAILABLE_WITH_HUMAN_SCOPE",
  EVIDENCE_NOTIFICATIONS: "PROPOSED_NOT_LIVE",
  RECURRING_SUBSCRIPTIONS: "PROPOSED_NOT_LIVE",
  CUSTOMER_DECISION_BOUNDARY_API: "PROPOSED_NOT_LIVE"
});
const localeRoutes = Object.freeze({ "/": "en", "/en/": "en", "/zh-cn/": "zh-CN", "/es/": "es" });

async function html(path) {
  const response = await worker.fetch(new Request(`https://structevidence.com${path}`), {});
  assert.equal(response.status, 200, path);
  return response.text();
}

test("commercial feature availability is explicit and conservative", () => {
  assert.deepEqual(Object.fromEntries(COMMERCIAL_FEATURE_AVAILABILITY.map(({ feature_id, status }) => [feature_id, status])), expectedFeatures);
  assert.equal(COMMERCIAL_FEATURE_AVAILABILITY.filter(({ status }) => status === "LIVE").length, 2);
  assert.equal(COMMERCIAL_FEATURE_AVAILABILITY.filter(({ status }) => status === "AVAILABLE_WITH_HUMAN_SCOPE").length, 2);
  assert.equal(COMMERCIAL_FEATURE_AVAILABILITY.filter(({ status }) => status === "PROPOSED_NOT_LIVE").length, 3);
});

test("EN, zh-CN, and ES expose the same Decision Boundary structure and statuses", async () => {
  for (const [path, locale] of Object.entries(localeRoutes)) {
    const page = await html(path);
    assert.match(page, new RegExp(`data-se-locale="${locale}"`), path);
    for (const step of ["ESTABLISHED", "UNKNOWN", "CHANGED", "WHAT_WOULD_CHANGE_IT"]) assert.match(page, new RegExp(`data-boundary-step="${step}"`), `${path} ${step}`);
    for (const [feature, status] of Object.entries(expectedFeatures)) {
      assert.match(page, new RegExp(`data-feature-id="${feature}" data-availability="${status}"`), `${path} ${feature}`);
    }
    for (const token of ["USD 199", "USD 1,999", "USD 4,999", "USD 399"]) assert.match(page, new RegExp(token.replace("$", "\\$")), `${path} ${token}`);
  }
});

test("homepage locale canonicals and reciprocal hreflang are deterministic", async () => {
  const canonicals = { "/": "/", "/en/": "/en/", "/zh-cn/": "/zh-cn/", "/es/": "/es/" };
  for (const [path, canonical] of Object.entries(canonicals)) {
    const page = await html(path);
    assert.match(page, new RegExp(`<link rel="canonical" href="https://structevidence\\.com${canonical}">`));
    for (const [language, target] of [["x-default", "/"], ["en", "/en/"], ["zh-CN", "/zh-cn/"], ["es", "/es/"]]) {
      assert.match(page, new RegExp(`hreflang="${language}" href="https://structevidence\\.com${target}"`), `${path} ${language}`);
    }
  }
});

test("public 800VDC facts link to canonical .org evidence without proxying it", async () => {
  for (const path of Object.keys(localeRoutes)) {
    const page = await html(path);
    for (const url of Object.values(PUBLIC_800VDC_SNAPSHOT.urls)) assert.match(page, new RegExp(url.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")), `${path} ${url}`);
    assert.match(page, /2026-10-22T14:02:00Z/);
    assert.match(page, /1aa90c414d4eee5f98adc1a35adcad304543eb30bfd57946fd7a998a37a1dea1/);
    assert.match(page, /CHINDATA_E3_E4/);
    assert.match(page, /SECOND_REAL_HUMAN_REVIEW/);
    assert.match(page, /UNSPECIFIED/);
    assert.match(page, /OEG-CML-001/);
    assert.match(page, /OEG-CML-002/);
    assert.doesNotMatch(page, /fetch\(['"]https:\/\/structurevidence\.org/);
  }
});

test("bounded-zero and customer-action guardrails remain explicit", async () => {
  const english = await html("/");
  assert.match(english, /bounded zero is not a claim of global absence/i);
  assert.match(english, /No customer action is inferred/);
  assert.match(english, /not a purchase, architecture, deployment, investment, or rejection recommendation/i);
  assert.match(english, /not independent validation or multi-entity replication/i);
  assert.doesNotMatch(english, /guaranteed (?:ROI|savings|outcome)/i);
  assert.doesNotMatch(english, /customer testimonial|trusted by|customers achieved/i);
});

test("protected .org artifacts, D1 intake migration, and locale price manifests do not drift", () => {
  const expected = Object.freeze({
    "../../../cases/800vdc/source-dependency/index.html": "e42b94dcbce09900c9b79bc2374bf09b53ace2d1b9e897a50fb544715272ba38",
    "../../../cases/800vdc/source-dependency-v0.1.json": "9038817ab15e1202ea5ae8ca374f515f5381b6480fce22f2ff137d3267cd7705",
    "../../../cases/800vdc/decision-conditions/index.html": "a50ab5f0985decd60aab105b90365ea3c10f4c0e5195d8c779c544649fd4d581",
    "../../../cases/800vdc/decision-conditions-v0.1.json": "c451662988a44c9907c906e6e245b1ee64e5c204fc5dca7b4d06c26f4b49f040",
    "../../../cases/800vdc/decision-conditions-v0.1.md": "bafe2695ee79f6cc0a9b5ed033546d1a36a84071d7a447f9ffed247eb6fe9fea",
    "../migrations/0001_customer_intake.sql": "156cea56e8278abc280315c10b98af03616cc9c2f71a5bc8a2b02a358c47b851",
    "../locales/en.json": "b85af98ab67ad66bc05f0d90c01e6030a2577a37199f4de9ce022393b84c6cfe",
    "../locales/zh-CN.json": "1dab213b5f6f1356d70cf2d4ec551af4aef822f2ff43d22cbc1baa0d1683e310",
    "../locales/es.json": "89d74f1e785c59927f20f92ca6cf19d1bc55d0300eeedd76a2463ada2b2b58af"
  });
  for (const [relative, hash] of Object.entries(expected)) {
    const actual = createHash("sha256").update(readFileSync(new URL(relative, import.meta.url))).digest("hex");
    assert.equal(actual, hash, relative);
  }
});

test("sitemap and robots publish only commercial canonicals and protect admin paths", async () => {
  const sitemapResponse = await worker.fetch(new Request("https://structevidence.com/sitemap.xml"), {});
  assert.equal(sitemapResponse.status, 200);
  assert.match(sitemapResponse.headers.get("content-type"), /application\/xml/);
  const sitemap = await sitemapResponse.text();
  for (const path of ["/", "/en/", "/zh-cn/", "/es/", "/verify/", "/context/", "/decision-pack/", "/gaps/OEG-CML-001/"]) assert.match(sitemap, new RegExp(`<loc>https://structevidence\\.com${path}</loc>`));
  assert.doesNotMatch(sitemap, /structurevidence\.org/);
  assert.doesNotMatch(sitemap, /\/admin\//);
  const robots = await (await worker.fetch(new Request("https://structevidence.com/robots.txt"), {})).text();
  assert.match(robots, /Disallow: \/admin\//);
  assert.match(robots, /Disallow: \/api\/admin\//);
  assert.match(robots, /Sitemap: https:\/\/structevidence\.com\/sitemap\.xml/);
});

test("Decision Boundary internal links, keyboard landmarks, and mobile CSS remain available", async () => {
  for (const path of Object.keys(localeRoutes)) {
    const page = await html(path);
    assert.match(page, /<a class="skip" href="#main">/);
    assert.match(page, /<main id="main">/);
    assert.match(page, /<nav aria-label="Primary navigation">/);
    assert.match(page, /<div class="lang-switch" aria-label="Language">/);
    const internal = [...page.matchAll(/href="(\/[^"#]*)"/g)].map((match) => match[1]);
    for (const href of new Set(internal)) {
      const response = await worker.fetch(new Request(`https://structevidence.com${href}`), {});
      assert.ok([200, 308].includes(response.status), `${path} -> ${href}: ${response.status}`);
    }
  }
  const css = await (await worker.fetch(new Request("https://structevidence.com/assets/app.css"), {})).text();
  assert.match(css, /@media\(max-width:800px\)/);
  assert.match(css, /\.availability-grid/);
  assert.match(css, /grid-template-columns:1fr/);
});
