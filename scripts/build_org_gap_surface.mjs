import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { OPEN_EVIDENCE_GAPS } from "../deploy/cloudflare-landing/gaps.js";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const API_ROOT = "https://structevidence.com/api/gaps";
const EFFECTS = ["SUPPORT", "CONTRADICT", "NARROW_SCOPE", "CORRECT_ATTRIBUTION"];
const ATTRIBUTIONS = ["NAMED", "ORGANIZATION_ONLY", "ANONYMOUS"];

const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (character) => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
})[character]);
const list = (items) => `<ul>${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
const nav = (current = "gaps") => `<header class="product-header"><nav class="product-nav" aria-label="Primary navigation"><a class="product-brand" href="/"><span>SE</span><strong>StructEvidence</strong></a><button class="product-nav-toggle" type="button" aria-expanded="false" aria-controls="product-links" data-product-nav-toggle>Menu</button><div class="product-links" id="product-links"><a href="/cases/">Evidence Cases</a><a${current === "gaps" ? ' aria-current="page"' : ""} href="/gaps/">Open Evidence Gaps</a><a href="https://structevidence.com/verify/">Commercial verification</a><a href="/method.html">Method</a></div></nav></header>`;
const footer = `<footer class="product-footer"><div class="product-wrap footer-grid"><strong>StructEvidence</strong><a href="/cases/">Evidence cases</a><a href="/gaps/">Open Evidence Gaps</a><a href="https://structevidence.com/verify/">Commercial verification</a><a href="/privacy.html">Privacy</a><span>Public challenge on .org. Canonical API on .com.</span></div></footer>`;

function page({ title, description, canonical, alternate, body, script = false }) {
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(title)} | StructEvidence</title><meta name="description" content="${escapeHtml(description)}"><link rel="canonical" href="${escapeHtml(canonical)}"><link rel="alternate" type="application/json" href="${escapeHtml(alternate)}"><link rel="stylesheet" href="/assets/product.css?v=20261006-public-boundary"></head>
<body class="product-site"><a class="skip-link" href="#main">Skip to content</a>${nav()}<main class="product-main" id="main">${body}</main>${footer}<script src="/assets/product.js"></script>${script ? '<script src="/assets/gap-challenge.js" defer></script>' : ""}</body></html>
`;
}

function facts(gap) {
  return `<dl class="stop-fields"><div class="stop-field"><span class="field-label">GAP_ID</span><p>${escapeHtml(gap.gap_id)}</p></div><div class="stop-field"><span class="field-label">CASE_ID</span><p>${escapeHtml(gap.case_id)}</p></div><div class="stop-field"><span class="field-label">CLAIM</span><p>${escapeHtml(gap.claim_text)}</p></div><div class="stop-field"><span class="field-label">CURRENT STATE</span><p>${escapeHtml(gap.current_state)}</p></div><div class="stop-field"><span class="field-label">SCOPE</span><p>${escapeHtml(gap.current_scope)}</p></div><div class="stop-field"><span class="field-label">EVIDENCE CUTOFF</span><p>${escapeHtml(gap.evidence_cutoff)}</p></div><div class="stop-field"><span class="field-label">WHAT IS ESTABLISHED</span>${list(gap.what_is_established)}</div><div class="stop-field"><span class="field-label">WHAT IS NOT ESTABLISHED</span>${list(gap.what_is_not_established)}</div><div class="stop-field"><span class="field-label">WHAT WOULD CHANGE THIS</span><p>${escapeHtml(gap.what_would_change_this)}</p></div><div class="stop-field"><span class="field-label">ACCEPTABLE SOURCES</span>${list(gap.acceptable_source_examples)}</div><div class="stop-field"><span class="field-label">NON-QUALIFYING SOURCES</span>${list(gap.non_qualifying_examples)}</div></dl>`;
}

function renderIndex() {
  const records = OPEN_EVIDENCE_GAPS.map((gap) => `<article class="evidence-record" data-gap-id="${escapeHtml(gap.gap_id)}"><div class="record-head"><div><p class="field-label">${escapeHtml(gap.gap_id)} · ${escapeHtml(gap.case_id)}</p><h3>${escapeHtml(gap.claim_text)}</h3></div><span class="state ${gap.current_state === "SUPPORTED" ? "supported" : "not-established"}">${escapeHtml(gap.current_state)}</span></div>${facts(gap)}<div class="actions"><a class="button" href="/gaps/${escapeHtml(gap.gap_id)}/">Challenge this gap</a><a class="button secondary" href="${escapeHtml(gap.case_url)}">View case</a><a class="button secondary" href="${API_ROOT}/${escapeHtml(gap.gap_id)}">Machine-readable gap</a></div></article>`).join("\n");
  const body = `<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">StructEvidence</a><span>›</span><span aria-current="page">Open Evidence Gaps</span></nav><section class="page-hero" aria-labelledby="gaps-title"><p class="eyebrow">Public research discovery · six bounded gaps</p><h1 id="gaps-title">Open Evidence Gaps</h1><p class="lead">Inspect the exact evidence boundary on structurevidence.org, then challenge it without entering a sales funnel. Submissions go directly to the single canonical challenge backend on structevidence.com for human review.</p><div class="callout"><strong>Public/commercial boundary:</strong> Challenge submission is free and separate from commercial verification. Submission never changes claim state automatically.</div><div class="actions"><a class="button" href="#gap-records">Inspect six gaps</a><a class="button secondary" href="${API_ROOT}">Canonical machine API</a></div></section><section class="product-section" id="gap-records" aria-labelledby="records-title"><div class="section-head"><div><p class="eyebrow">Current public register</p><h2 id="records-title">Six defined challenge boundaries</h2></div><p>Each record mirrors the canonical machine registry. No new Gap or alternate API is created here.</p></div><div class="evidence-list">${records}</div></section>`;
  return page({ title: "Open Evidence Gaps", description: "Research-side discovery for the six current StructEvidence Open Evidence Gaps.", canonical: "https://structurevidence.org/gaps/", alternate: API_ROOT, body });
}

