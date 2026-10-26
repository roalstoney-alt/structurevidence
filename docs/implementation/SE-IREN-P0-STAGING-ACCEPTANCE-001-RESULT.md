# SE-IREN-P0-STAGING-ACCEPTANCE-001 · Result

Date: 2026-10-27 (Asia/Shanghai)
Scope: isolated Cloudflare staging only; no production deployment or production POST.

```text
PROJECT = SE-IREN-P0-STAGING-ACCEPTANCE-001

BASE_MAIN_SHA = 56f8e345ddfc697855c8eb9492dc0b49d24c6fcc
HEAD_SHA = cfda41c4b9f66fc987488d82bb62f79704a22294
PR_NUMBER = 54
PR_DRAFT = YES

STAGING_WORKER = structevidence-commercial-staging
STAGING_D1 = structurevidence-customer-cases-staging / 65dc6680-0832-401d-8772-6a082b68673c
STAGING_URL = https://structevidence-commercial-staging.roalstoney.workers.dev

PRODUCTION_WORKER_CHANGED = NO
PRODUCTION_D1_CHANGED = NO
PRODUCTION_POST_COUNT = 0

MIGRATIONS = PASS
REAL_TURNSTILE = BLOCKED
STAGING_HTTP_E2E = BLOCKED
IDEMPOTENCY_CONCURRENCY = PASS
CONSENT_AUDIT = PASS
APPEND_ONLY = PASS
THREE_LANGUAGE_FORMS = PASS
ADMIN_ACCESS = BLOCKED
PRIVACY_AND_LOGGING = PASS

TESTS_PASSED = 54 Node tests; local D1 E2E; 9 staging rejection gates; 6 staging frontend gates; staging idempotency replay/conflict transport; drift/link checks
TESTS_FAILED = 0 new regressions; 11 known repository baseline failures; 2 staging acceptance boundaries remain blocked
NEW_REGRESSION_COUNT = 0

READY_FOR_OWNER_PRODUCTION_REVIEW = NO
PRODUCTION_DEPLOYMENT = NO
PUBLIC_PILOT_STARTED = NO
SOCIAL_POST_SENT = 0
```

## Isolated resources

- Worker version: `19f0ef29-c7c0-4cd0-b628-a68d860ec203`; `workers.dev` only, no custom route, `no-store`, `X-Robots-Tag: noindex, nofollow, noarchive`, and a visible staging banner.
- D1: `structurevidence-customer-cases-staging`, APAC, separate from production. Migrations `0001`, `0002`, and `0003` are applied. Schema SHA-256: `92776469b985558cb44427a55d4a4234fa30cb8c7b2cf965cb064741053cdf5b`.
- Turnstile: dedicated managed widget for the staging hostname and action `public-intake`. The secret is present only as a Worker secret.
- Access API app: `debb1428-4311-465d-a8dd-44cba4de0408`; policy `6219ceeb-9708-49ac-ba8c-7defd4aa62eb`.
- Access UI app: `3dc32aeb-3e9d-4636-b2f0-981804d58e03`; policy `a137e064-be11-4f20-9eaf-00dc1b43aa9c`.
- Rate-limit namespace: `842054`, distinct from production `842001`.
- Required secrets found by name only: `ADMIN_EMAILS`, `GAP_RATE_LIMIT_SALT`, and `TURNSTILE_SECRET_KEY`. No secret value was committed or retained locally.

The validated manifest reported zero isolation blockers. The final staging deployment exposed only the staging D1, staging rate limiter, staging variables, and existing secret names.

## Database and append-only checks

The staging schema contains `customers`, `requests`, `request_events`, `request_idempotency`, and `request_consent_receipts` with the expected indexes, foreign keys, unique constraints, and append-only triggers. Direct staging checks rejected UPDATE/DELETE against event and consent records.

Four synthetic logical records remain in staging:

1. schema/trigger fixture;
2. genuine browser submission `SE-REQ-BC5D71BFDBC646BF8DEC`;
3. explicit idempotency transport fixture `STAGING_TEST_FIXTURE_REQUEST_20261027`;
4. deterministic-key browser submission `SE-REQ-E56EABAB6D574DC3BC7C`.

Every record uses reserved synthetic identity data, is marked `STAGING_TEST` or `STAGING_TEST_FIXTURE`, and has exactly one customer/request relationship, one `REQUEST_SUBMITTED` event, one consent receipt, and one idempotency record. Every request is `CUSTOMER_PRIVATE`, `NOT_AUTHORIZED`, and has no human owner.

The event and consent histories are not deleted to simulate cleanup. The idempotency mapping has the designed 24-hour expiry. Any later removal or anonymization of staging customer/request rows requires a separately reviewed retention operation that preserves append-only audit meaning.

## Real HTTP evidence

Two genuine browser Turnstile challenges completed and each produced HTTP `201`. D1 readback confirmed the private defaults, consent audit, event, and idempotency record. A genuine invalid token returned `400`; missing token and all field/consent failures also failed closed before any write.

The rejection matrix passed:

- missing consent `400`;
- invalid consent version `400`;
- invalid email `400`;
- invalid request type `400`;
- unknown JSON field `400`;
- invalid Turnstile token `400`;
- oversized body `413`;
- disallowed browser Origin `403`;
- bounded burst overflow `429`.

