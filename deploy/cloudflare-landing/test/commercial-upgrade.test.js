import assert from "node:assert/strict";
import test from "node:test";
import { createWorker } from "../worker.js";

const env = {};
const worker = createWorker();

async function page(path) {
  const response = await worker.fetch(new Request(`https://structevidence.com${path}`), env);
  assert.equal(response.status, 200);
  return response.text();
}

test("Decision Pack has a dedicated privacy-safe scope form", async () => {
  const html = await page("/decision-pack/");
  assert.match(html, /data-request-form data-request-type="CONTEXT"/);
  assert.match(html, /name="requested_output" value="DECISION_PACK"/);
  assert.match(html, /What would change the decision\?/);
  assert.match(html, /name="confidentiality_ack" type="checkbox" required/);
  assert.doesNotMatch(html, /type="file"/);
});

test("service pages publish the dated evidence-cycle boundary", async () => {
  for (const path of ["/verify/", "/context/", "/decision-pack/", "/pricing/", "/terms/"]) {
    const html = await page(path);
    assert.match(html, /cut-off timestamp/i, path);
  }
  const pricing = await page("/pricing/");
  assert.match(pricing, /No included revision rounds/);
  assert.match(pricing, /separately paid collection cycle/);
  assert.match(pricing, /superseded evidence state is corrected automatically/);
});

test("deliverables exposes the public Decision Pack PDF sample", async () => {
  const html = await page("/deliverables/");
  assert.match(html, /STRUCTUREEVIDENCE_800VDC_DECISION_PACK_SAMPLE_v1\.0\.pdf/);
  assert.match(html, /five-page, customer-neutral example/);
});

test("all commercial pages carry the expanded trust footer", async () => {
  for (const path of ["/", "/verify/", "/context/", "/decision-pack/", "/pricing/", "/deliverables/", "/about/", "/privacy/", "/terms/"]) {
    const html = await page(path);
    assert.match(html, /Operated by MATRIX ASIA PACIFIC LIMITED/, path);
    assert.match(html, /Customer submissions remain separate from public research/, path);
    assert.match(html, /Public proof: 800V DC/, path);
  }
});

test("client script preserves private scoping context and fail-closed authorization copy", async () => {
  const response = await worker.fetch(new Request("https://structevidence.com/assets/app.js"), env);
  assert.equal(response.status, 200);
  const js = await response.text();
  assert.match(js, /case_reference/);
  assert.match(js, /Decision timing:/);
  assert.match(js, /What would change the decision:/);
  assert.match(js, /CUSTOMER_PRIVATE/);
  assert.match(js, /NOT_AUTHORIZED/);
});
