import assert from "node:assert/strict";
import test from "node:test";

import {
  COMMERCIAL_APP_JS_UPGRADE,
  COMMERCIAL_PAGES_V2,
  FORM_TRANSLATIONS,
  INTAKE_COPY,
  localizeIntakePage
} from "../commercial-upgrade.js";
import { createWorker } from "../worker.js";

const paths = ["/verify/", "/context/", "/decision-pack/"];
const locales = ["zh-CN", "es"];
const expectedFormTitles = {
  "/verify/": { "zh-CN": "提交一项陈述供人工审核", es: "Enviar una afirmación para revisión humana" },
  "/context/": { "zh-CN": "提交决策背景", es: "Enviar contexto de decisión" },
  "/decision-pack/": { "zh-CN": "申请决策证据包范围", es: "Solicitar el alcance de un Paquete de decisión" }
};
const expectedButtons = {
  "/verify/": { "zh-CN": "提交人工审核", es: "Enviar para revisión humana" },
  "/context/": { "zh-CN": "提交人工审核", es: "Enviar para revisión humana" },
  "/decision-pack/": { "zh-CN": "申请书面范围说明", es: "Solicitar alcance por escrito" }
};

const formLayout = (html) => html.match(/<section class="form-layout">[\s\S]*?<\/section>/)?.[0] || "";
const controlNames = (html) => [...html.matchAll(/\sname="([^"]+)"/g)].map((match) => match[1]).sort();

test("embedded browser code compiles and the consent contract remains frozen", () => {
  assert.doesNotThrow(() => new Function(COMMERCIAL_APP_JS_UPGRADE));
  assert.match(COMMERCIAL_APP_JS_UPGRADE, /const CONSENT_VERSION = "SE-CUSTOMER-PRIVACY-v1"/);
});

test("server output localizes each full form and preserves the API schema", () => {
  for (const path of paths) {
    const english = localizeIntakePage(COMMERCIAL_PAGES_V2[path], "en");
    assert.match(english, /<html lang="en">/);
    assert.match(formLayout(english), /<form lang="en" /);
    assert.match(formLayout(english), /<aside lang="en" class="boundary-card"/);
    for (const locale of locales) {
      const localized = localizeIntakePage(COMMERCIAL_PAGES_V2[path], locale);
      const layout = formLayout(localized);
      assert.match(localized, new RegExp(`<html lang="${locale}">`));
      assert.match(layout, new RegExp(`<form lang="${locale}" `));
      assert.match(layout, new RegExp(`<aside lang="${locale}" class="boundary-card"`));
      assert.ok(layout.includes(expectedFormTitles[path][locale]));
      assert.ok(layout.includes(expectedButtons[path][locale]));
      assert.ok(layout.includes(INTAKE_COPY[locale].consent));
      assert.ok(layout.includes(INTAKE_COPY[locale].turnstileHelp));
      assert.equal(layout.includes("Submission starts human review."), false);
      assert.equal(layout.includes("Research begins only after separate written authorization."), false);
      assert.deepEqual(controlNames(layout), controlNames(formLayout(english)));
      for (const token of ["SUPPORTED", "CONTRADICTED", "NOT ESTABLISHED", "UNKNOWN", "VERIFICATION REQUIRED"]) {
        assert.ok(layout.includes(token), `${path} ${locale} keeps canonical outcome ${token}`);
      }
    }
  }
});

test("translated select labels keep exact English API values", () => {
  const zhVerify = localizeIntakePage(COMMERCIAL_PAGES_V2["/verify/"], "zh-CN");
  const esContext = localizeIntakePage(COMMERCIAL_PAGES_V2["/context/"], "es");
  assert.match(zhVerify, /<option value="Informational">仅供了解<\/option>/);
  assert.match(zhVerify, /<option value="This quarter">本季度<\/option>/);
  assert.match(zhVerify, /<option value="Blocking a live commitment">阻碍当前承诺<\/option>/);
  assert.match(esContext, /<option value="Exploratory">Exploratorio<\/option>/);
  assert.match(esContext, /<option value="This quarter">Este trimestre<\/option>/);
  assert.match(esContext, /<option value="Commitment pending">Compromiso pendiente<\/option>/);
});

test("all visible form labels and help strings have zh-CN and es mappings", () => {
  const formSources = new Set();
  for (const path of paths) {
    const layout = formLayout(COMMERCIAL_PAGES_V2[path]);
    for (const match of layout.matchAll(/<(?:span|small|h2|p|li|option|button)[^>]*>([^<]+)<\//g)) {
      const source = match[1].trim();
      if (source && source !== INTAKE_COPY.en.consent && source !== INTAKE_COPY.en.turnstileHelp) formSources.add(source);
    }
  }
  const canonicalOnly = new Set(["SUPPORTED", "CONTRADICTED", "NOT ESTABLISHED", "UNKNOWN", "VERIFICATION REQUIRED"]);
  for (const source of formSources) {
    if (canonicalOnly.has(source)) continue;
    assert.ok(FORM_TRANSLATIONS[source]?.["zh-CN"], `missing zh-CN mapping: ${source}`);
    assert.ok(FORM_TRANSLATIONS[source]?.es, `missing es mapping: ${source}`);
  }
});

test("label associations and language attributes remain accessible", () => {
  for (const path of paths) {
    for (const locale of ["en", ...locales]) {
      const html = localizeIntakePage(COMMERCIAL_PAGES_V2[path], locale);
      const layout = formLayout(html);
      for (const match of layout.matchAll(/<label[^>]*for="([^"]+)"/g)) {
        assert.match(layout, new RegExp(`id="${match[1]}"`), `${path} ${locale} label ${match[1]}`);
      }
      assert.match(layout, /role="status" aria-live="polite"/);
    }
  }
});

test("worker applies locale on first HTML response without changing canonicals", async () => {
  const worker = createWorker();
  for (const path of paths) {
    const response = await worker.fetch(new Request(`https://structevidence.com${path}?lang=zh-CN`), { TURNSTILE_SITE_KEY: "0xTEST_PUBLIC_SITE_KEY" });
    const html = await response.text();
    assert.equal(response.status, 200);
    assert.match(html, /<html lang="zh-CN">/);
    assert.match(html, /<form lang="zh-CN" /);
    assert.match(html, /data-sitekey="0xTEST_PUBLIC_SITE_KEY"/);
    assert.match(html, new RegExp(`<link rel="canonical" href="https://structevidence.com${path.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}"`));
  }
});
