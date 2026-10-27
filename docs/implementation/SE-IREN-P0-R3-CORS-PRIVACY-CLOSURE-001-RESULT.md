# SE-IREN-P0-R3-CORS-PRIVACY-CLOSURE-001 result

Status: `ENGINEERING_CLOSURE_PASS`; `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`; `READY_FOR_OWNER_PRODUCTION_RELEASE=NO`.

Scope lock: Draft PR #54, input HEAD `081c5f29833427c6f140492d89a94c79678663a2`. This record contains no customer row, request body, email, administrator identity, JWT, OTP, Turnstile token, cookie, Secret value, or private signature. No Staging or production deployment was performed.

## Real Staging CORS observations

At `2026-10-27T00:54:01Z`, an HTTP OPTIONS request to the Staging `/api/requests` endpoint used the exact Staging frontend origin, requested `POST`, and requested `content-type,idempotency-key`. The response was HTTP 204 and returned:

- `Access-Control-Allow-Origin` equal to the Staging origin;
- `Access-Control-Allow-Methods: POST, OPTIONS`;
- `Access-Control-Allow-Headers: content-type, idempotency-key`;
- `Vary: Origin`;
- Staging/no-index environment headers.

At `2026-10-27T00:54:02Z`, the same OPTIONS shape from an isolated local test Origin returned HTTP 204 but no allow-origin, allow-methods, allow-headers, or `Vary` response headers. This is the intended refusal to grant cross-origin browser access.

The live form at `/verify/` and its API share the exact origin. Browser observation at `2026-10-27T00:51:21.951Z` confirmed origin equality, so a normal same-origin form POST does not invoke the browser CORS preflight algorithm. This is recorded as `BROWSER_PREFLIGHT_NOT_APPLICABLE_SAME_ORIGIN`, not as a missing test.

For a real browser cross-origin check, an isolated page at a local Origin attempted a request with both non-simple headers. At `2026-10-27T00:54:12.638Z`, the browser returned `TypeError` with the observed outcome `PREFLIGHT_REJECTED_BEFORE_POST`. Because the Origin received no CORS approval, the browser did not send the POST. No production endpoint was addressed.

Result: `STAGING_CORS_HTTP_OPTIONS=PASS`; `CROSS_ORIGIN_BROWSER_FAIL_CLOSED=PASS`; `STAGING_POST_FROM_CROSS_ORIGIN=0`.

## Live three-language baseline and source-only correction

Read-only Staging GETs returned HTTP 200 for `/en/`, `/zh-cn/`, `/es/`, and `/verify/`. Their sanitized SHA-256 values are recorded in the companion JSON. The three home routes correctly exposed `lang=en`, `lang=zh-CN`, and `lang=es`, while the currently deployed shared `/verify/` form was English and its Consent and Turnstile guidance were English. Therefore the deployed baseline remains `LOCALIZED_SHARED_CONSENT=INCOMPLETE_ENGLISH_ONLY`.

The source patch, not deployed by this task, introduces one deterministic EN/zh-CN/ES dictionary for:

- the mandatory Consent statement;
- Turnstile/fallback guidance;
- verification, validation, idempotency-conflict, oversized-request, and service-unavailable errors;
- the successful receipt boundary.

The localized home routes now carry an explicit `lang` parameter to the existing same-origin forms. The client localizes only these shared intake/legal surfaces and marks their language for assistive technology. Canonical routes, service prices, D1 schema, API fields, and the server consent version are unchanged.

Meaning lock:

- customer submission stays private by default;
- form Consent does not authorize research;
- publication still requires separate written authorization;
- success remains `CUSTOMER_PRIVATE` and `NOT_AUTHORIZED`;
- every fail-closed message states that nothing was recorded.

`SE-CUSTOMER-PRIVACY-v1` remains unchanged. The patch does not claim that machine/code review is legal approval or native-speaker approval.

## Human signoff boundary

The unsigned checklist at `docs/implementation/SE-IREN-P0-R3-PRIVACY-LEGAL-SIGNOFF-CHECKLIST.md` covers semantic equivalence, controller/purpose/legal basis, retention, rights, cross-border processing and subprocessors, incidents, minors/prohibited data, logging, Access least privilege, staging/production isolation, and recovery limitations.

The named reviewer, authority, qualifications, jurisdictions, findings, decision, signature time, and record location must be completed in a restricted internal system. They must not be fabricated or committed to this public repository. Until that occurs:

`HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`

`READY_FOR_OWNER_PRODUCTION_RELEASE=NO`

## Regression summary

- Focused intake suite: `19/19 PASS`.
- Full Cloudflare landing/Worker suite: `66/66 PASS`.
- R3 result/privacy guards: `3/3 PASS` (included above).
- Wrangler bundle dry-run: PASS; `--dry-run` exited without deployment.
- Public record drift: PASS.
- Internal link audit: PASS; 0 broken links, 0 orphan pages, 0 cases without state, 0 evidence without parent.
- Legacy Phase-B customer-intake guard: `2/3`; its unchanged baseline assertion expects `https://structevidence.com/verify/` in the current public root `index.html`, where that CTA was already absent at locked input HEAD. Neither the public root page nor this guard changed in R3, so this is not a new regression.
- `git diff --check`: PASS.
- `NEW_REGRESSION_COUNT=0`.

## No-action record

- PR #54 remains Draft and unmerged.
- Production POST: 0.
- Production migration: none.
- Production or Staging Worker deploy: none.
- Production or Staging D1 write: none in this task.
- Public Pilot, social publication, charging, and outreach: none.
