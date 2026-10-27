const origin = "https://structevidence-commercial-staging.roalstoney.workers.dev";
const expectations = [
  { path: "/en/", language: "en", marker: "Decision Boundary" },
  { path: "/zh-cn/", language: "zh-CN", marker: "决策边界" },
  { path: "/es/", language: "es", marker: "Límite de decisión" }
];

let failed = false;
for (const expectation of expectations) {
  const response = await fetch(`${origin}${expectation.path}`);
  const html = await response.text();
  const result = {
    path: expectation.path,
    status: response.status,
    language: html.match(/<html lang="([^"]+)"/)?.[1] || null,
    localized_marker: html.includes(expectation.marker),
    staging_banner: html.includes("data-se-staging-banner"),
    noindex: response.headers.get("x-robots-tag"),
    no_store: response.headers.get("cache-control"),
    environment: response.headers.get("x-structurevidence-environment")
  };
  result.pass = result.status === 200 && result.language === expectation.language && result.localized_marker && result.staging_banner && result.noindex === "noindex, nofollow, noarchive" && result.no_store === "no-store" && result.environment === "staging";
  console.log(JSON.stringify(result));
  failed ||= !result.pass;
}

for (const path of ["/verify/", "/context/", "/decision-pack/"]) {
  const response = await fetch(`${origin}${path}`);
  const html = await response.text();
  const result = {
    path,
    status: response.status,
    form: html.includes("data-request-form"),
    consent_boundary: html.includes("does not authorize research") && html.includes("without separate written authorization"),
    turnstile_sitekey_present: /data-sitekey="(?!__TURNSTILE_SITE_KEY__)[A-Za-z0-9_-]{10,100}"/.test(html),
    turnstile_action: html.includes('data-action="public-intake"'),
    accessible_status: html.includes('role="status"') && html.includes('aria-live="polite"'),
    staging_banner: html.includes("data-se-staging-banner")
  };
  result.pass = result.status === 200 && Object.entries(result).filter(([key]) => !["path", "status", "pass"].includes(key)).every(([, value]) => value === true);
  console.log(JSON.stringify(result));
  failed ||= !result.pass;
}

if (failed) process.exitCode = 1;
