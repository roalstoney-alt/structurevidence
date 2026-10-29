#!/usr/bin/env node

import fs from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const output = process.env.SE_QA_OUTPUT
  ? path.resolve(process.env.SE_QA_OUTPUT)
  : path.join(root, "growth", "external-challenge", "output", "site-qa");
fs.mkdirSync(output, { recursive: true });

const baseUrl = process.env.SE_PREVIEW_URL || "http://127.0.0.1:8765";
const browser = await chromium.launch({
  headless: true,
  ...(process.env.PLAYWRIGHT_BROWSER_EXECUTABLE
    ? { executablePath: process.env.PLAYWRIGHT_BROWSER_EXECUTABLE }
    : {}),
});

const report = {
  schema_version: "SE-SITE-QA-v0.1",
  checked_at: "2026-10-29",
  target: baseUrl,
  checks: [],
  console_errors: [],
};

async function inspect(name, viewport, pathname, screenshot) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => {
    if (message.type() === "error") report.console_errors.push(`${name}: ${message.text()}`);
  });
  page.on("pageerror", (error) => report.console_errors.push(`${name}: ${error.message}`));
  const response = await page.goto(`${baseUrl}${pathname}`, { waitUntil: "networkidle" });
  await page.keyboard.press("Tab");
  const metrics = await page.evaluate(() => ({
    title: document.title,
    horizontal_overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
    challenge_cards: document.querySelectorAll(".challenge-workbench-card").length,
    challenge_controls: document.querySelectorAll('.challenge-workbench-card a[href^="https://structevidence.com/verify/"]').length,
    challenge_workbench_visible: Boolean(document.querySelector("#challenge-workbench")),
    decision_sample_visible: Boolean(document.querySelector(".ddr-sample")),
    ddr_navigation_visible: Boolean(document.querySelector('a[href="ddr-sample.html"], a[href="/cases/iren-ai-cloud-transition/#IREN-R009"]')),
    source_cutoff_visible: document.body.innerText.includes("2026-10-22"),
    active_element: document.activeElement?.tagName || null,
    focus_indicator_visible: (() => {
      const active = document.activeElement;
      if (!active || active === document.body) return false;
      const style = getComputedStyle(active);
      return style.outlineStyle !== "none" && parseFloat(style.outlineWidth) >= 2;
    })(),
    verify_links: [...document.querySelectorAll('a[href^="https://structevidence.com/verify/"]')].map((node) => node.getAttribute("href")),
    decision_pack_links: [...document.querySelectorAll('a[href^="https://structevidence.com/decision-pack/"]')].map((node) => node.getAttribute("href")),
    internal_links: [...document.querySelectorAll("a[href]")]
      .map((node) => node.getAttribute("href"))
      .filter((href) => href && !href.startsWith("#") && !href.startsWith("http") && !href.startsWith("mailto:") && !href.startsWith("tel:")),
  }));
  const internalResults = [];
  for (const href of [...new Set(metrics.internal_links)]) {
    const target = new URL(href, `${baseUrl}${pathname}`);
    target.hash = "";
    const check = await page.request.get(target.href, { failOnStatusCode: false });
    internalResults.push({ href, status: check.status() });
  }
  metrics.internal_link_results = internalResults;
  delete metrics.internal_links;
  await page.screenshot({ path: path.join(output, screenshot), fullPage: true });
  report.checks.push({ name, pathname, viewport, http_status: response?.status(), ...metrics });
  await page.close();
}

try {
  await inspect("desktop-case", { width: 1440, height: 1000 }, "/cases/iren-ai-cloud-transition/", "desktop-case.png");
  await inspect("mobile-case", { width: 390, height: 844 }, "/cases/iren-ai-cloud-transition/", "mobile-case.png");
  await inspect("desktop-ddr", { width: 1280, height: 900 }, "/cases/iren-ai-cloud-transition/ddr-sample.html", "desktop-ddr.png");
} finally {
  await browser.close();
}

const caseChecks = report.checks.filter((check) => check.name.endsWith("case"));
const allInternalLinksPass = report.checks.every((check) =>
  check.internal_link_results.every((link) => link.status >= 200 && link.status < 400));
const allDecisionLinksPass = report.checks.every((check) =>
  check.decision_pack_links.every((href) => href === "https://structevidence.com/decision-pack/?case=SE-IREN-AI-CLOUD-001"));
report.result = (
  report.console_errors.length === 0
  && report.checks.every((check) => check.http_status === 200 && !check.horizontal_overflow && check.focus_indicator_visible && check.source_cutoff_visible)
  && caseChecks.every((check) => check.challenge_cards === 3 && check.challenge_controls === 3 && check.challenge_workbench_visible && check.ddr_navigation_visible)
  && report.checks.find((check) => check.name === "desktop-ddr")?.decision_sample_visible
  && report.checks.find((check) => check.name === "desktop-ddr")?.ddr_navigation_visible
  && allInternalLinksPass
  && allDecisionLinksPass
) ? "PASS" : "FAIL";

fs.writeFileSync(path.join(output, "qa-report.json"), JSON.stringify(report, null, 2) + "\n");
console.log(`site_qa=${report.result} console_errors=${report.console_errors.length}`);
if (report.result !== "PASS") process.exitCode = 1;
