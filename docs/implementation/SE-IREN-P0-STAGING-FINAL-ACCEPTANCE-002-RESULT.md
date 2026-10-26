# SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002 · Result

Date: 2026-10-27 (Asia/Shanghai)

This report appends to `SE-IREN-P0-STAGING-ACCEPTANCE-001`; it does not overwrite the earlier observations. The validation target was locked before execution.

```text
PROJECT = SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002
LOCKED_HEAD_SHA = fc0615d0e6e2799909d72baaa743dd1bfb3f20cd
PR_NUMBER = 54
PR_DRAFT = YES

ACCESS_AUTHORIZED_ADMIN_READ = PASS
REAL_PROVIDER_OBSERVED = PASS_VALID_AND_INVALID
DETERMINISTIC_FAULT_INJECTION = PASS
LAYERED_TURNSTILE_ACCEPTANCE = PASS
CONSENT_AUDIT = PASS
IDEMPOTENCY = PASS
APPEND_ONLY = PASS
PRIVACY = PASS
PRODUCTION_ISOLATION = PASS

PRODUCTION_WORKER_CHANGED = NO
PRODUCTION_D1_CHANGED = NO
PRODUCTION_POST_COUNT = 0
MERGE_AUTHORIZED = NO
PRODUCTION_DEPLOYMENT = NO
PUBLIC_PILOT_STARTED = NO

READY_FOR_OWNER_PRODUCTION_REVIEW = YES
```

## 1. Cloudflare Access authorized read

A real Cloudflare Access identity flow was used for the staging API application. The browser followed the Access application to the configured Cloudflare identity provider and returned to:

`https://structevidence-commercial-staging.roalstoney.workers.dev/api/admin/requests`

The protected endpoint returned HTTP 200 JSON with four synthetic staging requests. It included `SE-REQ-E56EABAB6D574DC3BC7C` with:

- `SUBMITTED`
- `CUSTOMER_PRIVATE`
- `NOT_AUTHORIZED`
- no human owner

An independent read-only staging D1 query returned the same values. No authentication bypass was used. No Access JWT, OTP, cookie, administrator email, or other identity value was extracted into a report, terminal command, repository file, or GitHub.

## 2. Layered Turnstile acceptance

The evidence layers are intentionally separated.

### REAL_PROVIDER_OBSERVED

- Two independent genuine staging browser challenges produced HTTP 201.
- A fresh invalid token sent to the isolated staging API produced HTTP 400 with `Human verification failed` and no D1 write.

### DETERMINISTIC_FAULT_INJECTION

Automated tests exercised the production Worker verification path with controlled verifier or Siteverify responses:

- missing token: HTTP 400, no write;
- expired token: HTTP 400, no write;
- replayed single-use token: first request 201, second request 400, one logical write;
- wrong hostname: HTTP 400, no write;
- wrong action: HTTP 400, no write;
- provider transport error: HTTP 503, no write;
- provider timeout/abort: HTTP 503, no write.

These injected cases prove deterministic fail-closed behavior. They are not described as real Cloudflare provider incidents.

## 3. Staging D1 and privacy recheck

At the final check, the isolated staging D1 contained four synthetic customers, requests, events, consent receipts, and idempotency mappings. The target request had exactly one request, one `REQUEST_SUBMITTED` event, one accepted `SE-CUSTOMER-PRIVACY-v1` receipt, and one active idempotency record.

Four append-only triggers were present for UPDATE and DELETE protection on `request_events` and `request_consent_receipts`. No-op UPDATE attempts against the target event and consent receipt were both rejected with `SQLITE_CONSTRAINT_TRIGGER`; values and row counts remained unchanged.

Consent to submit remains distinct from authorization to research or publish. Every staging record remains synthetic, private, unauthorized, and unassigned.

## 4. Production isolation

Read-only inventory checks confirmed:

- production Worker deployment history still ends at `2026-10-08T05:23:20.397Z`;
- production D1 still lists only `0003_intake_hardening.sql` as pending;
- no production Worker deployment occurred;
- no production D1 migration or mutation occurred;
- no POST was sent to the production intake endpoint.

No price, public evidence record, case status, social channel, charging path, outreach path, or Pilot state changed.

## 5. Regression results

- Cloudflare Worker suite: 56/56 PASS.
- Focused Turnstile suite: 4/4 PASS.
- Staging rejection matrix: 9/9 PASS.
- Staging frontend checks: 6/6 PASS.
- Staging idempotency replay/conflict transport: PASS.
- Public record drift: PASS.
- Internal links: 0 broken / 0 orphan.
- Repository Python suite: 41 tests / 11 pre-existing failures / 0 new failures.
- `git diff --check`: PASS.
- `NEW_REGRESSION_COUNT = 0`.

## 6. Risk decision boundary

The formal matrix is `SE-IREN-P0-STAGING-FINAL-ACCEPTANCE-002-RISK-ACCEPTANCE-MATRIX.md`. Technical evidence closes the two previous staging blockers for owner production review:

- real Access-authorized admin read: PASS;
- layered Turnstile acceptance: PASS.

Risk acceptance authority remains with the owner. `READY_FOR_OWNER_PRODUCTION_REVIEW = YES` does not authorize merge or production deployment.
