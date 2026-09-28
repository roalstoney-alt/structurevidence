import assert from "node:assert/strict";
import test from "node:test";
import CANONICAL from "../../../technical-risk/cml-v1.1/pdre/CML-PDRE-001/pdre-record.json" with { type: "json" };
import RDL from "../../../rdl/research/records/CML-PDRE-001-L1-FIELD-DEPLOYMENT-2026-09-20/research-record.json" with { type: "json" };
import { build800vPublicClaim, CLAIM_SLUG, CLAIM_TRANSLATIONS } from "../phase5c-claims.js";
import { deriveExpressionBoundary, EXPRESSION_LOCALES, STATE_EXPLANATIONS } from "../phase5c-expression.js";
import { CLAIM_STOP_POINT_JS } from "../phase5c-claim-surface.js";
import { createWorker } from "../worker.js";

const library = await build800vPublicClaim(CANONICAL, RDL);
const latest = library.versions.at(-1);
const env = { SE_CLAIM_STOP_POINT: "1" };

function localized(version, locale) {
  const t = CLAIM_TRANSLATIONS[locale], translated = t.versions?.[version.version];
  return deriveExpressionBoundary(version, { locale, claim: t.claim || version.stop_point.CLAIM, supports: translated?.supports || version.stop_point.SUPPORTS, doesNotSupport: translated?.doesNot || version.stop_point.DOES_NOT_SUPPORT });
}

test("5C1 expression is a deterministic derivative of one bound Stop-Point authority", () => {
  const first = localized(latest, "EN"), second = localized(latest, "EN");
  assert.deepEqual(first, second);
  assert.equal(first.determination, latest.stop_point.determination);
  assert.equal(first.derived_from_projection_hash, latest.projection_hash);
  assert.equal(first.boundary_complete, true);
  assert.match(first.decision_sentence, /It does not establish:/);
  assert.match(first.citation_text, /Does not support:/);
  assert.match(first.short_summary, /It does not establish:/);
});

test("complete citation generation fails closed without scope, cutoff, or either boundary side", () => {
  const withoutScope = { ...latest, stop_point: { ...latest.stop_point, SCOPE: { ...latest.stop_point.SCOPE, jurisdiction: "UNRESOLVED" } } };
  const withoutCutoff = { ...latest, stop_point: { ...latest.stop_point, AS_OF: "" } };
  const withoutCounterBoundary = { ...latest, stop_point: { ...latest.stop_point, determination: { ...latest.stop_point.determination, does_not_support: [] } } };
  assert.throws(() => deriveExpressionBoundary(withoutScope), /SCOPE_OR_CUTOFF/);
  assert.throws(() => deriveExpressionBoundary(withoutCutoff), /SCOPE_OR_CUTOFF/);
  assert.throws(() => deriveExpressionBoundary(withoutCounterBoundary), /BOUNDARY_INCOMPLETE/);
});

test("evidence time and StructEvidence knowledge time remain distinct and historical versions are not rewritten", () => {
  const current = localized(latest, "EN"), historical = localized(library.versions[0], "EN");
  assert.equal(current.as_of, RDL.core.effective_at);
  assert.equal(current.knowledge_as_of, RDL.core.known_at);
  assert.notEqual(current.as_of, current.knowledge_as_of);
  assert.equal(historical.version, 1);
  assert.equal(historical.knowledge_as_of, "2026-08-01T23:59:59Z");
});

test("EN, ZH-CN, and ES expressions retain one machine boundary while translating controlled copy", () => {
  const outputs = EXPRESSION_LOCALES.map((locale) => localized(latest, locale));
  for (const output of outputs) {
    assert.equal(output.claim_id, latest.claim_id); assert.equal(output.version, latest.version);
    assert.equal(output.projection_hash, latest.projection_hash); assert.equal(output.determination.state, "ATTRIBUTABLE_ONLY");
    assert.equal(output.scope.population_scope, "ONE_NAMED_PRODUCTION_DEPLOYMENT_INSTANCE");
    assert.equal(output.state_explanation, STATE_EXPLANATIONS[output.render_locale].ATTRIBUTABLE_ONLY);
    assert.ok(output.citation_text.includes(output.determination.state));
  }
  assert.match(outputs[1].decision_sentence, /不能据此推出/);
  assert.match(outputs[2].decision_sentence, /No permite concluir/);
});

test("short summaries and social metadata cannot upgrade one instance into industry adoption", async () => {
  const expression = localized(latest, "EN");
  assert.match(expression.short_summary, /Industry-wide adoption/i);
  const html = await (await createWorker().fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}`), env)).text();
  const description = html.match(/<meta name="description" content="([^"]+)"/)[1];
  assert.match(description, /Industry-wide adoption/i);
  assert.doesNotMatch(description, /industry-wide adoption (is|has been) established/i);
});

test("fixed version HTML and JSON expose the same version, hash, and complete citation", async () => {
  const worker = createWorker();
  const htmlResponse = await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}/versions/2?lang=ZH-CN`), env);
  const jsonResponse = await worker.fetch(new Request(`http://127.0.0.1/claims/${CLAIM_SLUG}/versions/2.json?lang=ZH-CN`), env);
  assert.equal(htmlResponse.status, 200); assert.equal(jsonResponse.status, 200);
  const html = await htmlResponse.text(), json = await jsonResponse.json();
  const embedded = JSON.parse(html.match(/<script type="application\/ld\+json">([^<]+)<\/script>/)[1]);
  assert.deepEqual(embedded, json);
  assert.equal(json.version, 2); assert.equal(json.render_locale, "ZH-CN");
  assert.match(json.stable_url, /\/versions\/2$/); assert.match(json.citation_text, /不能据此推出/);
});

test("copy controls copy only complete or explicitly bounded text", async () => {
  const js = await (await createWorker().fetch(new Request("http://127.0.0.1/__preview__/claim-stop-point.js"), env)).text();
  assert.match(js, /data-full-citation/); assert.match(js, /data-short-summary/);
  assert.match(js, /DOES_NOT_SUPPORT boundary/);
  assert.doesNotMatch(CLAIM_STOP_POINT_JS, /navigator\.clipboard/);
});
