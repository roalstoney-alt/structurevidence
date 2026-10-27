# SE-IREN-P0-R3-LOCALIZED-STAGING-ACCEPTANCE-002
Date: 2026-10-27
Authorization: Deploy ONLY PR #54's localized intake changes at input HEAD `da0421429a98e8c3d5dec96506b80cdc98fd1f35` to isolated Staging Worker; use REAL browser to validate EN, zh-CN, es consent/Turnstile/errors/success and API 201/200/409 with D1 append-only.
Status at preparation: `CLOUDFLARE_DEPLOY=BLOCKED_NO_CONNECTED_TOOL`; `REAL_BROWSER_E2E=NOT_PERFORMED`. The GitHub-only assistant MUST NOT claim remote deployment or acceptance success.

## Frozen scope and environment manifest
Repository `roalstoney-alt/structurevidence`, existing Draft PR #54, base main `56f8e345ddfc697855c8eb9492dc0b49d24c6fcc`.
Expected source input HEAD `da0421429a98e8c3d5dec96506b80cdc98fd1f35`. If head moved, inspect diff and obtain a fresh lock; after this spec-only commit, code SHA must be checked separately.
Staging-only Wrangler config `deploy/cloudflare-landing/wrangler.staging.jsonc`:
- Worker `structevidence-commercial-staging`, `main=staging-worker.js`, `workers_dev=true`, no custom domain
- Staging D1 `structurevidence-customer-cases-staging`, id `65dc6680-0832-401d-8772-6a082b68673c`
- Staging limiter namespace `842054`, `STAGING_TEST_ONLY=true`
- Turnstile expected hostname `structevidence-commercial-staging.roalstoney.workers.dev`, action `public-intake`; existing staging Sitekey, secret managed on Worker (never print secret)
- Staging URL `https://structevidence-commercial-staging.roalstoney.workers.dev`
Forbidden production D1 `aee10591-536a-47af-8ee0-957551ba2360`, production limiter `842001`, production Worker `structevidence-commercial`, domains `structevidence.com` and `www.structevidence.com`.
Do not reuse staging synthetic identities that could be confused with real users. No secret, request payload, admin identity or token in GitHub.

## Phase 0 — No-write preflight and rollback checkpoint
1. Verify HEAD branch, staging-worker import of `worker.js` and the localized `commercial-upgrade.js`, config name/IDs, absence of routes, staging-exclusive Access UI/API audiences.
2. Record current staging Worker version, current D1 aggregate counts and existing four synthetic requests. Check migrations 0001-0003 already applied to staging; do NOT reapply migration to production.
3. Record old staging Worker version and exact Wrangler artifact hash, identify how to restore ONLY staging if deploy fails. Stage/production bindings must never cross.
4. Capture SHA-256 of localized source, final Worker bundle, EN/zh-CN/es expected copy; run existing Worker suite, focused intake tests, privacy guard and `wrangler deploy -c wrangler.staging.jsonc --dry-run`. Keep logs redacted.
5. Check that **Chinese and Spanish localized forms actually use localized consent in the forms users reach**, not just on home-page chrome. If /verify/ is a shared English route, document which localized landing/form route carries each consent; do not claim localization solely based on translated dictionary.

## Phase 1 — Authorized Staging deploy only
Run deployment only if bindings and checks match exactly. Explicitly specify staging config `wrangler.staging.jsonc`; do not rely on default `wrangler.jsonc`. Record command/version, UTC timestamp, deployment/version ID, current routes and binding manifest. If any check fails, STOP and do not deploy.
No production deploy, main merge, production POST, or billing/public pilot.

## Phase 2 — Real browser acceptance, staging only
A. EN/zh-CN/es: navigate actual localized intake entry(s); capture HTTP 200, html lang, correct consent text/policy version, challenge/fallback, validation/errors (400/409/429/503 when safely fault-injected), confirmation copy and 'submission does not authorize research or publication' in correct language. Real human language equivalence remains separate signature; no AI legal approval.
B. For each language, use independent *synthetic* identity using example.invalid, test a valid Turnstile provider challenge, consent checked, POST HTTP 201; verify success display and D1 statuses `SUBMITTED`, `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, `human_owner=null`. Count expected new synthetic records and record the delta; do NOT assert count remains 4 if new successful requests were submitted.
C. Replay identical payload and idempotency key with an independently valid fresh challenge if verification required -> HTTP 200 + same request ID and replay semantics. Same key with changed payload -> HTTP 409. Protect against Turnstile reuse; never store token. If browser automatic key reset after successful POST prevents manual replay, use a controlled staging test-client fixture and distinguish it from browser path.
D. Confirm exactly one logical request, event, consent, active idempotency mapping per logical submission, 4 append-only triggers remain, UPDATE/DELETE rejected on **synthetic** rows; 0 unexpected mutations from rejected cases. Record sanitized counts and per-record comparison hashes, not PII.
E. CORS: allowlisted staging Origin OPTIONS 204 with `content-type, idempotency-key`, disallowed Origin OPTIONS 204 without approval; same-origin form preflight NOT_APPLICABLE, don't invent cross-origin browser preflight PASS.
F. Access unauthorized redirect, authenticated admin GET 200 for staging synthetic record only if authorized, no credential extraction.
G. Verify pages unchanged on actual production through read-only checks only if needed; no production POST or D1 read of private rows.

## Phase 3 — Result to PR #54
Write two append-only sanitized result artifacts:
`docs/implementation/SE-IREN-P0-R3-LOCALIZED-STAGING-ACCEPTANCE-002-RESULT.md`
`docs/implementation/SE-IREN-P0-R3-LOCALIZED-STAGING-ACCEPTANCE-002-RESULT.json`
Include LOCKED_INPUT_HEAD, FINAL_HEAD_SHA, STAGING_WORKER_VERSION_BEFORE/AFTER, staging D1 totals before/after, three-language actual routes, browser observations, server results 201/200/409, Trigger/Consent/Idempotency results, security/status gate, timestamp and SHA-256, test suite counts. Never claim real browser/real Turnstile if tests were injected. Distinguish `STAGING_DEPLOYED`, `STAGING_REAL_BROWSER_E2E`, `HUMAN_PRIVACY_LEGAL_SIGNOFF`.
Keep `HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING` until a separate real authorized human privately signs. Keep `PRODUCTION_RECOVERABILITY=UNKNOWN`; `READY_FOR_OWNER_PRODUCTION_RELEASE=NO`.
Must remain PR Draft/unmerged, production migration 0003 pending, production Worker unmodified, production POST 0, no public pilot, social publication, charging, outreach.
Stop on any ambiguous resource ID, production binding, security config gap or accidental data exposure. Do not disguise a failed deployment as PASS.

## Current checkpoint
GITHUB_HEAD_LOCK_VERIFIED=YES
STAGING_DEPLOYMENT=NOT_PERFORMED_BY_THIS_ASSISTANT
REAL_BROWSER_ACCEPTANCE=NOT_PERFORMED_BY_THIS_ASSISTANT
HUMAN_PRIVACY_LEGAL_SIGNOFF=PENDING
PRODUCTION_RECOVERABILITY=UNKNOWN
PRODUCTION_D1_MIGRATION_0003=NOT_AUTHORIZED
PRODUCTION_WORKER_DEPLOY=NOT_AUTHORIZED
PRODUCTION_POST=0
PR54_MERGED=NO
