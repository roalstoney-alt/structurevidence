# SE-IREN-P0-R3-LOCALIZED-STAGING-ACCEPTANCE-002 · Result

Date: 2026-10-27 (Asia/Shanghai)

This append-only record documents an authorized deployment and acceptance run against the isolated Staging Worker only. It does not overwrite prior R3 or staging observations. No customer payload, email, raw request ID, idempotency key, Access identity, JWT, OTP, cookie, Turnstile token, or Secret value is committed here.

```text
PROJECT = SE-IREN-P0-R3-LOCALIZED-STAGING-ACCEPTANCE-002
LOCKED_INPUT_HEAD = da0421429a98e8c3d5dec96506b80cdc98fd1f35
EXECUTION_SPEC_HEAD = 5647d491ddd84071ee5cdb9bd3682d39bee24b22
FINAL_HEAD_SHA = GIT_COMMIT_CONTAINING_THIS_RESULT (reported in the PR and final handoff; omitted here to avoid a self-referential hash)
PR_NUMBER = 54
PR_DRAFT = YES

STAGING_DEPLOYED = YES
STAGING_REAL_BROWSER_E2E = PASS_CRITICAL_SURFACES_WITH_DOCUMENT_LANGUAGE_GAP
LOCALIZED_CRITICAL_INTAKE_COPY = PASS
FULL_FORM_LOCALIZATION = NOT_IMPLEMENTED
DOCUMENT_HTML_LANG_ZH_CN_ES = INCORRECT_EN
HUMAN_PRIVACY_LEGAL_SIGNOFF = PENDING
PRODUCTION_RECOVERABILITY = UNKNOWN
READY_FOR_OWNER_PRODUCTION_RELEASE = NO

PRODUCTION_WORKER_CHANGED = NO
PRODUCTION_D1_CHANGED = NO
PRODUCTION_POST_COUNT = 0
MERGE_AUTHORIZED = NO
PUBLIC_PILOT_STARTED = NO
NEW_REGRESSION_COUNT = 0
```

## 1. Locked Staging resources and deployment

The deployment command explicitly used `deploy/cloudflare-landing/wrangler.staging.jsonc`. Preflight and deployment both resolved only:

- Worker: `structevidence-commercial-staging`;
- workers.dev URL: `https://structevidence-commercial-staging.roalstoney.workers.dev`;
- D1: `structurevidence-customer-cases-staging`, ID `65dc6680-0832-401d-8772-6a082b68673c`;
- independent rate-limit namespace: `842054`;
- `STAGING_TEST_ONLY=true`;
- Turnstile action `public-intake` and exact Staging hostname;
- distinct Access UI and API applications;
- no custom routes and no production domain binding.

The previous Staging deployment version was `19f0ef29-c7c0-4cd0-b628-a68d860ec203`. The authorized deployment ran from `2026-10-27T01:13:36Z` to `2026-10-27T01:13:46Z` and produced version `64a10491-6cf2-40b9-ac6e-a7aca364d149`, receiving 100% of Staging traffic. That version was rechecked after browser acceptance.

Rollback remains bounded to the prior Staging version using the same explicit Staging config. No rollback was required.

Artifact SHA-256:

- localized source `commercial-upgrade.js`: `1ce655d7167a7ac45682d1b924f4c1cf2a9c152ef7b09371085f2dd3e904cd4f`;
- production-core source `worker.js`: `2218d1dbbeb182b21edb989b48f399c6841c8f247d19cd79f9a48bbd7736f21e`;
- Staging wrapper `staging-worker.js`: `0037795ec2a4d77102410b4103fb82a0bb360c8ca326004852ca0712bda1335b`;
- Staging config: `bab9d6461b0500fda6a4d12b55356dae00ccae0d73e6dc9686f323385af77fd1`;
- dry-run deployment bundle: `d7d988cc621bc66605cdbc215c401773f1aeec4457890f71e3414c9e47d85e40`.

## 2. Real browser and real Turnstile observations

Three independent synthetic `example.invalid` identities were submitted through the real Staging browser form. A human completed each live Cloudflare Turnstile challenge. Each browser submission returned the successful receipt UI and created one HTTP 201 request.

| Locale | Actual intake route | Document `html lang` | Critical-copy language marker | Local missing-challenge message | Browser result |
| --- | --- | --- | --- | --- | --- |
| EN | `/verify/?lang=en` | `en` | `en` | `Complete human verification before submitting.` | HTTP 201; `REQUEST RECEIVED` |
| 简中 | `/verify/?lang=zh-CN` | `en` | `zh-CN` | `请在提交前完成人机验证。` | HTTP 201; `已收到请求` |
| ES | `/verify/?lang=es` | `en` | `es` | `Complete la verificación humana antes de enviar la solicitud.` | HTTP 201; `SOLICITUD RECIBIDA` |

All three success panels displayed `SUBMITTED`, `CUSTOMER_PRIVATE`, and `NOT_AUTHORIZED`, stated that a human review follows, and stated that the form does not begin research. The zh-CN and es Consent text explicitly preserves both boundaries: submission does not authorize research and publication requires separate written authorization. `SE-CUSTOMER-PRIVACY-v1` was unchanged.

The language result is deliberately bounded. Consent, Turnstile/fallback guidance, missing-challenge status, conflict/error dictionary, and success confirmation were localized and marked for assistive technology. The shared form's headings, labels, navigation, and research-boundary block remain English. More importantly, the document-level `html lang` remained `en` for zh-CN and es query variants. Therefore this run does not claim full-form localization or fully correct document-language metadata.

