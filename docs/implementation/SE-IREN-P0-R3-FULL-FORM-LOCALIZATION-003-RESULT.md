# SE-IREN-P0-R3-FULL-FORM-LOCALIZATION-003 · Result

Completed: 2026-10-27 18:11 HKT / 2026-10-27T10:11:08Z  
Repository: `roalstoney-alt/structurevidence`  
Branch: `codex/se-iren-intake-hardening-v01`  
Draft PR: `#54`  
Locked input HEAD: `871b07474af08508a3c5470f953af75dc152c854`  
Deployed code HEAD: `00a77cf15c7c6da23bec948e781804459794cea5`

## Outcome

The isolated Staging acceptance passed. The shared intake forms at `/verify/`, `/context/`, and `/decision-pack/` now render EN, Simplified Chinese, and Spanish form content with deterministic server-side first paint and matching client behavior. The API field names, English protocol values, canonical URLs, prices, evidence records, and `SE-CUSTOMER-PRIVACY-v1` remain unchanged.

The deployed target was only `structevidence-commercial-staging`, using `wrangler.staging.jsonc`, Staging D1 `65dc6680-0832-401d-8772-6a082b68673c`, and limiter namespace `842054`. The config contains no production route. Worker version changed from `64a10491-6cf2-40b9-ac6e-a7aca364d149` to `07358cc6-f01c-4ee3-8dc3-3a60b1559ee1`. No production Worker, D1, route, POST, or migration was touched.

## Localization and actual DOM

Nine actual DOM combinations were inspected: three form journeys times three locales. The checks covered document title, `html lang`, explicit form/boundary language, label/control relationships, every field label, help string, option label and value, Consent, Turnstile help, buttons, Research Boundary, error copy, and success confirmation.

- EN behavior and API values remain stable.
- zh-CN and ES labels, help, introductions, options, buttons, Consent, errors, Research Boundary, and confirmations are localized.
- Option display strings are localized while submitted values remain exactly `Informational`, `Exploratory`, `This quarter`, `Blocking a live commitment`, or `Commitment pending`.
- Canonical state tokens such as `UNKNOWN`, `SUBMITTED`, `CUSTOMER_PRIVATE`, and `NOT_AUTHORIZED` remain visible by design.
- Cloudflare controls the checkbox label `Verify you are human`; it remained provider-controlled English in all three journeys.
- This is full **form** localization. Shared-route marketing narrative outside the form remains English and is not represented as translated.

The three missing-verification messages observed in real local DOM were:

- EN: `Complete human verification before submitting.`
- zh-CN: `请在提交前完成人机验证。`
- ES: `Complete la verificación humana antes de enviar la solicitud.`

No network POST was sent by these missing-verification checks.

## Real Staging browser acceptance

The human-completed Turnstile observations are classified `REAL_PROVIDER_OBSERVED`, separately from deterministic fault-injection tests.

| Locale / path | Create | Exact replay | Changed-payload conflict | Confirmation |
|---|---:|---:|---:|---|
| EN `/verify/` | 201 | 200 | 409 | localized EN |
| zh-CN `/context/` | 201 | 200 | 409 | localized zh-CN |
| ES `/decision-pack/` | 201 | 200 | 409 | localized ES |

Only SHA-256 digests of the three synthetic Request IDs are retained in the JSON result. Raw Request IDs, raw idempotency keys, synthetic emails/payload bodies, Turnstile tokens, Access credentials, administrator identity, JWTs, OTPs, Secrets, and private rows are not committed.

## D1, append-only, Access, and CORS

Staging D1 aggregate counts moved from 7 to 10 in each of the five intake tables. The three new logical requests each produced exactly one customer, request, event, Consent receipt, and active idempotency mapping. All three stayed `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, and unassigned. All three Consent receipts use the frozen Consent version. Foreign-key violations remain zero.

All four append-only probes were rejected with `SQLITE_CONSTRAINT_TRIGGER`: UPDATE and DELETE for `request_events`, and UPDATE and DELETE for `request_consent_receipts`. Post-probe counts remained 10 in every intake table.

Unauthenticated admin GET remained protected by Cloudflare Access with HTTP 302. The existing authorized browser identity loaded the Staging admin request array and saw all three synthetic records with their private/not-authorized boundary. No identity or row content was persisted in this report.

Real Staging OPTIONS returned HTTP 204 with exact allowed Origin, `POST, OPTIONS`, `content-type, idempotency-key`, and `Vary: Origin`. A disallowed Origin received no allow-Origin header. A real browser OPTIONS call from a different localhost origin was blocked by CORS; no POST was attempted. Normal form traffic remains same-origin, so an automatic browser preflight is not applicable to the form submissions.

## Regression and hashes

- Module and embedded client JavaScript compile: PASS.
- Explicit `wrangler.staging.jsonc` dry-run: PASS.
- Worker/landing suite after deployment and report guards: 75/75 PASS.
- Public record drift: PASS.
- Internal links: 0 broken, 0 orphan.
- `git diff --check`: PASS.
- Legacy Phase-B customer-intake guard: 2/3, with its unchanged pre-existing root-page CTA expectation. The root page and that guard were not changed here.
- `NEW_REGRESSION_COUNT=0`.

Principal SHA-256 values:

- `commercial-upgrade.js`: `4f9af20c5c36b8d47090cc14c68266c7ea529bc78d549f0709726f0b5c074ada`
- `worker.js`: `8a01b397a92bcf9a6183fc79f6ca7c4f1ef54ed576c157f3c4368969e8f309bd`
- `staging-worker.js`: `0037795ec2a4d77102410b4103fb82a0bb360c8ca326004852ca0712bda1335b`
- `wrangler.staging.jsonc`: `bab9d6461b0500fda6a4d12b55356dae00ccae0d73e6dc9686f323385af77fd1`
- full-form regression test: `eeebca8fe483362b2fc63cdf23c51a002258b4e07f36ee88efd1d14ed4a4fd78`
- dry-run bundle: `727a0f37fa58c604c55cc902839d986c6541d016aec2e5462dc0af47701b4363`

## Remaining gates

Staging acceptance is complete, but production readiness is not established. Exactly two gates remain:

1. `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING`
2. `PRODUCTION_RECOVERABILITY=UNKNOWN`

Therefore `READY_FOR_OWNER_PRODUCTION_REVIEW=NO` and `READY_FOR_OWNER_PRODUCTION_RELEASE=NO`.

PR #54 remains Draft and unmerged. Production migration 0003, production Worker deployment, production POST, public Pilot, social publication, billing, and outreach were not performed.
