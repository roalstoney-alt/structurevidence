#!/usr/bin/env node

import crypto from "node:crypto";
import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const base = path.join(root, "growth", "external-challenge");
const template = fs.readFileSync(path.join(base, "visuals", "evidence-card.template.html"), "utf8");
const data = JSON.parse(fs.readFileSync(path.join(base, "visuals", "card-data.json"), "utf8"));
const output = path.join(base, "output", "cards");
fs.mkdirSync(output, { recursive: true });

const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;").replaceAll("'", "&#039;");

const sha256 = (file) => crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");

const formats = {
  x: { width: 1600, height: 900, pad: 66, inset: 28, brand: 28, small: 17, title: 49, body: 24, label: 17, cellbody: 22, cell: 27, gap: 34, viewport: { width: 1600, height: 900 } },
  linkedin: { width: 1200, height: 627, pad: 48, inset: 22, brand: 22, small: 13, title: 35, body: 18, label: 13, cellbody: 16, cell: 19, gap: 24, viewport: { width: 1200, height: 627 } },
};

const apply = (html, card, spec) => {
  const alt = `${card.claim_id}. Public claim: ${card.public_claim} Evidence boundary: ${card.evidence_boundary} What remains unknown: ${card.what_remains_unknown} What would change it: ${card.what_would_change_it}`;
  const values = {
    WIDTH: spec.width, HEIGHT: spec.height, PAD: spec.pad, INSET: spec.inset, BRAND: spec.brand,
    SMALL: spec.small, TITLE: spec.title, BODY: spec.body, LABEL: spec.label, CELLBODY: spec.cellbody,
    CELL: spec.cell, FOOT: spec.small, GAP: spec.gap, ALT: alt,
    CLAIM_ID: card.claim_id, STATE: card.state.replaceAll("_", " "), PUBLIC_CLAIM: card.public_claim,
    EVIDENCE_BOUNDARY: card.evidence_boundary, WHAT_REMAINS_UNKNOWN: card.what_remains_unknown,
    WHAT_WOULD_CHANGE_IT: card.what_would_change_it, SOURCE_IDS: card.source_ids.join(", "),
    CUTOFF: card.cutoff, VERSION: card.version, SOURCE_URL: card.source_url,
  };
  return Object.entries(values).reduce((text, [key, value]) => text.replaceAll(`{{${key}}}`, escapeHtml(value)), html);
};

const browser = await chromium.launch({
  headless: true,
  ...(process.env.PLAYWRIGHT_BROWSER_EXECUTABLE
    ? { executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE }
    : {}),
});
const manifest = { schema_version: "SE-SOCIAL-CARD-MANIFEST-v0.1", generated_at: "2026-10-29", publication_status: "DO_NOT_PUBLISH", assets: [] };
const altLines = ["# Accessibility text", ""];
const captionLines = ["# Draft captions — human review required", ""];
try {
  for (const [format, spec] of Object.entries(formats)) {
    const dir = path.join(output, format);
    fs.mkdirSync(dir, { recursive: true });
    for (const card of data.cards) {
      const page = await browser.newPage({ viewport: spec.viewport, deviceScaleFactor: 1 });
      const html = apply(template, card, spec);
      await page.setContent(html, { waitUntil: "load" });
      const file = path.join(dir, `${card.claim_id}.png`);
      await page.screenshot({ path: file, type: "png" });
      await page.close();
      const alt = `${card.claim_id}: ${card.public_claim} Boundary: ${card.evidence_boundary} Unknown: ${card.what_remains_unknown} Change condition: ${card.what_would_change_it}`;
      manifest.assets.push({ format, claim_id: card.claim_id, path: path.relative(root, file), sha256: sha256(file), width: spec.width, height: spec.height, approval: "PENDING_HUMAN_REVIEW" });
      altLines.push(`## ${format.toUpperCase()} · ${card.claim_id}`, "", alt, "");
      captionLines.push(`## ${format.toUpperCase()} · ${card.claim_id}`, "", `${card.public_claim}\n\nBoundary: ${card.evidence_boundary}\n\nWhat evidence would change this? ${card.what_would_change_it}\n\nSource and cutoff: https://structurevidence.org/cases/iren-ai-cloud-transition/#${card.claim_id}\n\n#Evidence #DueDiligence`, "");
    }
  }
} finally {
  await browser.close();
}

fs.writeFileSync(path.join(output, "asset-manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
fs.writeFileSync(path.join(output, "ALT_TEXT.md"), altLines.join("\n"));
fs.writeFileSync(path.join(output, "DRAFT_CAPTIONS.md"), captionLines.join("\n"));
console.log(`rendered=${manifest.assets.length} publication=${manifest.publication_status}`);