function renderForm(gap) {
  const effects = EFFECTS.map((effect) => `<option value="${effect}">${effect}</option>`).join("");
  const attributions = ATTRIBUTIONS.map((option) => `<option value="${option}">${option}</option>`).join("");
  const postTarget = `${API_ROOT}/${gap.gap_id}/challenge`;
  return `<section class="product-section" id="challenge" aria-labelledby="challenge-title"><div class="section-head"><div><p class="eyebrow">Public evidence challenge</p><h2 id="challenge-title">Challenge this gap</h2></div><p>No payment, quote request, or sales qualification is required.</p></div><div class="form-layout"><div class="form-panel"><form class="scope-form" method="post" action="${postTarget}" data-gap-challenge-form data-gap-id="${escapeHtml(gap.gap_id)}" data-post-target="${postTarget}"><input type="hidden" name="gap_id" value="${escapeHtml(gap.gap_id)}"><div class="field wide"><label for="evidence-reference">Public URL or document reference *</label><input id="evidence-reference" name="evidence_reference" maxlength="2000" required><small>References only. Do not submit files, private records, credentials, or personal health information.</small></div><div class="field"><label for="effect">Proposed effect *</label><select id="effect" name="effect" required><option value="">Select</option>${effects}</select></div><div class="field"><label for="attribution-preference">Attribution preference *</label><select id="attribution-preference" name="attribution_preference" required><option value="">Select</option>${attributions}</select></div><div class="field" data-named-field hidden><label for="attribution-name">Public contributor name *</label><input id="attribution-name" name="attribution_name" maxlength="200"></div><div class="field" data-organization-field hidden><label for="organization-name">Public organization name *</label><input id="organization-name" name="organization_name" maxlength="300"></div><div class="field"><label for="contact-email">Contact email (optional, never public)</label><input id="contact-email" name="contact_email" type="email" maxlength="254"></div><div class="field wide"><label for="challenge-note">Note (optional)</label><textarea id="challenge-note" name="note" maxlength="4000"></textarea></div><div class="field wide"><button class="button" type="submit">Submit challenge for human review</button></div><p class="form-status" data-gap-form-status role="status" aria-live="polite"></p></form></div><aside class="panel"><p class="field-label">Review and attribution boundary</p><h3>Submission is private until reviewed.</h3><p><strong>Submission does not automatically change the claim state.</strong> Evidence enters human review before any public state change.</p><p><strong>Public attribution is optional.</strong> Attribution means evidence contribution only and does not imply endorsement of StructEvidence's final conclusion.</p><p>Raw submitted text, contact email, hidden identity, private reviewer notes, and private or patient-identifiable materials are not automatically published.</p></aside></div></section>`;
}

function renderDetail(gap) {
  const gapUrl = `https://structurevidence.org/gaps/${gap.gap_id}/`;
  const apiUrl = `${API_ROOT}/${gap.gap_id}`;
  const body = `<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="/">StructEvidence</a><span>›</span><a href="/gaps/">Open Evidence Gaps</a><span>›</span><span aria-current="page">${escapeHtml(gap.gap_id)}</span></nav><section class="page-hero case-hero" aria-labelledby="gap-title"><p class="eyebrow">${escapeHtml(gap.gap_id)} · ${escapeHtml(gap.current_state)}</p><h1 id="gap-title">${escapeHtml(gap.claim_text)}</h1><p class="lead">${escapeHtml(gap.current_scope)}</p><div class="actions"><a class="button" href="#challenge">Challenge this gap</a><a class="button secondary" href="${escapeHtml(gap.case_url)}">View case</a><a class="button secondary" href="${apiUrl}">Machine-readable gap</a></div></section><section class="product-section" aria-labelledby="boundary-title"><div class="section-head"><div><p class="eyebrow">Frozen evidence boundary</p><h2 id="boundary-title">What the current record does and does not establish</h2></div><p>Evidence cutoff: ${escapeHtml(gap.evidence_cutoff)}</p></div><article class="stop-card">${facts(gap)}</article></section>${renderForm(gap)}<section class="product-section" aria-labelledby="commercial-title"><div class="callout"><p class="field-label">Separate commercial path</p><h2 id="commercial-title">Need this evaluated for your decision?</h2><p>Commercial verification is a paid decision scope and is never required to submit a public evidence challenge.</p><a class="button secondary" href="https://structevidence.com/verify/">Open commercial verification</a></div></section>`;
  return page({ title: `${gap.gap_id} Open Evidence Gap`, description: gap.claim_text, canonical: gapUrl, alternate: apiUrl, body, script: true });
}

async function writeMirrored(relativePath, content) {
  for (const base of [ROOT, resolve(ROOT, "docs")]) {
    const target = resolve(base, relativePath);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, content, "utf8");
  }
}

await writeMirrored("gaps/index.html", renderIndex());
for (const gap of OPEN_EVIDENCE_GAPS) await writeMirrored(`gaps/${gap.gap_id}/index.html`, renderDetail(gap));
await writeMirrored("assets/gap-challenge.js", await (await import("node:fs/promises")).readFile(resolve(ROOT, "assets/gap-challenge.js"), "utf8"));

console.log(`Generated .org Gap index and ${OPEN_EVIDENCE_GAPS.length} mirrored detail pages from the canonical registry.`);