The rate limiter returned `429` during a four-batch burst inside one ten-second window. Because the binding's distributed counter did not reject exactly at request six, this evidence establishes overflow enforcement, not a precise per-request threshold guarantee.

The staging idempotency fixture returned concurrent `200/200` replays with the same request ID and `REPLAYED`, followed by `409` for the same key with a different payload. D1 remained at one logical fixture record. The browser-created deterministic-key request was then replayed over real staging HTTP: the identical payload returned `200`, `REPLAYED`, and the same request ID; a changed payload returned `409`. A post-replay D1 read confirmed exactly one request, event, consent receipt, and idempotency record for that logical submission, while the staging request total remained four. The isolated local D1 E2E separately exercised a fresh concurrent insert and returned `201/200` with one request, event, consent, customer, and idempotency record.

## Turnstile boundary

`REAL_TURNSTILE = BLOCKED`, not failed. Real staging proved two independent valid browser challenges and one invalid token. Missing, expired, replayed, wrong-hostname, wrong-action, provider-error, and timeout fail-closed behavior is covered by deterministic Worker tests. A real-provider expired/replayed/wrong-hostname/wrong-action/timeout matrix remains incomplete, so deterministic coverage is not presented as complete real-provider acceptance.

## Frontend, privacy, and logging

English, Simplified Chinese, and Spanish entry routes returned `200`, the correct HTML language and localized Decision Boundary marker, the staging banner, no-store, noindex, and the staging environment header. `/verify/`, `/context/`, and `/decision-pack/` expose the same consent version, research/publication boundary, required Turnstile action, keyboard-addressable fields, and live status region. The shared form is English; the three localized entry routes and preserved shared-form behavior were tested without changing prices or commercial copy.

No browser console or report contains a Turnstile token or secret. Worker failure logging records only event, path, and sanitized error message. Rejected staging requests did not change D1 counts. The lifecycle distinction remains explicit:

`consent to submit ≠ authorization to research ≠ authorization to publish`.

## Access boundary and blocker

Unauthenticated `/admin/requests/` and `/api/admin/requests` requests were redirected to their distinct staging Access applications and audiences. The API authorization flow reached the configured Cloudflare identity provider, but the current in-app browser session remained on the Cloudflare login loading state and never returned an Access assertion to the staging API. No OTP, credential, or bypass was attempted.

Consequently, `ADMIN_ACCESS = BLOCKED` and the required real authorized HTTP `200` read is not claimed. Direct read-only D1 queries confirmed the records, but they do not substitute for the Access-protected admin E2E.

## Production isolation

- Production Worker `structevidence-commercial` was not deployed; its returned deployment history ends before this staging activity.
- Production D1 still reports only `0003_intake_hardening.sql` as pending, proving its migration count did not change.
- No request was POSTed to `https://structevidence.com/api/requests`.
- No production route, variable, secret, price, public evidence record, case status, social channel, payment path, or pilot state was changed.
- `PUBLIC_RECORD_DRIFT = PASS`; internal links report zero broken and zero orphan pages.

## Test summary

- Cloudflare landing Node suite: `54/54 PASS`.
- Targeted intake + staging suite: `23/23 PASS`.
- Isolated local D1 E2E: `PASS` (`201`, replay `200`, conflict `409`, fresh concurrency `201/200`, consent `400`, challenge `400`, admin read `200`).
- Staging frontend checks: `6/6 PASS`.
- Staging rejection matrix: `9/9 PASS`.
- Staging idempotency transport: concurrent replay and conflict `PASS`.
- Public record drift: `PASS`.
- Internal link audit: `PASS` (`0` broken, `0` orphan).
- Repository Python suite: `41` tests, `11` pre-existing failures, `0` new failures.
- `git diff --check`: `PASS`.

The remaining production-review gates are a real Access-authorized admin HTTP `200` read and completion of the real-provider Turnstile edge-case matrix. PR #54 must remain Draft and must not be merged or deployed to production on this report.

## Source hashes

| Artifact | SHA-256 |
|---|---|
| `wrangler.staging.jsonc` | `bab9d6461b0500fda6a4d12b55356dae00ccae0d73e6dc9686f323385af77fd1` |
| `staging-worker.js` | `0037795ec2a4d77102410b4103fb82a0bb360c8ca326004852ca0712bda1335b` |
| staging manifest validator | `900dcd2a8b105eb108425d86ebf77b44db3f0c3ed8aeae905acaa0eda1269e39` |
| staging frontend checker | `ee26f9fcf0e1b8447c44613c0d845f6ef26f16cd044fc60f5bbf02555be0e001` |
| staging rejection matrix | `fcf4f43ba65cad1936eae18c0cb2ec126187957a84f266701566abad94f6c932` |
| staging idempotency transport | `efb23e63a0392de76f781aed06a28b9cb942f8837b7303c0c7ec65f82613a4fa` |
| staging boundary tests | `9fa7ffc5b432c9c5a03f02ff8fb0de8d3d91270b15ab8e9358197cfe12c464fe` |
| migration `0003` | `fd31df9a29343319f8a5787f8e2ee5689b9668b2808cdc0c3b907b29908b0df6` |
