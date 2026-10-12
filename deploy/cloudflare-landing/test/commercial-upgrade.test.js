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
  assert.match(html, /name="privacy_notice_ack" type="checkbox" required/);
  assert.match(html, /name="confidentiality_ack" type="checkbox" required/);
  assert.match(html, /does not authorize research, marketing, publication/);
  assert.doesNotMatch(html, /type="file"/);
});

test("service pages publish the dated evidence-cycle boundary", async () => {
  for (const path of ["/verify/", "/context/", "/decision-pack/", "/pricing/", "/terms/"]) {
    const html = await page(path);
    assert.match(html, /cut-off timestamp/i, path);
  }
  const pricing = await page("/pricing/");
  assert.match(pricing, /Confirmed service errors/);
  assert.match(pricing, /without requiring purchase of another cycle/);
  assert.match(pricing, /new source universe/);
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
  assert.match(js, /privacy_notice_version:"2026-10-08"/);
  assert.match(js, /publication_authorization:false/);
});

test("privacy and terms disclose collection and separate correction from new research", async () => {
  const privacy = await page("/privacy/"), terms = await page("/terms/");
  assert.match(privacy, /patient records, identity documents, passwords, private keys/);
  assert.match(privacy, /does not authorize research, marketing or publication/);
  assert.match(terms, /confirmed service error is corrected without requiring another purchase/i);
  assert.match(terms, /Website updates do not retroactively amend/);
});

test("Verify handoff prefills protocol scope without submitting", async () => {
  const response = await worker.fetch(new Request("https://structevidence.com/assets/app.js"), env);
  const js = await response.text();
  assert.match(js, /prefill\('claim_or_question','question'\)/);
  assert.match(js, /prefill\('existing_evidence','minimum_missing_evidence'\)/);
  assert.match(js, /params\.get\('claim_id'\)/);
  assert.match(js, /params\.get\('match_class'\)/);
  assert.match(js, /params\.get\('rdl'\)/);
  assert.doesNotMatch(js, /\.submit\(/);
  assert.match(js, /Research authorization<\/dt><dd>NOT_AUTHORIZED/);
});