The three request-ID comparison hashes, rather than raw IDs, are:

- EN: `a6bc54c87d4930e4c5b864b66d2fefb495200896eceb023087c1fd1ecce10005`;
- zh-CN: `38b5ff351268ca34c1b16f380e000dde149ce568b837af92d8fefde10a3d6eb5`;
- es: `408cd6a97d55f2caa81cb70b4aa279574c6e70e511f5ded4aae262a13be4320f`.

No Turnstile token was read into a file or reused. Browser automation checked only that a response was present before each authorized click.

## 3. 201 / 200 / 409 and provider boundaries

For each locale, the browser issued the initial real-challenge request and received HTTP 201. Because the browser intentionally deletes its test idempotency state after success, a controlled Staging test client then replayed the identical canonical payload and key. The durable mapping is checked before Turnstile, so the client supplied a non-secret placeholder rather than storing or reusing the consumed token:

- identical replay: HTTP 200, same request-ID hash, `idempotency_status=REPLAYED`;
- changed claim with the same scoped key: HTTP 409, no ID returned and no write;
- result for EN, zh-CN, and es: PASS.

A fresh invalid token sent to the real Staging endpoint returned HTTP 400 `Human verification failed`; aggregate counts remained unchanged. This is `REAL_PROVIDER_OBSERVED`. Missing, expired, replayed, wrong-hostname, wrong-action, provider-error, and timeout paths were separately exercised by deterministic Worker tests and fail closed with 400 or 503 as applicable. Those cases are `DETERMINISTIC_FAULT_INJECTION`, not claimed as real provider incidents. Rate-limit 429 and oversized-body 413 behavior are likewise deterministic test evidence, not live browser incidents.

## 4. Staging D1 integrity

Before deployment and acceptance, each of the five business tables contained four synthetic rows. After exactly three successful localized logical submissions, the totals were:

| Table | Before | After |
| --- | ---: | ---: |
| `customers` | 4 | 7 |
| `requests` | 4 | 7 |
| `request_events` | 4 | 7 |
| `request_consent_receipts` | 4 | 7 |
| `request_idempotency` | 4 | 7 |

For each locale independently, the final read-only join found exactly one customer, one request, one event, one consent receipt, and one active idempotency mapping. Each request was `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, and `human_owner IS NULL`. Each Consent receipt was accepted under `SE-CUSTOMER-PRIVACY-v1`. Foreign-key violations: 0.

Migrations `0001_customer_intake.sql`, `0002_open_evidence_gaps.sql`, and `0003_intake_hardening.sql` were already applied to the isolated Staging D1. No migration was applied during this acceptance run.

All four append-only triggers were present. UPDATE and DELETE attempts against the synthetic event and Consent tables were rejected with `SQLITE_CONSTRAINT_TRIGGER`; row counts and values remained unchanged.

## 5. CORS, Access, and privacy

Real Staging HTTP OPTIONS observations:

- allowlisted Staging Origin: HTTP 204 with exact `Access-Control-Allow-Origin`, `POST, OPTIONS`, `content-type, idempotency-key`, and `Vary: Origin`;
- disallowed Origin: HTTP 204 with none of those approvals;
- normal browser form/API traffic is same-origin, so `BROWSER_PREFLIGHT_NOT_APPLICABLE_SAME_ORIGIN` remains the accurate classification.

Unauthenticated UI and API admin GETs returned HTTP 302 to Cloudflare Access. Their redirect targets were distinct, consistent with the distinct configured audiences. Using the already-authorized real Access browser session, `/api/admin/requests` returned HTTP 200 and showed the three new synthetic records with the same private/unassigned boundaries as D1. No authentication bypass occurred and no Access credential or human identity was persisted.

All committed observations are aggregate or hashed. The repository contains no synthetic payload body, synthetic email, raw request ID, raw idempotency key, private customer row, administrator identity, authentication artifact, Turnstile token, or Secret.

## 6. Regression results

- Pre-deploy config/binding guard: PASS, 0 blockers.
- Explicit Staging Wrangler dry run: PASS.
- Cloudflare Worker suite before deploy: 66/66 PASS.
- Focused intake/privacy suite before deploy: 29/29 PASS.
- Cloudflare Worker suite after acceptance: 66/66 PASS.
- Layered Turnstile deterministic cases: PASS.
- Real Staging 201/200/409 matrix: 9/9 PASS.
- Three-language missing-challenge and success copy: 6/6 observed as expected.
- Public record drift: PASS.
- Internal links: 0 broken / 0 orphan.
- Legacy Phase-B customer-intake guard: 2/3 with its pre-existing root-page CTA expectation; neither the root page nor that test changed in this task.
- `git diff --check`: PASS after result generation.
- `NEW_REGRESSION_COUNT=0`.

## 7. Release boundary and remaining gates

This Staging run validates the critical localized Consent/Turnstile/error/success surfaces and the durable intake path. It does not authorize production release.

Production-release blockers remain:

1. Correct or explicitly owner-accept the zh-CN/es shared-form scope: document-level language metadata is currently wrong and most form chrome remains English; after a correction, redeploy only Staging and repeat localized browser acceptance.
2. Obtain a real authorized human privacy/legal review in the restricted signing system. `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`; no AI or test result substitutes for that signature.

`PRODUCTION_RECOVERABILITY=UNKNOWN` remains unchanged. Production migration 0003, production Worker deployment, production POST, PR merge, public Pilot, social publication, charging, and outreach remain unauthorized and were not performed.
